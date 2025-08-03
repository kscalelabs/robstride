import argparse
import sys
import tarfile
import asyncio
import json
import time
from robstride_driver import PyRobstrideDriver, PyActuatorCommand, PyRobstrideActuatorType
from pathlib import Path
from typing import Sequence

DEFAULT_KINFERLOG:str = "kinfer_log.ndjson"
JSON_TORQUE_IDENTIFIER:str = "joint_torques"
JSON_TIME_IDENTIFIER:str = "t_us"
POSIX_SCALE:float = 1e6 # microseconds to seconds

name2motorid = {
        "dof_left_hip_pitch_04":31,
        "dof_left_shoulder_pitch_03":11,
        "dof_right_hip_pitch_04":41,
        "dof_right_shoulder_pitch_03":21,
        "dof_left_hip_roll_03":32,
        "dof_left_shoulder_roll_03":12,
        "dof_right_hip_roll_03":42,
        "dof_right_shoulder_roll_03":22,
        "dof_left_hip_yaw_03":33,
        "dof_left_shoulder_yaw_02":13,
        "dof_right_hip_yaw_03":43,
        "dof_right_shoulder_yaw_02":23,
        "dof_left_knee_04":34,
        "dof_left_elbow_02":14,
        "dof_right_knee_04":44,
        "dof_right_elbow_02":24,
        "dof_left_ankle_02":35,
        "dof_left_wrist_00":15,
        "dof_right_ankle_02":45,
        "dof_right_wrist_00":25
    }

def load_joint_names(kinfer_file: Path) -> Sequence[str]:
    """Return the ordered list of joint names for robot.
    """
    with tarfile.open(kinfer_file, 'r:gz') as tar:
        metadata_file = tar.extractfile('metadata.json')
        metadata_json = metadata_file.read().decode('utf-8')
        metadata = json.loads(metadata_json)
    return metadata['joint_names']

def parse_policy(ndjson: str, kinfer_file: Path, scale: float = 1.0, ids: list[int] = None) -> dict:
    with open(ndjson, 'r') as f:
        data = []
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {e}")

    joint_names = load_joint_names(kinfer_file)

    # Build kinfer2motorid as a list where index is kinfer index, value is motor id
    kinfer2motorid = [name2motorid[name] for name in joint_names]

    # If ids is provided, build a set for fast lookup and a mapping from motor id to kinfer index
    if ids is not None:
        ids_set = set(ids)
        # Map motor id to kinfer index
        motorid_to_kinferidx = {motor_id: idx for idx, motor_id in enumerate(kinfer2motorid) if motor_id in ids_set}
        # Only keep kinfer indices for requested ids, in the order of ids
        selected_kinfer_indices = [motorid_to_kinferidx[motor_id] for motor_id in ids if motor_id in motorid_to_kinferidx]
        selected_motor_ids = [kinfer2motorid[idx] for idx in selected_kinfer_indices]
    else:
        selected_kinfer_indices = list(range(len(kinfer2motorid)))
        selected_motor_ids = kinfer2motorid

    torque_data = []  # List of dicts: [{motor_id: torque, ...}, ...]
    time_abs = []  # seconds
    time_rel = []  # seconds

    for row_idx, row in enumerate(data):
        t_us = row[JSON_TIME_IDENTIFIER]
        t_sec = t_us / POSIX_SCALE
        time_abs.append(t_sec)
        time_rel.append(t_sec - time_abs[0])

        joint_torques = row[JSON_TORQUE_IDENTIFIER]

        # Only include the requested motor ids (by kinfer index)
        torque_row = {}
        for idx, motor_id in zip(selected_kinfer_indices, selected_motor_ids):
            step_torque_Nm = joint_torques[idx]
            torque_row[motor_id] = step_torque_Nm * scale
        torque_data.append(torque_row)

    # Confirm all rows have the same key sets
    if torque_data:
        first_keys = set(torque_data[0].keys())
        for row in torque_data:
            if set(row.keys()) != first_keys:
                print(f"Command id {row} has different keys than the first row, exiting lazily")
                exit()

    return {
        'torque_data': torque_data,
        'time_abs': time_abs,
        'time_rel': time_rel,
    }


# Replay the policy as time step commands to selected actuators. Torque Control
async def replay(ndjson:str, kinfer:str, scale:float=1.0, ids:list[int] or None = None, log:bool = True):

    policy = parse_policy(ndjson, kinfer, scale, ids)
    #with open("policy.json", "w") as f:
    #    json.dump(policy, f, indent=4)
    
    torque_data = policy['torque_data']
    time_rel = policy['time_rel']
    print(time_rel)

    canint:list[str] = ["can0"]
    drivers_actuators = {}  # {driver: [actuator_ids]}
    actuators = torque_data[0].keys()

    # Register the actuators with drivers per CAN interface -> drivers_actuators
    for interface_name in canint:
        driver = PyRobstrideDriver(interface_name)
        driver.connect(interface_name)
        
        try: 
            return_ids = driver.scan_actuators(start_id=min(actuators), end_id=max(actuators))
            found_actuators = []
            
            for actuator_id in return_ids:
                if actuator_id in actuators:
                    found_actuators.append(actuator_id)
                    print(f"Actuator {actuator_id} found on {interface_name}")
                else:
                    print(f"Also found {actuator_id} on {interface_name} but not in actuators list")
            
            if found_actuators:
                drivers_actuators[driver] = found_actuators
                
        except Exception as e:
            print(f"Error polling {interface_name} with driver {driver}: {e}")
            exit()

    # Split torque_data by driver groups - timeseries with subdictionaries
    data_by_driver = []  # [{driver: {actuator_id: position}}, ...] - timeseries
    for time_idx in range(len(time_rel)):
        time_step_data = {}

        for driver, actuator_ids in drivers_actuators.items():
            driver_positions = {}

            for actuator_id in actuator_ids:
                if actuator_id in torque_data[time_idx]:
                    driver_positions[actuator_id] = torque_data[time_idx][actuator_id]

            time_step_data[driver] = driver_positions
        data_by_driver.append(time_step_data) 

    # Check that all required actuators are driven
    all_found_actuators = []
    for driver, actuator_ids in drivers_actuators.items():
        all_found_actuators.extend(actuator_ids)
    
    missing_actuators = [id for id in actuators if id not in all_found_actuators]
    if missing_actuators:
        print(f"Actuators not found on any interface: {missing_actuators}")
        exit()
    
    # Initialize timer for current onboard time
    start_time = time.time()
    skipFirst = True

    if log:
        # Pre-loading 
        iqf_hex = 0x301E # ref parameters.rs
        iqf_amps = []
        for time_idx in range(len(time_rel)):
            iqf_amps.append({})
            for driver in data_by_driver[time_idx].keys(): # skip this in formation
                for actuator_id in data_by_driver[time_idx][driver]:
                    iqf_amps[time_idx][actuator_id] = 1000
    # MAIN CONTROL LOOPING -- Send time series commands to all actuators by driver
    for time_idx in range(len(time_rel)):
        # first time flag
        if not skipFirst:
            sleep_time = time_rel[time_idx] + start_time - time.time()
            await asyncio.sleep(sleep_time)
            print(f"Sleeping for {sleep_time}s")
        skipFirst = False
        time_step_data = data_by_driver[time_idx]
        # TODO: batch commands
        #time_step_commands = []
        for driver in time_step_data.keys():
            for actuator_id in time_step_data[driver].keys():
                #TODO: torque control
                command = PyActuatorCommand(
                    position=0.0,
                    velocity=0.0,   
                    torque=time_step_data[driver][actuator_id],
                    kp = 0.0, #kp_leg[actuator_id],
                    kd = 0.0 #kd_leg[actuator_id]
                )
                #print(str(command))                 #print(driver)                  #print(actuator_id)
                driver.send_command(actuator_id, command)
                #if log:
                #    iqf_amps[time_idx][actuator_id] = driver.read_raw_parameter(int(actuator_id), param_index = iqf_hex)
                #time_step_commands.append((actuator_id, command))
            #driver.send_command_batch(time_step_commands)
    for driver in data_by_driver[0].keys():
        for actuator_id in data_by_driver[0][driver].keys():
            command = PyActuatorCommand(
                position=0.0,
                velocity=0.0,   
                torque=0.0,
                kp = 0.0, 
                kd = 0.0 
            )
            driver.send_command(actuator_id, command)

    if log:
        logs = [iqf_amps]
        with open("./log_replay.json", "w") as f:
            json.dump(logs, f, indent=4)




def run_replay(ndjson:str, kinfer:str, scale:float, ids:list[int] or None, log:bool = True):
    asyncio.run(replay(ndjson=ndjson, kinfer=kinfer, scale=scale, ids=ids, log=log))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay kinfer_log policy outputs to actuators")
    parser.add_argument('--kinfer', type=str, required=True, help='Path to KINFER file')
    parser.add_argument('--ndjson', type=str, required=False, help='Path to NDJSON file', default = DEFAULT_KINFERLOG)
    parser.add_argument('--scale', type=float, required=True, help='Scale factor for replay')
    parser.add_argument('--ids', type=str, required=False, help='Motor IDs to replay, comma delimited')
    parser.add_argument('--log', type=bool, required=False, help='Logging current', default= True)
    args = parser.parse_args()

    if args.ids is not None:
        try:
            ids = [int(x) for x in args.ids.split(',')]
            valid_motor_ids = set(name2motorid.values())
            invalid_ids = [x for x in ids if x not in valid_motor_ids]
            if invalid_ids:
                print(f"Error: The following ids are not valid motor ids: {invalid_ids}")
                exit(1)
        except Exception as e:
            print(f"Error parsing --ids: {e}")
            exit(1)
    else:
        ids = None

    run_replay(ndjson=args.ndjson, scale=args.scale, kinfer=args.kinfer, ids=ids, log=args.log)

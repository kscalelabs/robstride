import argparse
import sys
import robstride_driver.cli
import asyncio
import json
import time
from robstride_driver import PyRobstrideDriver, PyActuatorCommand, PyRobstrideActuatorType

JSON_CURRENT_IDENTIFIER:str = "joint_pos"#"joint_amps"
JSON_TIME_IDENTIFIER:str = "t_us"
POSIX_SCALE:float = 1e6 # microseconds to seconds
#TODO: remove
INPUT_POS =  [{41: 0.3, 42: 0.7, 43: 0.3, 44: 0.7, 45: 0.3},{41: 0.7, 42: 0.3, 34: 0.7, 44: 0.3, 45: 0.7},{41: 0.3, 42: 0.7, 34: 0.3, 44: 0.7, 45: 0.3}]
#[{31: 0.3, 32: 0.7, 33: 0.3, 34: 0.7, 35: 0.3},{31: 0.7, 32: 0.3, 33: 0.7, 34: 0.3, 35: 0.7}]
#kp_leg = {31: 150.0, 32: 200.0, 33: 100.0, 34:150.0, 35:40.0, 41: 150.0, 42: 200.0, 43: 100.0, 44:150.0, 45:40.0} # taken 2025m07d31 from firmware -> robot_description
#kd_leg = {31: 24.722, 32: 26.387, 33: 3.419, 34: 8.654, 35: 0.99,41: 24.722, 42: 26.387, 43: 3.419, 44: 8.654, 45: 0.99} # taken 2025m07d31 from firmware -> robot_description

def parse_policy(ndjson:str, scale:float=1.0, ids:list[str] = None) -> list[dict]:
    with open(ndjson, 'r') as f:
        data = []
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {e}")
    
    with open("params/params.json", "r") as fparam:
        params = json.load(fparam)

        kinfer2motorid = params["kinfer2motorid"]
        motorid2type = params["motorid2type"]
        motortype2ktNmA = params["motortype2ktNmA"]

        try:
            kinfer2motorid = dict(zip(
                [int(k) for k in kinfer2motorid.keys()],
                [int(v) for v in kinfer2motorid.values()]
            ))
        except Exception as e:
            print(f"Error parsing kinfer2motorid.json: {e}")
            exit()
        
        try:
            motorid2kt = dict(zip(
                [int(k) for k in motorid2type.keys()],
                [motortype2ktNmA[motorid2type[k]] for k in motorid2type.keys()]  # Fixed: motorid2type[k]
            ))
        except Exception as e:
            print(f"Error parsing params.json: {e}")
            exit()

    # Parse the data into a dictionary of motor ids to torque values
    torque_data = [{}] # [motor id: [torq values, Nm]]
    time_abs = [] # seconds
    time_rel = [] # seconds

    for row in data:
        torque_data.append({})
        t_us = row[JSON_TIME_IDENTIFIER]
        t_sec = t_us / POSIX_SCALE
        time_abs.append(t_sec)
        time_rel.append(t_sec - time_abs[0])

        joint_amps = row[JSON_CURRENT_IDENTIFIER]

        #motors_ids = [kinfer_idx for kinfer_idx in range(len(joint_amps)) if kinfer_

        for kinfer_idx in range(len(joint_amps)):
            current_amps = joint_amps[kinfer_idx]
            motor_id = kinfer2motorid[kinfer_idx]
            if motor_id not in torque_data[row]:
                torque_data[row][motor_id] = []
            # convert amps to torque Nm 
            torque_data[row][motor_id].append(current_amps * scale * motorid2kt[motor_id])


        #for motor_id in kinfer2motorid.values():
        #    if motor_id not in torque_data[row]:
        #        torque_data[row][motor_id] = []
        #    torque_data[row][motor_id].append(row[JSON_CURRENT_IDENTIFIER][motor_id])
    
    # Confirm all rows have the same key sets
    for row in torque_data:
        if row.keys() != torque_data[0].keys():
            print(f"Command id {row} has different keys than the first row, exiting lazily")
            exit()

    return {
        'torque_data': torque_data,
        'time_abs': time_abs,
        'time_rel': time_rel,
    } 
   



async def replay(ndjson:str, scale:float=1.0):

    # TODO: return to policy parsing
    #policy = parse_policy(ndjson, scale)
    #pos_data = policy['torque_data']
    pos_data = INPUT_POS
    #torque_data = policy['torque_data']
    time_rel = [0.0, 1.0, 2.0] 
    #time_rel = policy['time_rel']

    canint:list[str] = ["can0"]
    drivers_actuators = {}  # {driver: [actuator_ids]}
    actuators = pos_data[0].keys()

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

    # Split pos_data by driver groups - timeseries with subdictionaries
    data_by_driver = []  # [{driver: {actuator_id: position}}, ...] - timeseries
    for time_idx in range(len(time_rel)):
        time_step_data = {}

        for driver, actuator_ids in drivers_actuators.items():
            driver_positions = {}

            for actuator_id in actuator_ids:
                if actuator_id in pos_data[time_idx]:
                    driver_positions[actuator_id] = pos_data[time_idx][actuator_id]

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
                    position=time_step_data[driver][actuator_id],
                    velocity=0.0,   
                    torque=0.0,
                    kp = 50.0, #kp_leg[actuator_id],
                    kd =2.0 #kd_leg[actuator_id]
                )
                print(str(command))
                print(driver)
                print(actuator_id)
                driver.send_command(actuator_id, command)
                #time_step_commands.append((actuator_id, command))
            #driver.send_command_batch(time_step_commands)

def run_replay(ndjson:str, scale:float):
    asyncio.run(replay(ndjson=ndjson, scale=scale))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay kinfer_log policy outputs to actuators")
    parser.add_argument('--ndjson', type=str, required=False, help='Path to NDJSON file')
    parser.add_argument('--scale', type=float, required=False, help='Scale factor for replay')
    args = parser.parse_args()

    run_replay(ndjson=args.ndjson, scale=args.scale)

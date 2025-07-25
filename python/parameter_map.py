#!/usr/bin/env python3
"""
Robstride Parameter Maps

Parameter definitions for different Robstride servo drive types.
Automatically detects servo type from firmware version:
- 0.0.x.x → RS00: 14Nm actuator (max current: 16A, max speed: 33 rad/s)
- 0.2.x.x → RS02: 17Nm actuator (max current: 23A, max speed: 44 rad/s) 
- 0.3.x.x → RS03: 60Nm actuator (max current: 43A, max speed: 20 rad/s)
- 0.4.x.x → RS04: 120Nm actuator (max current: 90A, max speed: 15 rad/s)

This module uses a common parameter map with type-specific overrides and extensions
to reduce redundancy while preserving unique characteristics of each servo type.
"""

import re
from typing import Dict, Tuple, Optional, List, Set

def detect_servo_type_from_version(version_string: str) -> str:
    """
    Detect servo type from firmware version string.
    
    Args:
        version_string: Firmware version (e.g., "0.2.3.9")
        
    Returns:
        Servo type string (RS00, RS02, RS03, RS04)
        
    Raises:
        ValueError: If version format is not recognized
    """
    if not version_string:
        raise ValueError("Empty version string")
    
    # Parse version pattern: major.minor.patch.build
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$', version_string.strip())
    if not match:
        raise ValueError(f"Invalid version format: {version_string}")
    
    major, minor = int(match.group(1)), int(match.group(2))
    
    # Map version to servo type
    version_map = {
        (0, 0): "RS00",
        (0, 2): "RS02", 
        (0, 3): "RS03",
        (0, 4): "RS04"
    }
    
    servo_type = version_map.get((major, minor))
    if not servo_type:
        raise ValueError(f"Unknown servo type for version {version_string} (major={major}, minor={minor})")
    
    return servo_type

# Common Parameter Map - Parameters identical across all servo types
# Format: parameter_index: (name, data_type, access_mode, min_value, max_value, description)
COMMON_PARAM_MAP = {
    # Device identification (identical across all types)
    #0x0000: ("Name",                "String", "RW", None, None, "Device name"),
    #0x0001: ("BarCode",             "String", "RW", None, None, "Device barcode"),
    
    # Boot / firmware info (identical across all types)
    0x1000: ("BootCodeVersion",     "String", "R", None, None, "Boot code version"),
    0x1001: ("BootBuildDate",       "String", "R", None, None, "Boot build date"),
    0x1002: ("BootBuildTime",       "String", "R", None, None, "Boot build time"),
    0x1003: ("AppCodeVersion",      "String", "R", None, None, "Application code version"),
    0x1004: ("AppGitVersion",       "String", "R", None, None, "Application git version"),
    0x1005: ("AppBuildDate",        "String", "R", None, None, "Application build date"),
    0x1006: ("AppBuildTime",        "String", "R", None, None, "Application build time"),
    0x1007: ("AppCodeName",         "String", "R", None, None, "Application code name"),
    
    # Common configuration parameters
    0x2004: ("echoFreHz",           "uint32", "RW", 1, 10000, "Echo frequency (Hz)"),
    0x2008: ("I_FW_MAX",            "float",  "RW", 0, 33, "Field-weakening current max"),
    0x2009: ("motor_baud",          "uint8",  "RW", 1, 4, "Motor baud rate configuration"),
    0x200B: ("CAN_MASTER",          "uint8",  "RW", 0, 300, "Master CAN ID"),
    0x200D: ("status2",             "int16",  "RW", 0, 1800, "Status parameter 2"),
    0x200E: ("status3",             "uint32", "RW", 1000, 1000000, "Status parameter 3"),
    0x200F: ("status1",             "float",  "RW", 1, 64, "Status parameter 1"),
    0x2010: ("status6",             "uint8",  "RW", 0, 1, "Status parameter 6"),
    0x2011: ("cur_filt_gain",       "float",  "RW", 0, 1, "Current filter gain"),
    0x2012: ("cur_kp",              "float",  "RW", 0, 200, "Current Kp gain"),
    0x2013: ("cur_ki",              "float",  "RW", 0, 200, "Current Ki gain"),
    0x2014: ("spd_kp",              "float",  "RW", 0, 200, "Speed Kp gain"),
    0x2015: ("spd_ki",              "float",  "RW", 0, 200, "Speed Ki gain"),
    0x2016: ("loc_kp",              "float",  "RW", 0, 200, "Position Kp gain"),
    0x2017: ("spd_filt_gain",       "float",  "RW", 0, 1, "Speed filter gain"),
    0x2018: ("limit_spd",           "float",  "RW", 0, 200, "Speed limit"),
    0x2019: ("limit_cur",           "float",  "RW", 0, 27, "Current limit"),
    
    # Timing diagnostics (identical across all types)
    0x3000: ("timeUse0",            "uint16", "R", None, None, "Time usage 0"),
    0x3001: ("timeUse1",            "uint16", "R", None, None, "Time usage 1"),
    0x3002: ("timeUse2",            "uint16", "R", None, None, "Time usage 2"),
    0x3003: ("timeUse3",            "uint16", "R", None, None, "Time usage 3"),
    
    # Common telemetry & sensor values
    0x3005: ("mcuTemp",             "int16",  "R", None, None, "MCU temperature"),
    0x3006: ("motorTemp",           "int16",  "R", None, None, "Motor temperature"),
    0x3008: ("adc1Offset",          "int32",  "R", None, None, "ADC1 offset"),
    0x3009: ("adc2Offset",          "int32",  "R", None, None, "ADC2 offset"),
    0x300A: ("adc1Raw",             "uint16", "R", None, None, "ADC1 raw value"),
    0x300B: ("adc2Raw",             "uint16", "R", None, None, "ADC2 raw value"),
    0x300C: ("VBUS",                "float",  "R", None, None, "Bus voltage (V)"),
    0x300D: ("cmdId",               "float",  "R", None, None, "Command Id"),
    0x300E: ("cmdIq",               "float",  "R", None, None, "Command Iq"),
    0x300F: ("cmdlocref",           "float",  "R", None, None, "Command position reference"),
    0x3010: ("cmdspdref",           "float",  "R", None, None, "Command speed reference"),
    0x3011: ("cmdTorque",           "float",  "R", None, None, "Command torque"),
    0x3012: ("cmdPos",              "float",  "R", None, None, "Command position"),
    0x3013: ("cmdVel",              "float",  "R", None, None, "Command velocity"),
    0x3014: ("rotation",            "int32",  "R", None, None, "Rotation count"),
    0x3015: ("modPos",              "float",  "R", None, None, "Modulo position"),
    0x3016: ("mechPos",             "float",  "R", None, None, "Mechanical position"),
    0x3017: ("mechVel",             "float",  "R", None, None, "Mechanical velocity"),
    0x3018: ("elecPos",             "float",  "R", None, None, "Electrical position"),
    0x3019: ("ia",                  "float",  "R", None, None, "Phase A current"),
    0x301A: ("ib",                  "float",  "R", None, None, "Phase B current"),
    0x301B: ("ic",                  "float",  "R", None, None, "Phase C current"),
    0x301C: ("timeout",             "int32",  "R", None, None, "Timeout counter"),
    0x301D: ("phaseOrder",          "uint8",  "R", None, None, "Phase order"),
    0x301E: ("iqf",                 "float",  "R", None, None, "Iq filter value"),
    0x301F: ("boardTemp",           "int16",  "R", None, None, "Board temperature"),
    0x3020: ("iq",                  "float",  "R", None, None, "Current Iq"),
    0x3021: ("id",                  "float",  "R", None, None, "Current Id"),
    0x3022: ("faultSta",            "uint32", "R", None, None, "Fault status"),
    0x3023: ("warnSta",             "uint32", "R", None, None, "Warning status"),
    0x3024: ("drv_fault",           "uint16", "R", None, None, "Driver fault"),
    0x3025: ("drv_temp",            "uint16", "R", None, None, "Driver temperature"),
    0x3026: ("Uq",                  "float",  "R", None, None, "Voltage Uq"),
    0x3039: ("ElecOffset",          "float",  "R", None, None, "Electrical offset"),
    0x303A: ("mcOverTemp",          "int16",  "R", None, None, "MCU over temperature"),
    0x303B: ("Kt_Nm/Amp",           "float",  "R", None, None, "Kt Nm/Amp"),
    0x303C: ("Tqcali_Type",         "uint8",  "R", None, None, "Torque calibration type"),
    0x303D: ("theta_mech_1",        "float",  "R", None, None, "Theta mechanical 1"),
    0x303E: ("adcOffset_1",         "int32",  "R", None, None, "ADC offset 1"),
    0x303F: ("adcOffset_2",         "int32",  "R", None, None, "ADC offset 2"),
}

# Type-specific parameter overrides - Same parameter index but different properties
TYPE_SPECIFIC_OVERRIDES = {
    "RS00": {
        # Echo parameters with different max values
        0x2000: ("echoPara1",           "uint16", "D", 5, 110, "Echo parameter 1"),
        0x2001: ("echoPara2",           "uint16", "D", 5, 110, "Echo parameter 2"),
        0x2002: ("echoPara3",           "uint16", "D", 5, 110, "Echo parameter 3"),
        0x2003: ("echoPara4",           "uint16", "D", 5, 110, "Echo parameter 4"),
        # Mechanical offset with smaller range
        0x2005: ("MechOffset",          "float",  "S", -7, 7, "Mechanical encoder offset"),
        # Different parameter layout
        0x2006: ("MechPos_init",        "float",  "RW", -50, 50, "Initial mechanical position"),
        0x2007: ("limit_torque",        "float",  "RW", 0, 14, "Maximum torque limit (Nm)"),
        0x200A: ("CAN_ID",              "uint8",  "RW", 0, 127, "Node CAN ID"),
        0x200C: ("CAN_TIMEOUT",         "uint32", "RW", -2000, 2000000, "CAN timeout"),
        # Different telemetry parameters
        0x3004: ("encoderRaw",          "int16",  "R", None, None, "Raw encoder value"),
        0x3007: ("vBus(mv)",            "uint16", "R", None, None, "Bus voltage (mV)"),
        0x3027: ("Ud",                  "float",  "R", None, None, "Voltage Ud"),
    },
    
    "RS02": {
        # Echo parameters with different max values
        0x2000: ("echoPara1",           "uint16", "D", 5, 107, "Echo parameter 1"),
        0x2001: ("echoPara2",           "uint16", "D", 5, 107, "Echo parameter 2"),
        0x2002: ("echoPara3",           "uint16", "D", 5, 107, "Echo parameter 3"),
        0x2003: ("echoPara4",           "uint16", "D", 5, 107, "Echo parameter 4"),
        # Mechanical offset with medium range
        0x2005: ("MechOffset",          "float",  "S", -10, 10, "Mechanical encoder offset"),
        # Different parameter layout
        0x2006: ("status4",             "float",  "RW", -10, 10, "Status parameter 4"),
        0x2007: ("limit_torque",        "float",  "RW", 0, 30, "Maximum torque limit (Nm)"),
        0x200A: ("CAN_ID",              "uint8",  "S", 0, 127, "Node CAN ID"),
        0x200C: ("CAN_TIMEOUT",         "uint32", "RW", -2000000, 2000000, "CAN timeout"),
        # Different telemetry parameters
        0x3004: ("encoderRaw",          "int16",  "R", None, None, "Raw encoder value"),
        0x3007: ("vBus(mv)",            "uint16", "R", None, None, "Bus voltage (mV)"),
        0x3027: ("Ud",                  "float",  "R", None, None, "Voltage Ud"),
    },
    
    "RS03": {
        # Echo parameters with different max values
        0x2000: ("echoPara1",           "uint16", "D", 5, 106, "Echo parameter 1"),
        0x2001: ("echoPara2",           "uint16", "D", 5, 106, "Echo parameter 2"),
        0x2002: ("echoPara3",           "uint16", "D", 5, 106, "Echo parameter 3"),
        0x2003: ("echoPara4",           "uint16", "D", 5, 106, "Echo parameter 4"),
        # Mechanical offset with large range
        0x2005: ("MechOffset",          "float",  "RW", -50, 50, "Mechanical encoder offset"),
        0x2006: ("chasu_offset",        "float",  "RW", -50, 50, "Chassis offset"),
        0x2007: ("status1",             "float",  "S", -10, 10, "Status parameter 1"),
        0x2009: ("CAN_ID",              "uint8",  "RW", 0, 127, "Node CAN ID"),
        0x200A: ("CAN_MASTER",          "uint8",  "RW", 0, 300, "Master CAN ID"),
        0x200B: ("CAN_TIMEOUT",         "uint32", "RW", -100000, 100000, "CAN timeout"),
        # Different parameter ranges
        0x2019: ("limit_cur",           "float",  "RW", 0, 150, "Current limit"),
        # Different telemetry parameters
        0x3004: ("encoderRaw",          "uint16", "R", None, None, "Raw encoder value"),
        0x3007: ("encoder2raw",         "uint16", "R", None, None, "Raw encoder 2 value"),
        0x3027: ("as_angle",            "float",  "R", None, None, "AS angle"),
    },
    
    "RS04": {
        # Echo parameters with different max values
        0x2000: ("echoPara1",           "uint16", "D", 5, 106, "Echo parameter 1"),
        0x2001: ("echoPara2",           "uint16", "D", 5, 106, "Echo parameter 2"),
        0x2002: ("echoPara3",           "uint16", "D", 5, 106, "Echo parameter 3"),
        0x2003: ("echoPara4",           "uint16", "D", 5, 106, "Echo parameter 4"),
        # Mechanical offset with large range
        0x2005: ("MechOffset",          "float",  "RW", -50, 50, "Mechanical encoder offset"),
        0x2006: ("chasu_offset",        "float",  "RW", -50, 50, "Chassis offset"),
        0x2007: ("status1",             "float",  "S", -10, 10, "Status parameter 1"),
        0x2009: ("CAN_ID",              "uint8",  "RW", 0, 127, "Node CAN ID"),
        0x200A: ("CAN_MASTER",          "uint8",  "RW", 0, 300, "Master CAN ID"),
        0x200B: ("CAN_TIMEOUT",         "uint32", "RW", -10000, 100000, "CAN timeout"),
        # Different parameter ranges
        0x2019: ("limit_cur",           "float",  "RW", 0, 150, "Current limit"),
        # Different telemetry parameters
        0x3004: ("encoderRaw",          "uint16", "R", None, None, "Raw encoder value"),
        0x3007: ("encoder2raw",         "uint16", "R", None, None, "Raw encoder 2 value"),
        0x3027: ("as_angle",            "float",  "R", None, None, "AS angle"),
    },
}

# Type-specific parameter extensions - Parameters unique to specific servo types
TYPE_SPECIFIC_EXTENSIONS = {
    "RS00": {
        # Additional configuration parameters
        0x201A: ("loc_ref_filt_gai",    "float",  "RW", 0, 100, "Position reference filter gain"),
        0x201B: ("limit_loc",           "float",  "RW", 0, 100, "Position limit"),
        0x201C: ("position_offset",     "float",  "RW", 0, 27, "Position offset"),
        0x201D: ("chasu_angle_offs",    "float",  "RW", 0, 27, "Chassis angle offset"),
        0x201E: ("spd_step_value",      "float",  "RW", 0, 150, "Speed step value"),
        0x201F: ("vel_max",             "float",  "RW", 0, 20, "Maximum velocity"),
        0x2020: ("acc_set",             "float",  "RW", 0, 1000, "Acceleration setting"),
        0x2021: ("zero_sta",            "uint8",  "RW", 0, 100, "Zero status"),
        0x2022: ("protocol_1",          "uint8",  "RW", 0, 20, "Protocol 1"),
        0x2023: ("damper",              "uint8",  "RW", 0, 20, "Damper setting"),
        0x2024: ("add_offset",          "float",  "RW", -7, 7, "Additional offset"),
        
        # Additional telemetry
        0x3028: ("dtc_u",               "float",  "R", None, None, "DTC U"),
        0x3029: ("dtc_v",               "float",  "R", None, None, "DTC V"),
        0x302A: ("dtc_w",               "float",  "R", None, None, "DTC W"),
        0x302B: ("v_bus",               "float",  "R", None, None, "Bus voltage"),
        0x302C: ("torque_fdb",          "float",  "R", None, None, "Torque feedback"),
        0x302D: ("rated_i",             "float",  "R", None, None, "Rated current"),
        0x302E: ("limit_i",             "float",  "R", None, None, "Current limit"),
        0x302F: ("spd_ref",             "float",  "R", None, None, "Speed reference"),
        0x3030: ("spd_reff",            "float",  "R", None, None, "Speed reference filtered"),
        0x3031: ("zero_fault",          "uint8",  "R", None, None, "Zero fault"),
        0x3032: ("chasu_coder_raw",     "int16",  "R", None, None, "Chassis coder raw"),
        0x3033: ("chasu_angle",         "float",  "R", None, None, "Chassis angle"),
        0x3034: ("as_angle",            "float",  "R", None, None, "AS angle"),
        0x3035: ("vel_max",             "float",  "R", None, None, "Maximum velocity"),
        0x3036: ("judge",               "uint8",  "R", None, None, "Judge parameter"),
        0x3037: ("fault1",              "uint32", "R", None, None, "Fault 1"),
        0x3038: ("fault2",              "uint32", "R", None, None, "Fault 2"),
        0x3040: ("low_position",        "float",  "R", None, None, "Low position"),
        0x3041: ("instep",              "float",  "R", None, None, "In step"),
        0x3048: ("H",                   "uint8",  "R", None, None, "Parameter H"),
    },
    
    "RS02": {
        # Additional configuration parameters
        0x201A: ("loc_ref_filt_gai",    "float",  "RW", 0, 100, "Position reference filter gain"),
        0x201B: ("limit_loc",           "float",  "RW", 0, 100, "Position limit"),
        0x201C: ("position_offset",     "float",  "RW", 0, 27, "Position offset"),
        0x201D: ("chasu_angle_offs",    "float",  "RW", -100, 100, "Chassis angle offset"),
        0x201E: ("zero_sta",            "uint8",  "RW", 0, 100, "Zero status"),
        0x201F: ("protocol_1",          "uint8",  "RW", 0, 20, "Protocol 1"),
        0x2020: ("damper",              "uint8",  "RW", 0, 20, "Damper setting"),
        0x2021: ("add_offset",          "float",  "RW", -7, 7, "Additional offset"),
        
        # Additional telemetry
        0x3028: ("dtc_u",               "float",  "R", None, None, "DTC U"),
        0x3029: ("dtc_v",               "float",  "R", None, None, "DTC V"),
        0x302A: ("dtc_w",               "float",  "R", None, None, "DTC W"),
        0x302B: ("v_bus",               "float",  "R", None, None, "Bus voltage"),
        0x302C: ("torque_fdb",          "float",  "R", None, None, "Torque feedback"),
        0x302D: ("rated_i",             "float",  "R", None, None, "Rated current"),
        0x302E: ("limit_i",             "float",  "R", None, None, "Current limit"),
        0x302F: ("spd_ref",             "float",  "R", None, None, "Speed reference"),
        0x3030: ("motor_mech_angle",    "float",  "R", None, None, "Motor mechanical angle"),
        0x3031: ("position",            "float",  "R", None, None, "Position"),
        0x3032: ("chasu_angle_init",    "float",  "R", None, None, "Chassis angle init"),
        0x3033: ("chasu_angle_out",     "float",  "R", None, None, "Chassis angle output"),
        0x3034: ("motormechinit1",      "float",  "R", None, None, "Motor mech init 1"),
        0x3035: ("mech_angle_init2",    "float",  "R", None, None, "Mechanical angle init 2"),
        0x3036: ("mech_angle_rotat",    "int16",  "R", None, None, "Mechanical angle rotation"),
        0x3037: ("cmdlocref_1",         "float",  "R", None, None, "Command position reference 1"),
        0x3038: ("status_1",            "uint8",  "R", None, None, "Status 1"),
        0x3048: ("can_status",          "uint8",  "R", None, None, "CAN status"),
    },
    
    "RS03": {
        # Configuration with status parameters mapped differently
        0x200C: ("status2",             "int16",  "S", -200, 1500, "Status parameter 2"),
        0x200D: ("status3",             "uint32", "S", 1000, 1000000, "Status parameter 3"),
        0x200E: ("status4",             "float",  "S", 1, 64, "Status parameter 4"),
        0x200F: ("status5",             "float",  "S", -20, 20, "Status parameter 5"),
        0x2010: ("status6",             "uint8",  "S", 0, 127, "Status parameter 6"),
        # Different control parameter ranges
        0x2011: ("cur_filt_gain",       "float",  "RW", -1, 1, "Current filter gain"),
        0x2012: ("cur_kp",              "float",  "RW", -200, 200, "Current Kp gain"),
        0x2013: ("cur_ki",              "float",  "RW", -200, 200, "Current Ki gain"),
        0x2014: ("spd_kp",              "float",  "RW", -200, 200, "Speed Kp gain"),
        0x2015: ("spd_ki",              "float",  "RW", -200, 200, "Speed Ki gain"),
        0x2016: ("loc_kp",              "float",  "RW", -200, 200, "Position Kp gain"),
        0x2017: ("spd_filt_gain",       "float",  "RW", -1, 1, "Speed filter gain"),
        # Additional configuration parameters
        0x201A: ("limit_a",             "float",  "RW", -1, 150, "Limit A"),
        0x201B: ("fault1",              "uint32", "S", 0, 30000, "Fault 1 setting"),
        0x201C: ("fault2",              "uint32", "S", 0, 30000, "Fault 2 setting"),
        0x201D: ("fault3",              "uint32", "S", 0, 30000, "Fault 3 setting"),
        0x201E: ("fault4",              "uint32", "S", 0, 30000, "Fault 4 setting"),
        0x201F: ("fault5",              "uint32", "S", 0, 30000, "Fault 5 setting"),
        0x2020: ("fault6",              "uint32", "S", 0, 30000, "Fault 6 setting"),
        0x2021: ("fault7",              "uint32", "S", 0, 30000, "Fault 7 setting"),
        0x2022: ("baud",                "uint8",  "RW", -10, 10, "Baud rate setting"),
        0x2023: ("zero_sta",            "uint8",  "RW", 0, 100, "Zero status"),
        0x2024: ("position_offset",     "float",  "RW", 0, 27, "Position offset"),
        0x2025: ("protocol_1",          "uint8",  "RW", 0, 20, "Protocol 1"),
        0x2026: ("damper",              "uint8",  "RW", 0, 20, "Damper setting"),
        0x2027: ("add_offset",          "float",  "RW", -7, 7, "Additional offset"),
        
        # Additional telemetry
        0x3028: ("cs_angle",            "float",  "R", None, None, "CS angle"),
        0x3029: ("chasu_angle",         "float",  "R", None, None, "Chassis angle"),
        0x302A: ("v_bus",               "float",  "R", None, None, "Bus voltage"),
        0x302C: ("torque_fdb",          "float",  "R", None, None, "Torque feedback"),
        0x302D: ("rated_i",             "float",  "R", None, None, "Rated current"),
        0x302E: ("MechPos_init",        "float",  "R", None, None, "Initial mechanical position"),
        0x302F: ("instep",              "float",  "R", None, None, "In step"),
        0x3030: ("status",              "uint8",  "R", None, None, "Status"),
        0x3031: ("cmdlocref",           "float",  "R", None, None, "Command position reference"),
        0x3032: ("vel_max",             "float",  "R", None, None, "Maximum velocity"),
        0x3033: ("fault1",              "uint32", "R", None, None, "Fault 1"),
        0x3034: ("fault2",              "uint32", "R", None, None, "Fault 2"),
        0x3035: ("fault3",              "uint32", "R", None, None, "Fault 3"),
        0x3036: ("fault4",              "uint32", "R", None, None, "Fault 4"),
        0x3037: ("fault5",              "uint32", "R", None, None, "Fault 5"),
        0x3038: ("fault6",              "uint32", "R", None, None, "Fault 6"),
        0x3039: ("fault7",              "uint32", "R", None, None, "Fault 7"),
        0x303A: ("fault8",              "uint32", "R", None, None, "Fault 8"),
        0x3041: ("can_status",          "uint8",  "R", None, None, "CAN status"),
    },
    
    "RS04": {
        # Configuration with status parameters mapped differently
        0x200C: ("status2",             "int16",  "S", -200, 1500, "Status parameter 2"),
        0x200D: ("status3",             "uint32", "S", 1000, 1000000, "Status parameter 3"),
        0x200E: ("status4",             "float",  "S", 1, 64, "Status parameter 4"),
        0x200F: ("status5",             "float",  "S", 0, 20, "Status parameter 5"),
        0x2010: ("status6",             "uint8",  "S", 0, 1, "Status parameter 6"),
        # Additional configuration parameters
        0x201A: ("spd_step_value",      "float",  "RW", 0, 150, "Speed step value"),
        0x201B: ("vel_max",             "float",  "RW", 0, 20, "Maximum velocity"),
        0x201C: ("acc_set",             "float",  "RW", 0, 1000, "Acceleration setting"),
        0x201D: ("fault1",              "uint32", "S", 0, 30000, "Fault 1 setting"),
        0x201E: ("fault2",              "uint32", "S", 0, 30000, "Fault 2 setting"),
        0x201F: ("fault3",              "uint32", "S", 0, 30000, "Fault 3 setting"),
        0x2020: ("fault4",              "uint32", "S", 0, 30000, "Fault 4 setting"),
        0x2021: ("fault5",              "uint32", "S", 0, 30000, "Fault 5 setting"),
        0x2022: ("fault6",              "uint32", "S", 0, 30000, "Fault 6 setting"),
        0x2023: ("fault7",              "uint32", "S", 0, 30000, "Fault 7 setting"),
        0x2024: ("baud",                "uint8",  "RW", 0, 10, "Baud rate setting"),
        0x2025: ("zero_sta",            "uint8",  "RW", 0, 100, "Zero status"),
        0x2026: ("position_offset",     "float",  "RW", 0, 27, "Position offset"),
        0x2027: ("protocol_1",          "uint8",  "RW", 0, 20, "Protocol 1"),
        0x2028: ("damper",              "uint8",  "RW", 0, 20, "Damper setting"),
        0x2029: ("add_offset",          "float",  "RW", -7, 7, "Additional offset"),
        
        # Additional telemetry
        0x3028: ("cs_angle",            "float",  "R", None, None, "CS angle"),
        0x3029: ("chasu_angle",         "float",  "R", None, None, "Chassis angle"),
        0x302A: ("ibus",                "float",  "R", None, None, "Bus current"),
        0x302B: ("torque_fdb",          "float",  "R", None, None, "Torque feedback"),
        0x302C: ("rated_i",             "float",  "R", None, None, "Rated current"),
        0x302D: ("MechPos_init",        "float",  "R", None, None, "Initial mechanical position"),
        0x302E: ("vel_max",             "float",  "R", None, None, "Maximum velocity"),
        0x302F: ("loc_reff",            "float",  "R", None, None, "Position reference filtered"),
        0x3030: ("instep",              "float",  "R", None, None, "In step"),
        0x3031: ("fault1",              "uint32", "R", None, None, "Fault 1"),
        0x3032: ("fault2",              "uint32", "R", None, None, "Fault 2"),
        0x3033: ("fault3",              "uint32", "R", None, None, "Fault 3"),
        0x3034: ("fault4",              "uint32", "R", None, None, "Fault 4"),
        0x3035: ("fault5",              "uint32", "R", None, None, "Fault 5"),
        0x3036: ("fault6",              "uint32", "R", None, None, "Fault 6"),
        0x3037: ("fault7",              "uint32", "R", None, None, "Fault 7"),
        0x3038: ("fault8",              "uint32", "R", None, None, "Fault 8"),
    },
}

def get_parameter_map(servo_type: str) -> Dict[int, Tuple[str, str, str, Optional[float], Optional[float], str]]:
    """
    Get the complete parameter map for a specific servo drive type.
    
    Args:
        servo_type: One of "RS00", "RS02", "RS03", "RS04"
        
    Returns:
        Dictionary with parameter definitions in format:
        parameter_index: (name, data_type, access_mode, min_value, max_value, description)
    """
    if servo_type not in ["RS00", "RS02", "RS03", "RS04"]:
        raise ValueError(f"Unknown servo type: {servo_type}. Must be one of: RS00, RS02, RS03, RS04")
    
    # Start with common parameters
    param_map = COMMON_PARAM_MAP.copy()
    
    # Apply type-specific overrides
    if servo_type in TYPE_SPECIFIC_OVERRIDES:
        param_map.update(TYPE_SPECIFIC_OVERRIDES[servo_type])
    
    # Add type-specific extensions
    if servo_type in TYPE_SPECIFIC_EXTENSIONS:
        param_map.update(TYPE_SPECIFIC_EXTENSIONS[servo_type])
    
    return param_map

def get_common_parameters() -> Dict[int, Tuple[str, str, str, Optional[float], Optional[float], str]]:
    """
    Get parameters that are common across all servo types.
    
    Returns:
        Dictionary with common parameter definitions
    """
    return COMMON_PARAM_MAP.copy()

def get_type_specific_parameters(servo_type: str) -> Dict[int, Tuple[str, str, str, Optional[float], Optional[float], str]]:
    """
    Get parameters that are unique to a specific servo type or have type-specific properties.
    
    Args:
        servo_type: One of "RS00", "RS02", "RS03", "RS04"
        
    Returns:
        Dictionary with type-specific parameter definitions
    """
    if servo_type not in ["RS00", "RS02", "RS03", "RS04"]:
        raise ValueError(f"Unknown servo type: {servo_type}. Must be one of: RS00, RS02, RS03, RS04")
    
    type_specific = {}
    
    # Add overrides
    if servo_type in TYPE_SPECIFIC_OVERRIDES:
        type_specific.update(TYPE_SPECIFIC_OVERRIDES[servo_type])
    
    # Add extensions
    if servo_type in TYPE_SPECIFIC_EXTENSIONS:
        type_specific.update(TYPE_SPECIFIC_EXTENSIONS[servo_type])
    
    return type_specific

def compare_parameter_across_types(param_index: int) -> Dict[str, Tuple[str, str, str, Optional[float], Optional[float], str]]:
    """
    Compare a specific parameter across all servo types.
    
    Args:
        param_index: Parameter index to compare
        
    Returns:
        Dictionary mapping servo type to parameter definition, or None if not present
    """
    comparison = {}
    
    for servo_type in ["RS00", "RS02", "RS03", "RS04"]:
        param_map = get_parameter_map(servo_type)
        if param_index in param_map:
            comparison[servo_type] = param_map[param_index]
        else:
            comparison[servo_type] = None
    
    return comparison

def get_parameter_differences(servo_type1: str, servo_type2: str) -> Dict[str, Dict[int, Tuple]]:
    """
    Get parameter differences between two servo types.
    
    Args:
        servo_type1: First servo type
        servo_type2: Second servo type
        
    Returns:
        Dictionary with keys: 'only_in_type1', 'only_in_type2', 'different_properties'
    """
    map1 = get_parameter_map(servo_type1)
    map2 = get_parameter_map(servo_type2)
    
    set1 = set(map1.keys())
    set2 = set(map2.keys())
    
    differences = {
        'only_in_type1': {idx: map1[idx] for idx in set1 - set2},
        'only_in_type2': {idx: map2[idx] for idx in set2 - set1},
        'different_properties': {}
    }
    
    # Find parameters with different properties
    for idx in set1 & set2:
        if map1[idx] != map2[idx]:
            differences['different_properties'][idx] = {
                servo_type1: map1[idx],
                servo_type2: map2[idx]
            }
    
    return differences

def get_parameter_limits(servo_type: str) -> Dict[int, Tuple[Optional[float], Optional[float]]]:
    """
    Get parameter limits for a specific servo drive type.
    
    Args:
        servo_type: One of "RS00", "RS02", "RS03", "RS04"
        
    Returns:
        Dictionary with parameter limits in format:
        parameter_index: (min_value, max_value)
    """
    param_map = get_parameter_map(servo_type)
    limits = {}
    
    for idx, (name, dtype, access, min_val, max_val, desc) in param_map.items():
        if min_val is not None or max_val is not None:
            limits[idx] = (min_val, max_val)
    
    return limits

def get_servo_specs(servo_type: str) -> Dict[str, float]:
    """
    Get the key specifications for a specific servo drive type.
    
    Args:
        servo_type: One of "RS00", "RS02", "RS03", "RS04"
        
    Returns:
        Dictionary with servo specifications
    """
    specs = {
        "RS00": {
            "max_torque": 14.0,     # Nm
            "max_current": 16.0,    # A
            "max_speed": 33.0,      # rad/s
            "description": "14Nm compact actuator"
        },
        "RS02": {
            "max_torque": 17.0,     # Nm
            "max_current": 23.0,    # A
            "max_speed": 44.0,      # rad/s
            "description": "17Nm high-speed actuator"
        },
        "RS03": {
            "max_torque": 60.0,     # Nm
            "max_current": 43.0,    # A
            "max_speed": 20.0,      # rad/s
            "rated_current": 9.0,   # A
            "description": "60Nm medium-torque actuator"
        },
        "RS04": {
            "max_torque": 120.0,    # Nm
            "max_current": 90.0,    # A
            "max_speed": 15.0,      # rad/s
            "rated_current": 19.0,  # A
            "description": "120Nm high-torque actuator"
        },
    }
    
    if servo_type not in specs:
        raise ValueError(f"Unknown servo type: {servo_type}. Must be one of: {list(specs.keys())}")
    
    return specs[servo_type]

def list_all_servo_types() -> List[str]:
    """Return list of all supported servo drive types."""
    return ["RS00", "RS02", "RS03", "RS04"]

def auto_detect_servo_type(app_version: str) -> str:
    """
    Automatically detect servo type from AppCodeVersion parameter.
    
    Args:
        app_version: Value from parameter 0x1003 (AppCodeVersion)
        
    Returns:
        Detected servo type string
    """
    return detect_servo_type_from_version(app_version)

def get_parameter_coverage_summary() -> Dict[str, Dict[str, int]]:
    """
    Get a summary of parameter coverage across servo types.
    
    Returns:
        Dictionary with coverage statistics
    """
    all_param_indices = set()
    type_params = {}
    
    # Collect all parameter indices
    for servo_type in list_all_servo_types():
        param_map = get_parameter_map(servo_type)
        type_params[servo_type] = set(param_map.keys())
        all_param_indices.update(param_map.keys())
    
    # Calculate statistics
    common_count = len(COMMON_PARAM_MAP)
    total_unique = len(all_param_indices)
    
    summary = {
        'common_parameters': common_count,
        'total_unique_parameters': total_unique,
        'coverage_by_type': {}
    }
    
    for servo_type in list_all_servo_types():
        param_count = len(type_params[servo_type])
        type_specific_count = len(get_type_specific_parameters(servo_type))
        
        summary['coverage_by_type'][servo_type] = {
            'total_parameters': param_count,
            'common_parameters': common_count,
            'type_specific_parameters': type_specific_count,
            'coverage_percentage': round((param_count / total_unique) * 100, 1)
        }
    
    return summary


if __name__ == "__main__":
    # Example usage and testing
    print("Robstride Parameter Maps - Refactored")
    print("=" * 50)
    
    # Test version detection
    test_versions = ["0.0.1.0", "0.2.3.9", "0.3.1.5", "0.4.2.1"]
    print("\nVersion Detection Test:")
    for version in test_versions:
        try:
            servo_type = detect_servo_type_from_version(version)
            print(f"  {version} → {servo_type}")
        except ValueError as e:
            print(f"  {version} → Error: {e}")
    
    # Show parameter coverage summary
    print(f"\nParameter Coverage Summary:")
    summary = get_parameter_coverage_summary()
    print(f"  Common parameters: {summary['common_parameters']}")
    print(f"  Total unique parameters: {summary['total_unique_parameters']}")
    print(f"  Coverage by type:")
    
    for servo_type, stats in summary['coverage_by_type'].items():
        specs = get_servo_specs(servo_type)
        print(f"    {servo_type}: {stats['total_parameters']} params ({stats['coverage_percentage']}%) - {specs['description']}")
        print(f"      Common: {stats['common_parameters']}, Type-specific: {stats['type_specific_parameters']}")
    
    # Example parameter comparison
    print(f"\nExample: Comparing MechOffset (0x2005) across types:")
    comparison = compare_parameter_across_types(0x2005)
    for servo_type, param_def in comparison.items():
        if param_def:
            name, dtype, access, min_val, max_val, desc = param_def
            print(f"  {servo_type}: {name} range=[{min_val}, {max_val}] access={access}")
        else:
            print(f"  {servo_type}: Not present")
    
    # Example difference analysis
    print(f"\nDifferences between RS00 and RS02:")
    differences = get_parameter_differences("RS00", "RS02")
    print(f"  Only in RS00: {len(differences['only_in_type1'])} parameters")
    print(f"  Only in RS02: {len(differences['only_in_type2'])} parameters")
    print(f"  Different properties: {len(differences['different_properties'])} parameters")
    
    # Show a few examples of different properties
    if differences['different_properties']:
        print(f"  Examples of different properties:")
        for idx, defs in list(differences['different_properties'].items())[:3]:
            rs00_def = defs['RS00']
            rs02_def = defs['RS02']
            print(f"    0x{idx:04X}: {rs00_def[0]}")
            print(f"      RS00: range=[{rs00_def[3]}, {rs00_def[4]}] access={rs00_def[2]}")
            print(f"      RS02: range=[{rs02_def[3]}, {rs02_def[4]}] access={rs02_def[2]}")
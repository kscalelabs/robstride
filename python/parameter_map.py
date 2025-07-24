#!/usr/bin/env python3
"""
Robstride Parameter Maps

Parameter definitions for different Robstride servo drive types.
Automatically detects servo type from firmware version:
- 0.0.x.x → RS00: 14Nm actuator (max current: 16A, max speed: 33 rad/s)
- 0.2.x.x → RS02: 17Nm actuator (max current: 23A, max speed: 44 rad/s) 
- 0.3.x.x → RS03: 60Nm actuator (max current: 43A, max speed: 20 rad/s)
- 0.4.x.x → RS04: 120Nm actuator (max current: 90A, max speed: 15 rad/s)
"""

import re

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

# RS00 Parameter Map (from actual servo dump)
# Format: parameter_index: (name, data_type, access_mode, min_value, max_value, description)
RS00_PARAM_MAP = {
    # Device identification
    0x0000: ("Name",                "String", "RW", None, None, "Device name"),
    0x0001: ("BarCode",             "String", "RW", None, None, "Device barcode"),
    
    # Boot / firmware info
    0x1000: ("BootCodeVersion",     "String", "R", None, None, "Boot code version"),
    0x1001: ("BootBuildDate",       "String", "R", None, None, "Boot build date"),
    0x1002: ("BootBuildTime",       "String", "R", None, None, "Boot build time"),
    0x1003: ("AppCodeVersion",      "String", "R", None, None, "Application code version"),
    0x1004: ("AppGitVersion",       "String", "R", None, None, "Application git version"),
    0x1005: ("AppBuildDate",        "String", "R", None, None, "Application build date"),
    0x1006: ("AppBuildTime",        "String", "R", None, None, "Application build time"),
    0x1007: ("AppCodeName",         "String", "R", None, None, "Application code name"),
    
    # Configuration block
    0x2000: ("echoPara1",           "uint16", "D", 5, 110, "Echo parameter 1"),
    0x2001: ("echoPara2",           "uint16", "D", 5, 110, "Echo parameter 2"),
    0x2002: ("echoPara3",           "uint16", "D", 5, 110, "Echo parameter 3"),
    0x2003: ("echoPara4",           "uint16", "D", 5, 110, "Echo parameter 4"),
    0x2004: ("echoFreHz",           "uint32", "RW", 1, 10000, "Echo frequency (Hz)"),
    0x2005: ("MechOffset",          "float",  "S", -7, 7, "Mechanical encoder offset"),
    0x2006: ("MechPos_init",        "float",  "RW", -50, 50, "Initial mechanical position"),
    0x2007: ("limit_torque",        "float",  "RW", 0, 14, "Maximum torque limit (Nm)"),
    0x2008: ("I_FW_MAX",            "float",  "RW", 0, 33, "Field-weakening current max"),
    0x2009: ("motor_baud",          "uint8",  "RW", 1, 4, "Motor baud rate configuration"),
    0x200A: ("CAN_ID",              "uint8",  "RW", 0, 127, "Node CAN ID"),
    0x200B: ("CAN_MASTER",          "uint8",  "RW", 0, 300, "Master CAN ID"),
    0x200C: ("CAN_TIMEOUT",         "uint32", "RW", -2000, 2000000, "CAN timeout"),
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
    
    # Timing diagnostics
    0x3000: ("timeUse0",            "uint16", "R", None, None, "Time usage 0"),
    0x3001: ("timeUse1",            "uint16", "R", None, None, "Time usage 1"),
    0x3002: ("timeUse2",            "uint16", "R", None, None, "Time usage 2"),
    0x3003: ("timeUse3",            "uint16", "R", None, None, "Time usage 3"),
    
    # Telemetry & sensor values
    0x3004: ("encoderRaw",          "int16",  "R", None, None, "Raw encoder value"),
    0x3005: ("mcuTemp",             "int16",  "R", None, None, "MCU temperature"),
    0x3006: ("motorTemp",           "int16",  "R", None, None, "Motor temperature"),
    0x3007: ("vBus(mv)",            "uint16", "R", None, None, "Bus voltage (mV)"),
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
    0x3027: ("Ud",                  "float",  "R", None, None, "Voltage Ud"),
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
    0x3039: ("fault3",              "uint32", "R", None, None, "Fault 3"),
    0x303A: ("fault4",              "uint32", "R", None, None, "Fault 4"),
    0x303B: ("fault5",              "uint32", "R", None, None, "Fault 5"),
    0x303C: ("fault6",              "uint32", "R", None, None, "Fault 6"),
    0x303D: ("fault7",              "uint32", "R", None, None, "Fault 7"),
    0x303E: ("fault8",              "uint32", "R", None, None, "Fault 8"),
    0x303F: ("ElecOffset",          "float",  "R", None, None, "Electrical offset"),
    0x3040: ("mcOverTemp",          "int16",  "R", None, None, "MCU over temperature"),
    0x3041: ("Kt_Nm/Amp",           "float",  "R", None, None, "Kt Nm/Amp"),
    0x3042: ("Tqcali_Type",         "uint8",  "R", None, None, "Torque calibration type"),
    0x3043: ("low_position",        "float",  "R", None, None, "Low position"),
    0x3044: ("theta_mech_1",        "float",  "R", None, None, "Theta mechanical 1"),
    0x3045: ("instep",              "float",  "R", None, None, "In step"),
    0x3046: ("adcOffset_1",         "int32",  "R", None, None, "ADC offset 1"),
    0x3047: ("adcOffset_2",         "int32",  "R", None, None, "ADC offset 2"),
    0x3048: ("H",                   "uint8",  "R", None, None, "Parameter H"),
}


# RS02 Parameter Map (from actual servo dump)
# Format: parameter_index: (name, data_type, access_mode, min_value, max_value, description)
RS02_PARAM_MAP = {
    # Device identification
    0x0000: ("Name",                "String", "RW", None, None, "Device name"),
    0x0001: ("BarCode",             "String", "RW", None, None, "Device barcode"),
    
    # Boot / firmware info
    0x1000: ("BootCodeVersion",     "String", "R", None, None, "Boot code version"),
    0x1001: ("BootBuildDate",       "String", "R", None, None, "Boot build date"),
    0x1002: ("BootBuildTime",       "String", "R", None, None, "Boot build time"),
    0x1003: ("AppCodeVersion",      "String", "R", None, None, "Application code version"),
    0x1004: ("AppGitVersion",       "String", "R", None, None, "Application git version"),
    0x1005: ("AppBuildDate",        "String", "R", None, None, "Application build date"),
    0x1006: ("AppBuildTime",        "String", "R", None, None, "Application build time"),
    0x1007: ("AppCodeName",         "String", "R", None, None, "Application code name"),
    
    # Configuration block
    0x2000: ("echoPara1",           "uint16", "D", 5, 107, "Echo parameter 1"),
    0x2001: ("echoPara2",           "uint16", "D", 5, 107, "Echo parameter 2"),
    0x2002: ("echoPara3",           "uint16", "D", 5, 107, "Echo parameter 3"),
    0x2003: ("echoPara4",           "uint16", "D", 5, 107, "Echo parameter 4"),
    0x2004: ("echoFreHz",           "uint32", "RW", 1, 10000, "Echo frequency (Hz)"),
    0x2005: ("MechOffset",          "float",  "S", -10, 10, "Mechanical encoder offset"),
    0x2006: ("status4",             "float",  "RW", -10, 10, "Status parameter 4"),
    0x2007: ("limit_torque",        "float",  "RW", 0, 30, "Maximum torque limit (Nm)"),
    0x2008: ("I_FW_MAX",            "float",  "RW", 0, 33, "Field-weakening current max"),
    0x2009: ("motor_baud",          "uint8",  "RW", 1, 4, "Motor baud rate configuration"),
    0x200A: ("CAN_ID",              "uint8",  "S", 0, 127, "Node CAN ID"),
    0x200B: ("CAN_MASTER",          "uint8",  "RW", 0, 300, "Master CAN ID"),
    0x200C: ("CAN_TIMEOUT",         "uint32", "RW", -2000000, 2000000, "CAN timeout"),
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
    0x201A: ("loc_ref_filt_gai",    "float",  "RW", 0, 100, "Position reference filter gain"),
    0x201B: ("limit_loc",           "float",  "RW", 0, 100, "Position limit"),
    0x201C: ("position_offset",     "float",  "RW", 0, 27, "Position offset"),
    0x201D: ("chasu_angle_offs",    "float",  "RW", -100, 100, "Chassis angle offset"),
    0x201E: ("zero_sta",            "uint8",  "RW", 0, 100, "Zero status"),
    0x201F: ("protocol_1",          "uint8",  "RW", 0, 20, "Protocol 1"),
    0x2020: ("damper",              "uint8",  "RW", 0, 20, "Damper setting"),
    0x2021: ("add_offset",          "float",  "RW", -7, 7, "Additional offset"),
    
    # Timing diagnostics
    0x3000: ("timeUse0",            "uint16", "R", None, None, "Time usage 0"),
    0x3001: ("timeUse1",            "uint16", "R", None, None, "Time usage 1"),
    0x3002: ("timeUse2",            "uint16", "R", None, None, "Time usage 2"),
    0x3003: ("timeUse3",            "uint16", "R", None, None, "Time usage 3"),
    
    # Telemetry & sensor values
    0x3004: ("encoderRaw",          "int16",  "R", None, None, "Raw encoder value"),
    0x3005: ("mcuTemp",             "int16",  "R", None, None, "MCU temperature"),
    0x3006: ("motorTemp",           "int16",  "R", None, None, "Motor temperature"),
    0x3007: ("vBus(mv)",            "uint16", "R", None, None, "Bus voltage (mV)"),
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
    0x3027: ("Ud",                  "float",  "R", None, None, "Voltage Ud"),
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
    0x3039: ("ElecOffset",          "float",  "R", None, None, "Electrical offset"),
    0x303A: ("mcOverTemp",          "int16",  "R", None, None, "MCU over temperature"),
    0x303B: ("Kt_Nm/Amp",           "float",  "R", None, None, "Kt Nm/Amp"),
    0x303C: ("Tqcali_Type",         "uint8",  "R", None, None, "Torque calibration type"),
    0x303D: ("fault1",              "uint32", "R", None, None, "Fault 1"),
    0x303E: ("fault2",              "uint32", "R", None, None, "Fault 2"),
    0x303F: ("fault3",              "uint32", "R", None, None, "Fault 3"),
    0x3040: ("fault4",              "uint32", "R", None, None, "Fault 4"),
    0x3041: ("fault5",              "uint32", "R", None, None, "Fault 5"),
    0x3042: ("fault6",              "uint32", "R", None, None, "Fault 6"),
    0x3043: ("fault7",              "uint32", "R", None, None, "Fault 7"),
    0x3044: ("fault8",              "uint32", "R", None, None, "Fault 8"),
    0x3045: ("theta_mech_1",        "float",  "R", None, None, "Theta mechanical 1"),
    0x3046: ("adcOffset_1",         "int32",  "R", None, None, "ADC offset 1"),
    0x3047: ("adcOffset_2",         "int32",  "R", None, None, "ADC offset 2"),
    0x3048: ("can_status",          "uint8",  "R", None, None, "CAN status"),
}

# RS03 Parameter Map (from actual servo dump)
# Format: parameter_index: (name, data_type, access_mode, min_value, max_value, description)
RS03_PARAM_MAP = {
    # Device identification
    0x0000: ("Name",                "String", "RW", None, None, "Device name"),
    0x0001: ("BarCode",             "String", "RW", None, None, "Device barcode"),
    
    # Boot / firmware info
    0x1000: ("BootCodeVersion",     "String", "R", None, None, "Boot code version"),
    0x1001: ("BootBuildDate",       "String", "R", None, None, "Boot build date"),
    0x1002: ("BootBuildTime",       "String", "R", None, None, "Boot build time"),
    0x1003: ("AppCodeVersion",      "String", "R", None, None, "Application code version"),
    0x1004: ("AppGitVersion",       "String", "R", None, None, "Application git version"),
    0x1005: ("AppBuildDate",        "String", "R", None, None, "Application build date"),
    0x1006: ("AppBuildTime",        "String", "R", None, None, "Application build time"),
    0x1007: ("AppCodeName",         "String", "R", None, None, "Application code name"),
    
    # Configuration block
    0x2000: ("echoPara1",           "uint16", "D", 5, 106, "Echo parameter 1"),
    0x2001: ("echoPara2",           "uint16", "D", 5, 106, "Echo parameter 2"),
    0x2002: ("echoPara3",           "uint16", "D", 5, 106, "Echo parameter 3"),
    0x2003: ("echoPara4",           "uint16", "D", 5, 106, "Echo parameter 4"),
    0x2004: ("echoFreHz",           "uint32", "RW", 1, 10000, "Echo frequency (Hz)"),
    0x2005: ("MechOffset",          "float",  "RW", -50, 50, "Mechanical encoder offset"),
    0x2006: ("chasu_offset",        "float",  "RW", -50, 50, "Chassis offset"),
    0x2007: ("status1",             "float",  "S", -10, 10, "Status parameter 1"),
    0x2008: ("I_FW_MAX",            "float",  "RW", 0, 33, "Field-weakening current max"),
    0x2009: ("CAN_ID",              "uint8",  "RW", 0, 127, "Node CAN ID"),
    0x200A: ("CAN_MASTER",          "uint8",  "RW", 0, 300, "Master CAN ID"),
    0x200B: ("CAN_TIMEOUT",         "uint32", "RW", -100000, 100000, "CAN timeout"),
    0x200C: ("status2",             "int16",  "S", -200, 1500, "Status parameter 2"),
    0x200D: ("status3",             "uint32", "S", 1000, 1000000, "Status parameter 3"),
    0x200E: ("status4",             "float",  "S", 1, 64, "Status parameter 4"),
    0x200F: ("status5",             "float",  "S", -20, 20, "Status parameter 5"),
    0x2010: ("status6",             "uint8",  "S", 0, 127, "Status parameter 6"),
    0x2011: ("cur_filt_gain",       "float",  "RW", -1, 1, "Current filter gain"),
    0x2012: ("cur_kp",              "float",  "RW", -200, 200, "Current Kp gain"),
    0x2013: ("cur_ki",              "float",  "RW", -200, 200, "Current Ki gain"),
    0x2014: ("spd_kp",              "float",  "RW", -200, 200, "Speed Kp gain"),
    0x2015: ("spd_ki",              "float",  "RW", -200, 200, "Speed Ki gain"),
    0x2016: ("loc_kp",              "float",  "RW", -200, 200, "Position Kp gain"),
    0x2017: ("spd_filt_gain",       "float",  "RW", -1, 1, "Speed filter gain"),
    0x2018: ("limit_spd",           "float",  "RW", 0, 200, "Speed limit"),
    0x2019: ("limit_cur",           "float",  "RW", 0, 150, "Current limit"),
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
    
    # Timing diagnostics
    0x3000: ("timeUse0",            "uint16", "R", None, None, "Time usage 0"),
    0x3001: ("timeUse1",            "uint16", "R", None, None, "Time usage 1"),
    0x3002: ("timeUse2",            "uint16", "R", None, None, "Time usage 2"),
    0x3003: ("timeUse3",            "uint16", "R", None, None, "Time usage 3"),
    
    # Telemetry & sensor values
    0x3004: ("encoderRaw",          "uint16", "R", None, None, "Raw encoder value"),
    0x3005: ("mcuTemp",             "int16",  "R", None, None, "MCU temperature"),
    0x3006: ("motorTemp",           "int16",  "R", None, None, "Motor temperature"),
    0x3007: ("encoder2raw",         "uint16", "R", None, None, "Raw encoder 2 value"),
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
    0x3027: ("as_angle",            "float",  "R", None, None, "AS angle"),
    0x3028: ("cs_angle",            "float",  "R", None, None, "CS angle"),
    0x3029: ("chasu_angle",         "float",  "R", None, None, "Chassis angle"),
    0x302A: ("v_bus",               "float",  "R", None, None, "Bus voltage"),
    0x302B: ("ElecOffset",          "float",  "R", None, None, "Electrical offset"),
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
    0x303B: ("mcOverTemp",          "int16",  "R", None, None, "MCU over temperature"),
    0x303C: ("Kt_Nm/Amp",           "float",  "R", None, None, "Kt Nm/Amp"),
    0x303D: ("Tqcali_Type",         "uint8",  "R", None, None, "Torque calibration type"),
    0x303E: ("theta_mech_1",        "float",  "R", None, None, "Theta mechanical 1"),
    0x303F: ("adcOffset_1",         "int32",  "R", None, None, "ADC offset 1"),
    0x3040: ("adcOffset_2",         "int32",  "R", None, None, "ADC offset 2"),
    0x3041: ("can_status",          "uint8",  "R", None, None, "CAN status"),
}

# RS04 Parameter Map (from actual servo dump)
# Format: parameter_index: (name, data_type, access_mode, min_value, max_value, description)
RS04_PARAM_MAP = {
    # Device identification
    0x0000: ("Name",                "String", "RW", None, None, "Device name"),
    0x0001: ("BarCode",             "String", "RW", None, None, "Device barcode"),
    
    # Boot / firmware info
    0x1000: ("BootCodeVersion",     "String", "R", None, None, "Boot code version"),
    0x1001: ("BootBuildDate",       "String", "R", None, None, "Boot build date"),
    0x1002: ("BootBuildTime",       "String", "R", None, None, "Boot build time"),
    0x1003: ("AppCodeVersion",      "String", "R", None, None, "Application code version"),
    0x1004: ("AppGitVersion",       "String", "R", None, None, "Application git version"),
    0x1005: ("AppBuildDate",        "String", "R", None, None, "Application build date"),
    0x1006: ("AppBuildTime",        "String", "R", None, None, "Application build time"),
    0x1007: ("AppCodeName",         "String", "R", None, None, "Application code name"),
    
    # Configuration block
    0x2000: ("echoPara1",           "uint16", "D", 5, 106, "Echo parameter 1"),
    0x2001: ("echoPara2",           "uint16", "D", 5, 106, "Echo parameter 2"),
    0x2002: ("echoPara3",           "uint16", "D", 5, 106, "Echo parameter 3"),
    0x2003: ("echoPara4",           "uint16", "D", 5, 106, "Echo parameter 4"),
    0x2004: ("echoFreHz",           "uint32", "RW", 1, 10000, "Echo frequency (Hz)"),
    0x2005: ("MechOffset",          "float",  "RW", -50, 50, "Mechanical encoder offset"),
    0x2006: ("chasu_offset",        "float",  "RW", -50, 50, "Chassis offset"),
    0x2007: ("status1",             "float",  "S", -10, 10, "Status parameter 1"),
    0x2008: ("I_FW_MAX",            "float",  "RW", 0, 33, "Field-weakening current max"),
    0x2009: ("CAN_ID",              "uint8",  "RW", 0, 127, "Node CAN ID"),
    0x200A: ("CAN_MASTER",          "uint8",  "RW", 0, 300, "Master CAN ID"),
    0x200B: ("CAN_TIMEOUT",         "uint32", "RW", -10000, 100000, "CAN timeout"),
    0x200C: ("status2",             "int16",  "S", -200, 1500, "Status parameter 2"),
    0x200D: ("status3",             "uint32", "S", 1000, 1000000, "Status parameter 3"),
    0x200E: ("status4",             "float",  "S", 1, 64, "Status parameter 4"),
    0x200F: ("status5",             "float",  "S", 0, 20, "Status parameter 5"),
    0x2010: ("status6",             "uint8",  "S", 0, 1, "Status parameter 6"),
    0x2011: ("cur_filt_gain",       "float",  "RW", 0, 1, "Current filter gain"),
    0x2012: ("cur_kp",              "float",  "RW", 0, 200, "Current Kp gain"),
    0x2013: ("cur_ki",              "float",  "RW", 0, 200, "Current Ki gain"),
    0x2014: ("spd_kp",              "float",  "RW", 0, 200, "Speed Kp gain"),
    0x2015: ("spd_ki",              "float",  "RW", 0, 200, "Speed Ki gain"),
    0x2016: ("loc_kp",              "float",  "RW", 0, 200, "Position Kp gain"),
    0x2017: ("spd_filt_gain",       "float",  "RW", 0, 1, "Speed filter gain"),
    0x2018: ("limit_spd",           "float",  "RW", 0, 200, "Speed limit"),
    0x2019: ("limit_cur",           "float",  "RW", 0, 150, "Current limit"),
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
    
    # Timing diagnostics
    0x3000: ("timeUse0",            "uint16", "R", None, None, "Time usage 0"),
    0x3001: ("timeUse1",            "uint16", "R", None, None, "Time usage 1"),
    0x3002: ("timeUse2",            "uint16", "R", None, None, "Time usage 2"),
    0x3003: ("timeUse3",            "uint16", "R", None, None, "Time usage 3"),
    
    # Telemetry & sensor values
    0x3004: ("encoderRaw",          "uint16", "R", None, None, "Raw encoder value"),
    0x3005: ("mcuTemp",             "int16",  "R", None, None, "MCU temperature"),
    0x3006: ("motorTemp",           "int16",  "R", None, None, "Motor temperature"),
    0x3007: ("encoder2raw",         "uint16", "R", None, None, "Raw encoder 2 value"),
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
    0x3027: ("as_angle",            "float",  "R", None, None, "AS angle"),
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
    0x3039: ("ElecOffset",          "float",  "R", None, None, "Electrical offset"),
    0x303A: ("mcOverTemp",          "int16",  "R", None, None, "MCU over temperature"),
    0x303B: ("Kt_Nm/Amp",           "float",  "R", None, None, "Kt Nm/Amp"),
    0x303C: ("Tqcali_Type",         "uint8",  "R", None, None, "Torque calibration type"),
    0x303D: ("theta_mech_1",        "float",  "R", None, None, "Theta mechanical 1"),
    0x303E: ("adcOffset_1",         "int32",  "R", None, None, "ADC offset 1"),
    0x303F: ("adcOffset_2",         "int32",  "R", None, None, "ADC offset 2"),
}

def get_parameter_map(servo_type: str) -> dict:
    """
    Get the complete parameter map for a specific servo drive type.
    
    Args:
        servo_type: One of "RS00", "RS02", "RS03", "RS04"
        
    Returns:
        Dictionary with parameter definitions in format:
        parameter_index: (name, data_type, access_mode, min_value, max_value, description)
    """
    param_maps = {
        "RS00": RS00_PARAM_MAP,
        "RS02": RS02_PARAM_MAP,
        "RS03": RS03_PARAM_MAP,
        "RS04": RS04_PARAM_MAP
    }
    
    if servo_type not in param_maps:
        raise ValueError(f"Unknown servo type: {servo_type}. Must be one of: {list(param_maps.keys())}")
    
    param_map = param_maps[servo_type]
    if not param_map:
        raise ValueError(f"Parameter map for {servo_type} not yet implemented")
    
    return param_map

def get_parameter_limits(servo_type: str) -> dict:
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

def get_servo_specs(servo_type: str) -> dict:
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
            "max_torque": 17.0,     # Nm (from limit_torque max: 30, but spec is 17)
            "max_current": 23.0,    # A (from limit_i)
            "max_speed": 44.0,      # rad/s (from limit_spd, but max is 200)
            "description": "17Nm high-speed actuator"
        },
        "RS03": {
            "max_torque": 60.0,     # Nm (estimated from higher torque class)
            "max_current": 43.0,    # A (from limit_cur configured max)
            "max_speed": 20.0,      # rad/s (from limit_spd configured max)
            "rated_current": 9.0,   # A (from rated_i parameter)
            "description": "60Nm medium-torque actuator"
        },
        "RS04": {
            "max_torque": 120.0,    # Nm (estimated from highest torque class)
            "max_current": 90.0,    # A (from limit_cur configured max)
            "max_speed": 15.0,      # rad/s (from limit_spd typical, but max config is 200)
            "rated_current": 19.0,  # A (from rated_i parameter)
            "description": "120Nm high-torque actuator"
        },
    }
    
    if servo_type not in specs:
        raise ValueError(f"Unknown servo type: {servo_type}. Must be one of: {list(specs.keys())}")
    
    return specs[servo_type]

def list_all_servo_types() -> list:
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


if __name__ == "__main__":
    # Example usage and testing
    print("Robstride Parameter Maps")
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
    
    # Show implemented servo types
    print(f"\nImplemented Servo Types:")
    for servo_type in list_all_servo_types():
        try:
            param_map = get_parameter_map(servo_type)
            specs = get_servo_specs(servo_type)
            print(f"  {servo_type}: {len(param_map)} parameters - {specs['description']}")
        except ValueError:
            print(f"  {servo_type}: Not yet implemented")
    
    # Show RS02 parameter summary
    print(f"\nRS02 Parameter Summary:")
    rs02_params = get_parameter_map("RS02")
    
    # Group by parameter ranges
    groups = {
        "Device Info (0x0000-0x0001)": [p for p in rs02_params.keys() if 0x0000 <= p <= 0x0001],
        "Firmware Info (0x1000-0x1007)": [p for p in rs02_params.keys() if 0x1000 <= p <= 0x1007],
        "Configuration (0x2000-0x2021)": [p for p in rs02_params.keys() if 0x2000 <= p <= 0x2021],
        "Diagnostics (0x3000-0x3003)": [p for p in rs02_params.keys() if 0x3000 <= p <= 0x3003],
        "Telemetry (0x3004-0x3048)": [p for p in rs02_params.keys() if 0x3004 <= p <= 0x3048],
    }
    
    for group_name, param_indices in groups.items():
        if param_indices:
            print(f"  {group_name}: {len(param_indices)} parameters")
    
    print(f"  Total: {len(rs02_params)} parameters")
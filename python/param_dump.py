#!/usr/bin/env python3
"""
Robstride Parameter Dump Utility

Simple utility to dump all parameters from a Robstride actuator
and display them in a nice table format.
"""

import robstride_driver
import struct
from tabulate import tabulate
import argparse
import sys

# Complete parameter definitions from robstride-driver/src/parameters.rs
PARAM_DEFINITIONS = {
    # ------------------------------------------------------------------
    # Device identification
    # ------------------------------------------------------------------
    0x0000: ("Name",                "String", "RW"),
    0x0001: ("BarCode",             "String", "RW"),

    # ------------------------------------------------------------------
    # Boot / firmware info
    # ------------------------------------------------------------------
    0x1000: ("BootCodeVersion",     "String", "R"),
    0x1001: ("BootBuildDate",       "String", "R"),
    0x1002: ("BootBuildTime",       "String", "R"),
    0x1003: ("AppCodeVersion",      "String", "R"),
    0x1004: ("AppGitVersion",       "String", "R"),
    0x1005: ("AppBuildDate",        "String", "R"),
    0x1006: ("AppBuildTime",        "String", "R"),
    0x1007: ("AppCodeName",         "String", "R"),

    # ------------------------------------------------------------------
    # Configuration block (0x2000 – 0x2024)
    # ------------------------------------------------------------------
    0x2000: ("echoPara1",           "uint16", "D"),
    0x2001: ("echoPara2",           "uint16", "D"),
    0x2002: ("echoPara3",           "uint16", "D"),
    0x2003: ("echoPara4",           "uint16", "D"),
    0x2004: ("echoFreHz",           "uint32", "RW"),
    0x2005: ("MechOffset",          "float",  "S"),
    0x2006: ("MechPos_init",        "float",  "RW"),          # ← fixed
    0x2007: ("limit_torque",        "float",  "RW"),
    0x2008: ("I_FW_MAX",            "float",  "RW"),
    0x2009: ("motor_baud",          "uint8",  "S"),
    0x200A: ("CAN_ID",              "uint8",  "S"),
    0x200B: ("CAN_MASTER",          "uint8",  "S"),
    0x200C: ("CAN_TIMEOUT",         "uint32", "RW"),
    0x200D: ("status2_i16",         "int16",  "RW"),
    0x200E: ("status3",             "uint32", "RW"),
    0x200F: ("status1",             "float",  "RW"),
    0x2010: ("status6",             "uint8",  "RW"),
    0x2011: ("cur_filt_gain",       "float",  "RW"),
    0x2012: ("cur_kp",              "float",  "RW"),
    0x2013: ("cur_ki",              "float",  "RW"),
    0x2014: ("spd_kp",              "float",  "RW"),
    0x2015: ("spd_ki",              "float",  "RW"),
    0x2016: ("loc_kp",              "float",  "RW"),
    0x2017: ("spd_filt_gain",       "float",  "RW"),
    0x2018: ("limit_spd",           "float",  "RW"),
    0x2019: ("limit_cur",           "float",  "RW"),
    0x201A: ("loc_ref_filt_gain",   "float",  "RW"),
    0x201B: ("limit_loc",           "float",  "RW"),
    0x201C: ("position_offset",     "float",  "RW"),
    0x201D: ("chasu_angle_offset",  "float",  "RW"),
    0x201E: ("spd_step_value",      "float",  "RW"),          # ← added
    0x201F: ("vel_max",             "float",  "RW"),          # ← added
    0x2020: ("acc_set",             "float",  "RW"),          # ← added
    0x2021: ("zero_sta",            "float",  "RW"),          # ← shifted
    0x2022: ("protocol_1",          "uint8",  "RW"),          # ← uint8
    0x2023: ("damper",              "uint8",  "RW"),          # ← new
    0x2024: ("add_offset",          "float",  "RW"),          # ← new

    # ------------------------------------------------------------------
    # Timing diagnostics
    # ------------------------------------------------------------------
    0x3000: ("timeUse0",            "uint16", "R"),
    0x3001: ("timeUse1",            "uint16", "R"),
    0x3002: ("timeUse2",            "uint16", "R"),
    0x3003: ("timeUse3",            "uint16", "R"),

    # ------------------------------------------------------------------
    # Telemetry & sensor values
    # ------------------------------------------------------------------
    0x3004: ("encoderRaw",          "int16",  "R"),
    0x3005: ("mcuTemp",             "int16",  "R"),
    0x3006: ("motorTemp",           "int16",  "R"),
    0x3007: ("vBus_mv",            "uint16", "R"),
    0x3008: ("adc1Offset",          "int32",  "R"),
    0x3009: ("adc2Offset",          "int32",  "R"),
    0x300A: ("adc1Raw",            "uint16", "R"),
    0x300B: ("adc2Raw",            "uint16", "R"),
    0x300C: ("VBUS",               "float",  "R"),
    0x300D: ("cmdId",              "float",  "R"),
    0x300E: ("cmdIq",              "float",  "R"),
    0x300F: ("cmdLocRef",          "float",  "R"),
    0x3010: ("cmdSpdRef",          "float",  "R"),
    0x3011: ("cmdTorque",          "float",  "R"),
    0x3012: ("cmdPos",             "float",  "R"),
    0x3013: ("cmdVel",             "float",  "R"),
    0x3014: ("rotation",           "int16",  "R"),
    0x3015: ("modPos",             "float",  "R"),
    0x3016: ("mechPos",            "float",  "R"),
    0x3017: ("mechVel",            "float",  "R"),
    0x3018: ("elecPos",            "float",  "R"),
    0x3019: ("ia",                 "float",  "R"),
    0x301A: ("ib",                 "float",  "R"),
    0x301B: ("ic",                 "float",  "R"),
    0x301C: ("timeout_cnt",        "uint32", "R"),
    0x301D: ("phaseOrder",         "uint8",  "R"),
    0x301E: ("iq_filter",          "float",  "R"),
    0x301F: ("boardTemp",          "int16",  "R"),
    0x3020: ("iq",                 "float",  "R"),
    0x3021: ("id",                 "float",  "R"),
    0x3022: ("faultSta",           "uint32", "R"),
    0x3023: ("warnSta",            "uint32", "R"),
    0x3024: ("drv_fault",          "uint16", "R"),
    0x3025: ("drv_temp",           "int16",  "R"),
    0x3026: ("Uq",                 "float",  "R"),
    0x3027: ("Ud",                 "float",  "R"),
    0x3028: ("dtc_u",              "float",  "R"),
    0x3029: ("dtc_v",              "float",  "R"),
    0x302A: ("dtc_w",              "float",  "R"),
    0x302B: ("v_bus",             "float",  "R"),
    0x302C: ("torque_fdb",         "float",  "R"),
    0x302D: ("rated_i",           "float",  "R"),
    0x302E: ("limit_i",           "float",  "R"),
    0x302F: ("spd_ref",           "float",  "R"),

    # Extended diagnostics / fault log
    0x3030: ("spd_reff",           "float",  "R"),
    0x3031: ("zero_fault",         "float",  "R"),
    0x3032: ("chasu_coder_raw",    "float",  "R"),
    0x3033: ("chasu_angle",        "float",  "R"),
    0x3034: ("as_angle",           "float",  "R"),
    0x3035: ("vel_max_diag",       "float",  "R"),
    0x3036: ("judge",              "float",  "R"),
    0x3037: ("fault1",            "uint32", "R"),
    0x3038: ("fault2",            "uint32", "R"),
    0x3039: ("fault3",            "uint32", "R"),
    0x303A: ("fault4",            "uint32", "R"),
    0x303B: ("fault5",            "uint32", "R"),
    0x303C: ("fault6",            "uint32", "R"),
    0x303D: ("fault7",            "uint32", "R"),
    0x303E: ("fault8",            "uint32", "R"),
    0x303F: ("ElecOffset",        "float",  "R"),
    0x3040: ("mcOverTemp",        "int16",  "R"),
    0x3041: ("Kt_Nm_Amp",         "float",  "R"),
    0x3042: ("Tqcali_Type",        "uint8",  "R"),
    0x3043: ("low_position",      "float",  "R"),
    0x3044: ("theta_mech_1",      "float",  "R"),
    0x3045: ("instep",            "float",  "R"),
}


def decode_parameter(param_index: int, raw_bytes: bytes) -> str:
    """Decode raw parameter bytes based on known type"""
    if param_index not in PARAM_DEFINITIONS:
        return f"Raw: {raw_bytes.hex()}"
    
    name, param_type, access = PARAM_DEFINITIONS[param_index]
    
    try:
        if param_type == "String":
            # Protocol returns: parameter_name + null_padding + actual_value + null_padding
            # Split by null bytes and find the actual value (not the parameter name)
            parts = raw_bytes.split(b'\x00')
            
            # Filter out empty parts
            non_empty_parts = [part for part in parts if part]
            
            if len(non_empty_parts) >= 2:
                param_name = non_empty_parts[0].decode('utf-8', errors='ignore')
                
                # Protocol structure: [param_name, type_prefix+value, optional_binary_data, ...]
                # The actual value is usually in the second part with a type prefix
                
                # Try the second part first (most reliable for type_prefix+value)
                second_part = non_empty_parts[1].decode('utf-8', errors='ignore')
                
                # Check if it starts with a known type prefix
                # Observed prefixes: t(time), e(extended time/date), m(minute/time), i(int/version), 
                # s(string), o(object/version), f(float), b(binary), v(version), d(date), etc.
                if len(second_part) >= 2 and second_part[0] in 'temiosfbvdnlrcpugh':
                    # Extract clean value part (stop at any non-printable/binary chars)
                    value_part = second_part[1:]  # Remove type prefix
                    clean_value = ""
                    for char in value_part:
                        if char.isprintable() and ord(char) >= 32:
                            clean_value += char
                        else:
                            break
                    return clean_value if clean_value else second_part[1:]
                
                # Fallback: try the last meaningful part (for cases without clear type prefix)
                last_part = non_empty_parts[-1].decode('utf-8', errors='ignore')
                if last_part and len(last_part) > 1 and last_part[0] in 'temiosfbvdnlrcpugh':
                    return last_part[1:]
                
                return last_part
            elif len(non_empty_parts) == 1:
                # Only one part - might be just the value or just the name
                single_part = non_empty_parts[0].decode('utf-8', errors='ignore')
                # If it matches the expected parameter name, return empty
                if single_part.lower() == name.lower():
                    return "(empty)"
                return single_part
            else:
                return "(empty)"
        elif param_type == "uint8":
            # For uint8, try position 18 first, then fallback to start
            if len(raw_bytes) > 18:
                return str(raw_bytes[18])
            return str(struct.unpack('<B', raw_bytes[:1])[0])
        elif param_type == "uint16":
            # For uint16, the value is at position 18 as little endian
            if len(raw_bytes) >= 20:  # position 18 + 2 bytes
                return str(struct.unpack('<H', raw_bytes[18:20])[0])
            return str(struct.unpack('<H', raw_bytes[:2])[0])
        elif param_type == "uint32":
            # For uint32, the value is at position 26 as little endian  
            if len(raw_bytes) >= 30:  # position 26 + 4 bytes
                return str(struct.unpack('<L', raw_bytes[26:30])[0])
            return str(struct.unpack('<L', raw_bytes[:4])[0])
        elif param_type == "int16":
            # For int16, try position 18 first, then fallback
            if len(raw_bytes) >= 20:
                return str(struct.unpack('<h', raw_bytes[18:20])[0])
            return str(struct.unpack('<h', raw_bytes[:2])[0])
        elif param_type == "int32":
            # For int32, try position 26 first, then fallback
            if len(raw_bytes) >= 30:
                return str(struct.unpack('<l', raw_bytes[26:30])[0])
            return str(struct.unpack('<l', raw_bytes[:4])[0])
        elif param_type == "float":
            # For float, try position 26 first, then fallback
            if len(raw_bytes) >= 30:
                return f"{struct.unpack('<f', raw_bytes[26:30])[0]:.6f}"
            return f"{struct.unpack('<f', raw_bytes[:4])[0]:.6f}"
        else:
            return f"Raw: {raw_bytes.hex()}"
    except:
        return f"Raw: {raw_bytes.hex()}"

def main():
    parser = argparse.ArgumentParser(description='Dump Robstride actuator parameters')
    
    # Support both single actuator ID and multiple IDs
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('actuator_id', nargs='?', type=int, help='Single actuator CAN ID')
    group.add_argument('--ids', type=str, help='Comma-separated actuator IDs (e.g., 11,12,13,21) or "all" to scan 1-250')
    
    parser.add_argument('--interfaces', '-i', default='can0,can1,can2,can3,can4', 
                       help='Comma-separated CAN interfaces (default: can0,can1,can2,can3,can4)')
    parser.add_argument('--format', choices=['table', 'csv'], default='table', help='Output format')
    parser.add_argument('--debug', action='store_true', help='Show debug information for parameter decoding')
    parser.add_argument('--filter', type=str, help='Filter parameters by name pattern (case-insensitive)')
    
    args = parser.parse_args()
    
    # Parse actuator IDs
    if args.actuator_id:
        target_ids = [args.actuator_id]
    elif args.ids.lower() == 'all':
        target_ids = list(range(11, 50))  # Scan IDs 11-49
        print(f"Scanning for ALL actuators (IDs 11-49)...")
    else:
        target_ids = [int(x.strip()) for x in args.ids.split(',')]
    
    # Parse interfaces
    interfaces = [x.strip() for x in args.interfaces.split(',')]
    
    print(f"Looking for actuators {target_ids} across interfaces {interfaces}")
    
    try:
        # Discover actuators across all interfaces
        actuator_locations = {}  # {actuator_id: (interface, driver)}
        all_parameters = {}      # {actuator_id: {param_index: raw_bytes}}
        total_found = 0
        
        for interface_idx, interface in enumerate(interfaces, 1):
            # Show progress for "all" scan
            if args.ids and args.ids.lower() == 'all':
                print(f"\n[{interface_idx}/{len(interfaces)}] Scanning {interface} ({total_found} found so far)...")
            else:
                print(f"\nScanning {interface}...")
            
            try:
                driver = robstride_driver.PyRobstrideDriver(interface)
                driver.connect(interface)
                
                # Get remaining target IDs not yet found
                remaining_targets = [tid for tid in target_ids if tid not in actuator_locations]
                if not remaining_targets:
                    print(f"  All target actuators already found, skipping...")
                    continue
                
                # For efficiency, scan all remaining IDs at once if we're doing a full scan
                if len(remaining_targets) > 10:  # Bulk scan for many IDs
                    print(f"  Bulk scanning {len(remaining_targets)} IDs ({min(remaining_targets)}-{max(remaining_targets)})...")
                    min_id, max_id = min(remaining_targets), max(remaining_targets)
                    found = driver.scan_actuators(min_id, max_id)
                    found_actuators = [aid for aid in found if aid in remaining_targets]
                else:  # Individual scan for few IDs
                    found_actuators = []
                    for target_id in remaining_targets:
                        found = driver.scan_actuators(target_id, target_id)
                        if target_id in found:
                            found_actuators.append(target_id)
                
                # Register found actuators
                for actuator_id in found_actuators:
                    actuator_locations[actuator_id] = (interface, driver)
                
                total_found += len(found_actuators)
                
                if found_actuators:
                    print(f"  Found actuators: {sorted(found_actuators)} (total: {total_found})")
                    
                    # Get parameters from found actuators
                    for actuator_id in sorted(found_actuators):
                        print(f"  Dumping parameters from actuator {actuator_id}...")
                        try:
                            params = driver.dump_all_parameters(actuator_id)
                            if params:
                                all_parameters[actuator_id] = params
                                print(f"    Retrieved {len(params)} parameters")
                            else:
                                print(f"    No parameters retrieved from actuator {actuator_id}")
                        except Exception as e:
                            print(f"    Error getting parameters from actuator {actuator_id}: {e}")
                else:
                    print(f"  No target actuators found")
                    
            except Exception as e:
                print(f"  Error with interface {interface}: {e}")
                continue
        
        # Check if we found all requested actuators
        missing_actuators = set(target_ids) - set(actuator_locations.keys())
        if missing_actuators:
            print(f"\nWarning: Could not find actuators: {list(missing_actuators)}")
        
        if not all_parameters:
            print("No parameters retrieved from any actuators.")
            return 1
        
        print(f"\nSuccessfully retrieved parameters from actuators: {list(all_parameters.keys())}")
        
        # Build comparison table
        # Get all unique parameter indices across all actuators, but only include known parameters
        all_param_indices = set()
        for params in all_parameters.values():
            # Only include parameters that are in our definitions
            known_params = {idx for idx in params.keys() if idx in PARAM_DEFINITIONS}
            all_param_indices.update(known_params)
        
        print(f"Found {len(all_param_indices)} known parameters across all actuators")
         
        # Apply filter if specified
        filtered_indices = all_param_indices
        if args.filter:
            filter_pattern = args.filter.lower()
            filtered_indices = set()
            for param_idx in all_param_indices:
                param_name = PARAM_DEFINITIONS[param_idx][0].lower()
                if filter_pattern in param_name:
                    filtered_indices.add(param_idx)
            print(f"Filtering parameters containing '{args.filter}': {len(filtered_indices)}/{len(all_param_indices)} parameters")
        
        # Sort actuator IDs for consistent column order
        sorted_actuator_ids = sorted(all_parameters.keys())
        
        # Build table data
        table_data = []
        for param_index in sorted(filtered_indices):
            # We know all parameters are in PARAM_DEFINITIONS since we filtered above
            name, param_type, access = PARAM_DEFINITIONS[param_index]
            
            row = [f"0x{param_index:04X}", name, param_type, access]
        
            # Add value for each actuator
            for actuator_id in sorted_actuator_ids:
                if param_index in all_parameters[actuator_id]:
                    raw_bytes = bytes(all_parameters[actuator_id][param_index])
                    
                    if args.debug:
                        print(f"\nDecoding parameter 0x{param_index:04X} for actuator {actuator_id}:")
                        print(f"  Raw hex: {raw_bytes.hex().upper()}")
                    
                    decoded_value = decode_parameter(param_index, raw_bytes)
                    
                    if args.debug:
                        print(f"  Decoded value: \"{decoded_value}\"")
                    
                    row.append(decoded_value)
                else:
                    row.append("N/A")
        
            table_data.append(row)
        
        # Format output
        if args.format == 'table':
            headers = ["Code", "Name", "Type", "Access"] + [f"ID_{aid}" for aid in sorted_actuator_ids]
            print(f"\nParameter Comparison Table:")
            print(f"Found {len(sorted_actuator_ids)} actuators with {len(filtered_indices)} parameters")
            print("=" * 80)
            print(tabulate(table_data, headers=headers, tablefmt="simple", maxcolwidths=[None, 20, 8, 6] + [15] * len(sorted_actuator_ids)))
        else:  # CSV
            headers = ["Code", "Name", "Type", "Access"] + [f"ID_{aid}" for aid in sorted_actuator_ids]
            print(",".join(headers))
            for row in table_data:
                print(",".join(str(cell) for cell in row))
        
        print(f"\nSummary:")
        for actuator_id in sorted_actuator_ids:
            interface, _ = actuator_locations[actuator_id]
            param_count = len(all_parameters[actuator_id])
            print(f"  Actuator {actuator_id} ({interface}): {param_count} parameters")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
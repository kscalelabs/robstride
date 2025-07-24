#!/usr/bin/env python3
"""
Robstride Parameter Dump Utility

Simple utility to dump all parameters from a Robstride actuator
and display them in a nice table format. Detects servo type from firmware version.
"""

import robstride_driver
import struct
from tabulate import tabulate
import argparse
import sys
from parameter_map import get_parameter_map, auto_detect_servo_type, list_all_servo_types
def decode_parameter(param_index: int, raw_bytes: bytes, servo_type: str = None) -> str:
    """Decode raw parameter bytes based on known type"""
    
    param_map = get_parameter_map(servo_type)
    if param_index in param_map:
        name, param_type, access, min_val, max_val, desc = param_map[param_index]
    else:
        return f"Raw: {raw_bytes.hex()}"
  
   
    # Rest of the decode_parameter function stays the same...
    try:
        if param_type == "String":
            # Protocol returns: parameter_name + null_padding + actual_value + null_padding
            parts = raw_bytes.split(b'\x00')
            non_empty_parts = [part for part in parts if part]
            
            if len(non_empty_parts) >= 2:
                second_part = non_empty_parts[1].decode('utf-8', errors='ignore')
                if len(second_part) >= 2 and second_part[0] in 'temiosfbvdnlrcpugh':
                    value_part = second_part[1:]
                    clean_value = ""
                    for char in value_part:
                        if char.isprintable() and ord(char) >= 32:
                            clean_value += char
                        else:
                            break
                    return clean_value if clean_value else second_part[1:]
                
                last_part = non_empty_parts[-1].decode('utf-8', errors='ignore')
                if last_part and len(last_part) > 1 and last_part[0] in 'temiosfbvdnlrcpugh':
                    return last_part[1:]
                return last_part
            elif len(non_empty_parts) == 1:
                single_part = non_empty_parts[0].decode('utf-8', errors='ignore')
                if single_part.lower() == name.lower():
                    return "(empty)"
                return single_part
            else:
                return "(empty)"
        elif param_type == "uint8":
            if len(raw_bytes) > 18:
                return str(raw_bytes[18])
            return str(struct.unpack('<B', raw_bytes[:1])[0])
        elif param_type == "uint16":
            if len(raw_bytes) >= 20:
                return str(struct.unpack('<H', raw_bytes[18:20])[0])
            return str(struct.unpack('<H', raw_bytes[:2])[0])
        elif param_type == "uint32":
            if len(raw_bytes) >= 30:
                return str(struct.unpack('<L', raw_bytes[26:30])[0])
            return str(struct.unpack('<L', raw_bytes[:4])[0])
        elif param_type == "int16":
            if len(raw_bytes) >= 20:
                return str(struct.unpack('<h', raw_bytes[18:20])[0])
            return str(struct.unpack('<h', raw_bytes[:2])[0])
        elif param_type == "int32":
            if len(raw_bytes) >= 30:
                return str(struct.unpack('<l', raw_bytes[26:30])[0])
            return str(struct.unpack('<l', raw_bytes[:4])[0])
        elif param_type == "float":
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
    parser.add_argument('--servo-type', type=str, choices=list_all_servo_types() if USE_NEW_PARAM_MAPS else [], 
                       help='Override servo type detection (auto-detected from firmware if not specified)')
    
    args = parser.parse_args()
    
    # Parse actuator IDs
    if args.actuator_id:
        target_ids = [args.actuator_id]
    elif args.ids.lower() == 'all':
        target_ids = list(range(11, 50))
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
        servo_types = {}         # {actuator_id: servo_type}
        total_found = 0
        
        for interface_idx, interface in enumerate(interfaces, 1):
            if args.ids and args.ids.lower() == 'all':
                print(f"\n[{interface_idx}/{len(interfaces)}] Scanning {interface} ({total_found} found so far)...")
            else:
                print(f"\nScanning {interface}...")
            
            try:
                driver = robstride_driver.PyRobstrideDriver(interface)
                driver.connect(interface)
                
                remaining_targets = [tid for tid in target_ids if tid not in actuator_locations]
                if not remaining_targets:
                    print(f"  All target actuators already found, skipping...")
                    continue
                
                # Scan for actuators
                if len(remaining_targets) > 10:
                    print(f"  Bulk scanning {len(remaining_targets)} IDs ({min(remaining_targets)}-{max(remaining_targets)})...")
                    min_id, max_id = min(remaining_targets), max(remaining_targets)
                    found = driver.scan_actuators(min_id, max_id)
                    found_actuators = [aid for aid in found if aid in remaining_targets]
                else:
                    found_actuators = []
                    for target_id in remaining_targets:
                        found = driver.scan_actuators(target_id, target_id)
                        if target_id in found:
                            found_actuators.append(target_id)
                
                # Register found actuators and get parameters
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
                                
                                # Auto-detect servo type from firmware version
                                if USE_NEW_PARAM_MAPS and not args.servo_type:
                                    if 0x1003 in params:  # AppCodeVersion parameter
                                        try:
                                            version_bytes = bytes(params[0x1003])
                                            version_str = decode_parameter(0x1003, version_bytes)
                                            servo_type = auto_detect_servo_type(version_str)
                                            servo_types[actuator_id] = servo_type
                                            print(f"    Auto-detected servo type: {servo_type} (firmware: {version_str})")
                                        except Exception as e:
                                            print(f"    Could not auto-detect servo type: {e}")
                                            if args.servo_type:
                                                servo_types[actuator_id] = args.servo_type
                                elif args.servo_type:
                                    servo_types[actuator_id] = args.servo_type
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
        all_param_indices = set()
        for params in all_parameters.values():
            all_param_indices.update(params.keys())
        
        # Apply filter if specified
        filtered_indices = all_param_indices
        if args.filter and USE_NEW_PARAM_MAPS:
            filter_pattern = args.filter.lower()
            filtered_indices = set()
            
            # Try to get parameter map from any detected servo type
            sample_servo_type = next(iter(servo_types.values())) if servo_types else "RS02"
            try:
                param_map = get_parameter_map(sample_servo_type)
                for param_idx in all_param_indices:
                    if param_idx in param_map:
                        param_name = param_map[param_idx][0].lower()
                        if filter_pattern in param_name:
                            filtered_indices.add(param_idx)
            except:
                filtered_indices = all_param_indices  # fallback to no filtering
                
            print(f"Filtering parameters containing '{args.filter}': {len(filtered_indices)}/{len(all_param_indices)} parameters")
        
        print(f"Found {len(filtered_indices)} parameters to display")
        
        # Sort actuator IDs for consistent column order
        sorted_actuator_ids = sorted(all_parameters.keys())
        
        # Build table data
        table_data = []
        for param_index in sorted(filtered_indices):
            # Get parameter info
            servo_type = servo_types.get(sorted_actuator_ids[0]) if servo_types else None
            
            if USE_NEW_PARAM_MAPS and servo_type:
                try:
                    param_map = get_parameter_map(servo_type)
                    if param_index in param_map:
                        name, param_type, access, min_val, max_val, desc = param_map[param_index]
                    else:
                        name, param_type, access = f"Unknown_{param_index:04X}", "Unknown", "?"
                except:
                    name, param_type, access = f"Unknown_{param_index:04X}", "Unknown", "?"
            else:
                # Fallback to legacy definitions
                if param_index in LEGACY_PARAM_DEFINITIONS:
                    name, param_type, access = LEGACY_PARAM_DEFINITIONS[param_index]  
                else:
                    name, param_type, access = f"Unknown_{param_index:04X}", "Unknown", "?"
            
            row = [f"0x{param_index:04X}", name, param_type, access]
        
            # Add value for each actuator
            for actuator_id in sorted_actuator_ids:
                if param_index in all_parameters[actuator_id]:
                    raw_bytes = bytes(all_parameters[actuator_id][param_index])
                    
                    if args.debug:
                        print(f"\nDecoding parameter 0x{param_index:04X} for actuator {actuator_id}:")
                        print(f"  Raw hex: {raw_bytes.hex().upper()}")
                    
                    actuator_servo_type = servo_types.get(actuator_id)
                    decoded_value = decode_parameter(param_index, raw_bytes, actuator_servo_type)
                    
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
            
            # Show servo types if detected
            if servo_types:
                servo_info = [f"ID_{aid}({servo_types.get(aid, '?')})" for aid in sorted_actuator_ids]
                print(f"Servo types: {', '.join(servo_info)}")
            
            print("=" * 80)
            print(tabulate(table_data, headers=headers, tablefmt="simple", 
                          maxcolwidths=[None, 20, 8, 6] + [15] * len(sorted_actuator_ids)))
        else:  # CSV
            headers = ["Code", "Name", "Type", "Access"] + [f"ID_{aid}" for aid in sorted_actuator_ids]
            print(",".join(headers))
            for row in table_data:
                print(",".join(str(cell) for cell in row))
        
        print(f"\nSummary:")
        for actuator_id in sorted_actuator_ids:
            interface, _ = actuator_locations[actuator_id]
            param_count = len(all_parameters[actuator_id])
            servo_type = servo_types.get(actuator_id, "Unknown")
            print(f"  Actuator {actuator_id} ({interface}): {param_count} parameters, Type: {servo_type}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Robstride CLI - Command line interface for Robstride actuators
"""

import click
import sys
import time
import json
import os
from typing import List, Optional, Dict, Tuple
from robstride_driver import PyRobstrideDriver, PyActuatorCommand, PyRobstrideActuatorType

# Add the parent directory to sys.path so we can import parameter_map  
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parameter_map import get_parameter_map, auto_detect_servo_type, list_all_servo_types
from param_dump import decode_parameter
from tabulate import tabulate

    
def parse_ids(ids_str: str) -> List[int]:
    """Parse comma-separated actuator IDs"""
    if not ids_str:
        return []
    return [int(id.strip()) for id in ids_str.split(',')]


def parse_interfaces(interfaces_str: str) -> List[str]:
    """Parse comma-separated interface names"""
    if not interfaces_str:
        return []
    return [iface.strip() for iface in interfaces_str.split(',')]


def create_driver(interface: str) -> PyRobstrideDriver:
    """Create and connect driver for a single interface"""
    driver = PyRobstrideDriver(interface)
    driver.connect(interface)
    return driver


def detect_servo_type_from_parameters(params: Dict[int, bytes]) -> Optional[str]:
    """Detect servo type from AppCodeVersion parameter (0x1003)"""
    if 0x1003 not in params:
        return None
        
    try:
        version_bytes = params[0x1003]
        
        # Decode string parameter manually 
        parts = version_bytes.split(b'\x00')
        non_empty_parts = [part for part in parts if part]
        
        if len(non_empty_parts) >= 2:
            # Try the second part (type_prefix + value)
            second_part = non_empty_parts[1].decode('utf-8', errors='ignore')
            
            # Extract value after type prefix
            if len(second_part) >= 2 and second_part[0] in 'isvtf':
                version_str = second_part[1:]
                
                # Validate version format (should be "0.X.Y.Z")
                if version_str and len(version_str) >= 5 and version_str[0].isdigit():
                    click.echo(f"  Detected firmware version: {version_str}", err=True)
                    return auto_detect_servo_type(version_str)
                    
    except Exception as e:
        click.echo(f"  Error detecting servo type: {e}", err=True)
    
    return None

# Global cache for discovered actuators
_discovered_actuators: Dict[int, Tuple[PyRobstrideDriver, str]] = {}


def find_and_register_actuator(actuator_id: int, interfaces: List[str]) -> Optional[Tuple[PyRobstrideDriver, str]]:
    """Find and register an actuator on any interface. Returns (driver, interface) or None"""
    
    click.echo(f"Discovering actuator {actuator_id}...", err=True)
    
    for interface in interfaces:
        try:
            driver = create_driver(interface)
            
            # Use scan method to find this specific actuator
            click.echo(f"  Checking {interface}...", err=True)
            actuators = driver.scan_actuators(actuator_id, actuator_id)  # Scan just this ID
            
            if actuator_id in actuators:
                # Found it! Cache and return
                _discovered_actuators[actuator_id] = (driver, interface)
                click.echo(f"Found actuator {actuator_id} on {interface}", err=True)
                return (driver, interface)
                
        except Exception as e:
            click.echo(f"  Error checking {interface}: {e}", err=True)
            continue
    
    click.echo(f"Failed to find actuator {actuator_id} on any interface", err=True)
    return None


def get_actuator_driver(actuator_id: int, interfaces: List[str]) -> Optional[Tuple[PyRobstrideDriver, str]]:
    """Get driver for an actuator, discovering it if necessary"""
    return find_and_register_actuator(actuator_id, interfaces)


@click.group()
@click.option('--interface', '-i', 
              default='can0,can1,can2,can3,can4', 
              help='CAN interface(s) to use - comma separated (default: can0,can1,can2,can3,can4)')
@click.pass_context
def cli(ctx, interface):
    """Robstride actuator command line interface"""
    ctx.ensure_object(dict)
    ctx.obj['interfaces'] = parse_interfaces(interface)


@cli.command()
@click.option('--ids', required=True, help='Comma-separated actuator IDs (e.g., 11,12,13)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def state(ctx, ids, output_format):
    """Get current state of actuators"""
    interfaces = ctx.obj['interfaces']
    actuator_ids = parse_ids(ids)
    
    states = {}
    for actuator_id in actuator_ids:
        result = get_actuator_driver(actuator_id, interfaces)
        if result:
            driver, interface = result
            try:
                state = driver.get_actuator_state(actuator_id)
                states[actuator_id] = {
                    'position': state.position,
                    'velocity': state.velocity,
                    'torque': state.torque,
                    'temperature': state.temperature,
                    'faults': f"0x{state.faults:04x}",
                    'kp': state.kp,
                    'kd': state.kd,
                    'interface': interface
                }
            except Exception as e:
                states[actuator_id] = {'error': str(e)}
        else:
            states[actuator_id] = {'error': f'Not found on any interface ({", ".join(interfaces)})'}
    
    if output_format == 'json':
        click.echo(json.dumps(states, indent=2))
    else:
        # Table format
        click.echo("Actuator States:")
        click.echo("-" * 90)
        for actuator_id, state in states.items():
            if 'error' in state:
                click.echo(f"Actuator {actuator_id:2d}: Error - {state['error']}")
            else:
                click.echo(f"Actuator {actuator_id:2d} ({state['interface']}): pos={state['position']:6.3f} vel={state['velocity']:6.3f} "
                         f"torque={state['torque']:6.3f} temp={state['temperature']:5.1f}°C "
                         f"faults={state['faults']} kp={state['kp']:4.1f} kd={state['kd']:4.1f}")


@cli.command()
@click.option('--ids', required=True, help='Comma-separated actuator IDs (e.g., 11,12,13)')
@click.pass_context
def enable(ctx, ids):
    """Enable actuators for operation"""
    interfaces = ctx.obj['interfaces']
    actuator_ids = parse_ids(ids)
    
    click.echo(f"Enabling actuators: {actuator_ids}")
    success_count = 0
    
    for actuator_id in actuator_ids:
        result = get_actuator_driver(actuator_id, interfaces)
        if result:
            driver, interface = result
            try:
                driver.enable_actuator(actuator_id)
                click.echo(f"Actuator {actuator_id} enabled on {interface}")
                success_count += 1
            except Exception as e:
                click.echo(f"Actuator {actuator_id} enable failed: {e}")
        else:
            click.echo(f"Actuator {actuator_id} not found on any interface")
    
    click.echo(f"Enabled {success_count}/{len(actuator_ids)} actuators")


@cli.command()
@click.option('--ids', required=True, help='Comma-separated actuator IDs (e.g., 11,12,13)')
@click.pass_context
def disable(ctx, ids):
    """Disable actuators (set zero torque and gains)"""
    interfaces = ctx.obj['interfaces']
    actuator_ids = parse_ids(ids)
    
    click.echo(f"Disabling actuators: {actuator_ids}")
    success_count = 0
    
    for actuator_id in actuator_ids:
        result = get_actuator_driver(actuator_id, interfaces)
        if result:
            driver, interface = result
            try:
                driver.disable_actuator(actuator_id)
                click.echo(f"Actuator {actuator_id} disabled on {interface}")
                success_count += 1
            except Exception as e:
                click.echo(f"Actuator {actuator_id} disable failed: {e}")
        else:
            click.echo(f"Actuator {actuator_id} not found on any interface")
    
    click.echo(f"Disabled {success_count}/{len(actuator_ids)} actuators")


@cli.command()
@click.option('--ids', required=True, help='Comma-separated actuator IDs (e.g., 11,12,13)')
@click.option('--pos', type=float, help='Target position in radians')
@click.option('--vel', type=float, help='Target velocity in rad/s')
@click.option('--torque', type=float, help='Target torque in Nm')
@click.option('--kp', type=float, default=50.0, help='Position gain (default: 50.0)')
@click.option('--kd', type=float, default=2.0, help='Velocity gain (default: 2.0)')
@click.pass_context
def move(ctx, ids, pos, vel, torque, kp, kd):
    """Send movement commands to actuators"""
    interfaces = ctx.obj['interfaces']
    actuator_ids = parse_ids(ids)
    
    # Validate that at least one target is specified
    if pos is None and vel is None and torque is None:
        click.echo("Error: Must specify at least one of --pos, --vel, or --torque", err=True)
        sys.exit(1)
    
    # Create command
    command = PyActuatorCommand(
        position=pos or 0.0,
        velocity=vel or 0.0,
        torque=torque or 0.0,
        kp=kp if pos is not None else 0.0,
        kd=kd if (pos is not None or vel is not None) else 0.0
    )
    
    cmd_desc = []
    if pos is not None:
        cmd_desc.append(f"pos={pos:.3f}")
    if vel is not None:
        cmd_desc.append(f"vel={vel:.3f}")
    if torque is not None:
        cmd_desc.append(f"torque={torque:.3f}")
    
    click.echo(f"Moving actuators {actuator_ids} to {', '.join(cmd_desc)} (kp={kp}, kd={kd})")
    
    success_count = 0
    for actuator_id in actuator_ids:
        result = get_actuator_driver(actuator_id, interfaces)
        if result:
            driver, interface = result
            try:
                driver.send_command(actuator_id, command)
                click.echo(f"Command sent to actuator {actuator_id} on {interface}")
                success_count += 1
            except Exception as e:
                click.echo(f"Actuator {actuator_id} command failed: {e}")
        else:
            click.echo(f"Actuator {actuator_id} not found on any interface")
    
    click.echo(f"Commands sent to {success_count}/{len(actuator_ids)} actuators")


@cli.command()
@click.option('--start-id', type=int, default=10, help='Start of scan range (default: 10)')
@click.option('--end-id', type=int, default=50, help='End of scan range (default: 50)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def scan(ctx, start_id, end_id, output_format):
    """Scan for actuators on all CAN interfaces"""
    interfaces = ctx.obj['interfaces']
    
    all_actuators = {}
    total_found = 0
    
    for interface in interfaces:
        try:
            driver = create_driver(interface)
            click.echo(f"Scanning {interface} (IDs {start_id}-{end_id})...")
            actuators = driver.scan_actuators(start_id, end_id)
            
            if actuators:
                all_actuators[interface] = actuators
                total_found += len(actuators)
                
                # Cache discovered actuators
                for actuator_id in actuators:
                    _discovered_actuators[actuator_id] = (driver, interface)
                
                if output_format == 'table':
                    click.echo(f"  Found {len(actuators)} actuators: {actuators}")
            elif output_format == 'table':
                click.echo(f"  No actuators found")
                
        except Exception as e:
            if output_format == 'table':
                click.echo(f"  Error scanning {interface}: {e}")
    
    if output_format == 'json':
        click.echo(json.dumps(all_actuators, indent=2))
    else:
        click.echo(f"\nScan complete: Found {total_found} total actuators across {len(all_actuators)} interfaces")
        if not all_actuators:
            click.echo("Make sure CAN interfaces are up: sudo ip link set can0 up")


@cli.command()
@click.option('--ids', required=True, help='Comma-separated actuator IDs (e.g., 11,12,13)')
@click.option('--param', type=int, help='Specific parameter index to dump (hex, e.g., 0x2000)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'raw']), default='table', help='Output format')
@click.option('--filter', type=str, help='Filter parameters by name pattern (case-insensitive)')
@click.pass_context
def dump(ctx, ids, param, output_format, filter):
    """Dump parameters from actuators with proper decoding"""
    interfaces = ctx.obj['interfaces']
    actuator_ids = parse_ids(ids)
    
    # Collect parameters from all actuators
    all_parameters = {}  # {actuator_id: {param_index: raw_bytes}}
    actuator_interfaces = {}  # {actuator_id: interface}
    servo_types = {}  # {actuator_id: servo_type}
    
    for actuator_id in actuator_ids:
        result = get_actuator_driver(actuator_id, interfaces)
        if result:
            driver, interface = result
            actuator_interfaces[actuator_id] = interface
            
            try:
                if param is not None:
                    # Dump specific parameter
                    click.echo(f"Reading parameter 0x{param:04x} from actuator {actuator_id} on {interface}...")
                    data = driver.read_raw_parameter(actuator_id, param)
                    if data:
                        all_parameters[actuator_id] = {param: data}
                    else:
                        click.echo(f"No data received for parameter 0x{param:04x}")
                        all_parameters[actuator_id] = {}
                else:
                    # Dump all parameters
                    click.echo(f"Reading all parameters from actuator {actuator_id} on {interface}...")
                    params = driver.dump_all_parameters(actuator_id)
                    if params:
                        all_parameters[actuator_id] = {idx: bytes(data) for idx, data in params.items()}
                        click.echo(f"  Retrieved {len(params)} parameters")
                        
                        # Auto-detect servo type from firmware version
                        servo_type = detect_servo_type_from_parameters(all_parameters[actuator_id])
                        if servo_type:
                            servo_types[actuator_id] = servo_type
                            click.echo(f"  Auto-detected servo type: {servo_type}", err=True)
                
            except Exception as e:
                click.echo(f"Error reading parameters from actuator {actuator_id}: {e}")
                all_parameters[actuator_id] = {}
        else:
            click.echo(f"Actuator {actuator_id} not found on any interface")
    
    # Filter out actuators with no parameters
    valid_actuators = {aid: params for aid, params in all_parameters.items() if params}
    
    if not valid_actuators:
        click.echo("No parameters retrieved from any actuators")
        return
    
    # Display results based on format
    if output_format == 'raw':
        display_parameters_raw(valid_actuators, actuator_interfaces)
    elif output_format == 'json':
        display_parameters_json(valid_actuators, actuator_interfaces, servo_types)
    else:  # table
        if any(servo_types.values()):
            display_parameters_table(valid_actuators, actuator_interfaces, servo_types, filter, param)



@cli.command()
@click.option('--ids', required=True, help='Comma-separated actuator IDs (e.g., 11,12,13)')
@click.option('--amplitude', type=float, default=0.5, help='Sine wave amplitude in radians (default: 0.5)')
@click.option('--frequency', type=float, default=1.0, help='Sine wave frequency in Hz (default: 1.0)')
@click.option('--duration', type=float, default=5.0, help='Test duration in seconds (default: 5.0)')
@click.option('--kp', type=float, default=100.0, help='Position gain (default: 100.0)')
@click.option('--kd', type=float, default=5.0, help='Velocity gain (default: 5.0)')
@click.pass_context
def sine_test(ctx, ids, amplitude, frequency, duration, kp, kd):
    """Run a sine wave position test"""
    import math
    
    interfaces = ctx.obj['interfaces']
    actuator_ids = parse_ids(ids)
    
    # Find actuators and their drivers
    actuator_drivers = {}
    for actuator_id in actuator_ids:
        result = get_actuator_driver(actuator_id, interfaces)
        if result:
            driver, interface = result
            actuator_drivers[actuator_id] = (driver, interface)
            click.echo(f"Found actuator {actuator_id} on {interface}")
        else:
            click.echo(f"Warning: Actuator {actuator_id} not found on any interface")
    
    if not actuator_drivers:
        click.echo("No actuators found. Exiting.")
        return
    
    click.echo(f"Running sine wave test on {len(actuator_drivers)} actuators")
    click.echo(f"Amplitude: {amplitude:.3f} rad, Frequency: {frequency:.1f} Hz, Duration: {duration:.1f}s")
    click.echo("Press Ctrl+C to stop early")
    
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            t = time.time() - start_time
            target_pos = amplitude * math.sin(2 * math.pi * frequency * t)
            
            # Send commands
            command = PyActuatorCommand(position=target_pos, kp=kp, kd=kd)
            for actuator_id, (driver, interface) in actuator_drivers.items():
                try:
                    driver.send_command(actuator_id, command)
                except Exception as e:
                    click.echo(f"Command error for actuator {actuator_id} on {interface}: {e}")
            
            # Print status every second
            if int(t) != int(t - 0.01):
                click.echo(f"t={t:.1f}s: target={target_pos:.3f} rad")
            
            time.sleep(0.01)  # 100 Hz
            
    except KeyboardInterrupt:
        click.echo("\nSine test interrupted")
    
    # Stop all actuators
    click.echo("Stopping actuators...")
    for actuator_id, (driver, interface) in actuator_drivers.items():
        try:
            driver.disable_actuator(actuator_id)
        except Exception as e:
            click.echo(f"Stop error for actuator {actuator_id} on {interface}: {e}")
    
    click.echo("Sine test completed")


def display_parameters_table(all_parameters, actuator_interfaces, servo_types, name_filter, single_param):
    """Display parameters using parameter maps with tabulate"""
    
    # Get all unique parameter indices, filtered by known parameters
    all_param_indices = set()
    for actuator_id, params in all_parameters.items():
        servo_type = servo_types.get(actuator_id)
        if servo_type:
            param_map = get_parameter_map(servo_type)
            known_params = {idx for idx in params.keys() if idx in param_map}
            all_param_indices.update(known_params)
        else:
            all_param_indices.update(params.keys())
    
    # Apply name filter
    filtered_indices = all_param_indices
    if name_filter:
        filter_pattern = name_filter.lower()
        filtered_indices = set()
        
        for actuator_id in all_parameters.keys():
            servo_type = servo_types.get(actuator_id)
            if servo_type:
                param_map = get_parameter_map(servo_type)
                for param_idx in all_param_indices:
                    if param_idx in param_map:
                        name = param_map[param_idx][0].lower()
                        desc = param_map[param_idx][5].lower()
                        if filter_pattern in name or filter_pattern in desc:
                            filtered_indices.add(param_idx)
        
        click.echo(f"Filtering parameters containing '{name_filter}': {len(filtered_indices)}/{len(all_param_indices)} parameters")
    
    # Build table data
    sorted_actuator_ids = sorted(all_parameters.keys())
    table_data = []
    
    for param_index in sorted(filtered_indices):
        # Get parameter info from first actuator with detected servo type
        param_type = "unknown"
        access_mode = "?"
        description = f"Unknown parameter 0x{param_index:04X}"
        
        for actuator_id in sorted_actuator_ids:
            servo_type = servo_types.get(actuator_id)
            if servo_type:
                param_map = get_parameter_map(servo_type)
                if param_index in param_map:
                    name, dtype, access, min_val, max_val, desc = param_map[param_index]
                    param_type = dtype
                    access_mode = access
                    description = desc
                    break
        
        row = [f"0x{param_index:04X}", description, param_type, access_mode]
        
        # Add decoded values for each actuator
        for actuator_id in sorted_actuator_ids:
            if param_index in all_parameters[actuator_id]:
                raw_bytes = all_parameters[actuator_id][param_index]
                servo_type = servo_types.get(actuator_id)
                
                if servo_type:
                    decoded_value = decode_parameter(param_index, raw_bytes, servo_type)
                else:
                    decoded_value = raw_bytes.hex().upper()
                
                row.append(decoded_value)
            else:
                row.append("N/A")
        
        table_data.append(row)
    
    # Display with servo type info
    headers = ["Code", "Description", "Type", "Access"] + [f"ID_{aid}" for aid in sorted_actuator_ids]
    
    servo_info = [f"ID_{aid}({servo_types.get(aid, '?')})" for aid in sorted_actuator_ids]
    click.echo(f"Servo types: {', '.join(servo_info)}")
    click.echo(f"Found {len(sorted_actuator_ids)} actuators with {len(filtered_indices)} parameters")
    click.echo("=" * 80)
    
    click.echo(tabulate(table_data, headers=headers, tablefmt="simple", 
                      maxcolwidths=[None, 40, 8, 6] + [15] * len(sorted_actuator_ids)))


def display_parameters_raw(all_parameters, actuator_interfaces):
    """Display raw hex parameter data"""
    for actuator_id, params in all_parameters.items():
        interface = actuator_interfaces[actuator_id]
        click.echo(f"\nActuator {actuator_id} ({interface}):")
        for param_idx, raw_bytes in sorted(params.items()):
            click.echo(f"  0x{param_idx:04X}: {raw_bytes.hex().upper()}")


def display_parameters_json(all_parameters, actuator_interfaces, servo_types):
    """Display parameters in JSON format"""
    result = {}
    for actuator_id, params in all_parameters.items():
        result[actuator_id] = {
            'interface': actuator_interfaces[actuator_id],
            'servo_type': servo_types.get(actuator_id, 'unknown'),
            'parameters': {}
        }
        
        for param_idx, raw_bytes in params.items():
            servo_type = servo_types.get(actuator_id)
            if servo_type:
                try:
                    param_map = get_parameter_map(servo_type)
                    if param_idx in param_map:
                        name, param_type, access, min_val, max_val, desc = param_map[param_idx]
                        decoded = decode_parameter(param_idx, raw_bytes, servo_type)
                        result[actuator_id]['parameters'][f"0x{param_idx:04X}"] = {
                            'name': name,
                            'type': param_type,
                            'access': access,
                            'description': desc,
                            'min_value': min_val,
                            'max_value': max_val,
                            'value': decoded,
                            'raw_hex': raw_bytes.hex().upper()
                        }
                        continue
                except:
                    pass
            
            # Fallback to raw display
            result[actuator_id]['parameters'][f"0x{param_idx:04X}"] = {
                'description': 'Unknown parameter',
                'raw_hex': raw_bytes.hex().upper()
            }
    
    click.echo(json.dumps(result, indent=2))


if __name__ == '__main__':
    cli()
#!/usr/bin/env python3
"""
Robstride Actuator Scanner

Scans multiple CAN interfaces for Robstride actuators, similar to the Rust example.
"""

import sys
try:
    import robstride_driver
except ImportError:
    print("Error: robstride_driver module not found.")
    print("Please build and install the Python bindings first:")
    print("  pip install maturin")
    print("  maturin develop --features python")
    sys.exit(1)

import argparse
from tabulate import tabulate

def main():
    parser = argparse.ArgumentParser(description='Scan for Robstride actuators on multiple CAN interfaces')
    parser.add_argument('--interfaces', '-i', nargs='+', 
                        default=['can0', 'can1', 'can2', 'can3', 'can4'],
                        help='CAN interfaces to scan (default: can0 can1 can2 can3 can4)')
    parser.add_argument('--start-id', type=int, default=10, 
                        help='Start of actuator ID range (default: 10)')
    parser.add_argument('--end-id', type=int, default=50,
                        help='End of actuator ID range (default: 50)')
    parser.add_argument('--format', choices=['table', 'simple'], default='table',
                        help='Output format (default: table)')
    
    args = parser.parse_args()
    
    print(f"Scanning for Robstride actuators")
    print(f"Interfaces: {', '.join(args.interfaces)}")
    print(f"ID range: {args.start_id}-{args.end_id}")
    print()
    
    try:
        # Scan multiple interfaces
        print("Scanning...")
        discovered = robstride_driver.PyRobstrideDriver.scan_multiple_interfaces(
            args.interfaces, args.start_id, args.end_id
        )
        
        if not discovered:
            print("No actuators found on any interface")
            print()
            print("Make sure CAN interfaces are up:")
            for interface in args.interfaces:
                print(f"  sudo ip link set {interface} up")
            return 1
        
        # Display results
        if args.format == 'table':
            table_data = []
            total_actuators = 0
            
            for interface in sorted(discovered.keys()):
                actuators = discovered[interface]
                actuator_count = len(actuators)
                total_actuators += actuator_count
                
                actuators_str = ', '.join([str(id) for id in sorted(actuators)])
                table_data.append([interface, actuator_count, actuators_str])
            
            headers = ["Interface", "Count", "Actuator IDs"]
            print("Discovered actuators:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print(f"\nTotal: {total_actuators} actuators")
            
        else:  # simple format
            print("Discovered actuators:")
            total_actuators = 0
            for interface, actuators in sorted(discovered.items()):
                actuator_count = len(actuators)
                total_actuators += actuator_count
                print(f"  {interface}: {actuator_count} actuators - {sorted(actuators)}")
            print(f"\nTotal: {total_actuators} actuators")
        
        # Return success if actuators found
        return 0
        
    except Exception as e:
        print(f"Error during scan: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
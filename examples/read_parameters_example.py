#!/usr/bin/env python3
"""
Example demonstrating the new single parameter read CLI functionality
"""

import subprocess
import sys

def run_read_command():
    """Run the robstride read command with example parameters"""
    
    # Example 1: Read default parameters from actuator 11
    print("=== Reading default parameters from actuator 11 ===")
    result = subprocess.run([
        sys.executable, "-m", "robstride_driver.cli", 
        "read", "--ids", "11"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error: {result.stderr}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Read specific parameters from multiple actuators
    print("=== Reading specific parameters from actuators 11,12 ===")
    result = subprocess.run([
        sys.executable, "-m", "robstride_driver.cli", 
        "read", "--ids", "11,12", "--params", "0x7005,0x7019,0x701C,0x700B"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error: {result.stderr}")

if __name__ == "__main__":
    run_read_command()

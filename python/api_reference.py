#!/usr/bin/env python3
"""
API Reference for robstride-driver Python bindings
"""

from robstride_driver import PyRobstrideDriver, PyActuatorCommand, PyRobstrideActuatorType

# ============================================================================
# Driver Setup
# ============================================================================

# Create and connect driver
driver = PyRobstrideDriver("can4")
driver.connect("can4")

# Scan for actuators
actuators = driver.scan_actuators(start_id=10, end_id=50)  # Returns list of CAN IDs

# Add specific actuator (if you know the type)  
driver.add_actuator(can_id=31, actuator_type=PyRobstrideActuatorType.Robstride04)

# Enable actuator for operation
driver.enable_actuator(actuator_id=31)

# ============================================================================
# Getting Actuator State
# ============================================================================

# Get current actuator state
state = driver.get_actuator_state(actuator_id=31)

# Access state properties (all read-only)
print(f"Position: {state.position} rad")      # Current position in radians
print(f"Velocity: {state.velocity} rad/s")    # Current velocity in rad/s  
print(f"Torque: {state.torque} Nm")          # Current torque in Nm
print(f"Temperature: {state.temperature} °C") # Current temperature
print(f"Faults: 0x{state.faults:x}")         # Fault flags (hex)


# ============================================================================
# Sending Commands  
# ============================================================================

# Method 1: Convenience methods
#driver.set_position(actuator_id=21, position=1.0, kp=50.0, kd=2.0)
#driver.set_velocity(actuator_id=21, velocity=2.0, kd=3.0)  
#driver.set_torque(actuator_id=21, torque=0.5)

# Method 2: Full command object
command = PyActuatorCommand(
    position=-0.5,   # Target position (radians)
    velocity=0.0,   # Target velocity (rad/s)
    torque=0.0,     # Feedforward torque (Nm)
    kp=50.0,        # Position gain
    kd=0.5          # Velocity gain  
)
driver.send_command(actuator_id=31, command=command)

exit(0)

# Method 3: Create command step by step
command = PyActuatorCommand()
command.position = 0.2
command.kp = 5.0
command.kd = 0.5
driver.send_command(actuator_id=31, command=command)

# ============================================================================
# Utility Methods
# ============================================================================

# Check what actuators are registered
registered = driver.get_registered_actuators()  # Returns list of CAN IDs

# Check if specific actuator is registered
if driver.has_actuator(actuator_id=31):
    print("Actuator 21 is registered")

# ============================================================================
# Actuator Types
# ============================================================================

# Available actuator types:
PyRobstrideActuatorType.Robstride00
PyRobstrideActuatorType.Robstride01  
PyRobstrideActuatorType.Robstride02
PyRobstrideActuatorType.Robstride03
PyRobstrideActuatorType.Robstride04

# ============================================================================
# Error Handling
# ============================================================================

try:
    state = driver.get_actuator_state(999)  # Non-existent actuator
except RuntimeError as e:
    print(f"Error: {e}")

# ============================================================================
# Control Loop Example
# ============================================================================

#import time
#import math

# Real-time control at 100 Hz
#`start_time = time.time()
#while time.time() - start_time < 10.0:  # Run for 10 seconds
#    t = time.time() - start_time
    
    # Sine wave position reference
    #target_pos = math.sin(t) * 0.5
    
    # Send command
    #driver.set_position(actuator_id=31, position=target_pos, kp=100.0, kd=5.0)
    
    # Optional: Read feedback
    #if int(t * 10) % 10 == 0:  # Print every 1 second
    #    state = driver.get_actuator_state(actuator_id=31)
    #    error = target_pos - state.position
    #    print(f"t={t:.1f}: target={target_pos:.3f}, actual={state.position:.3f}, error={error:.3f}")
    
    #time.sleep(0.01)  # 100 Hz
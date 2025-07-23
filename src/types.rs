//! Core types for actuator control
//!
//! Extracted from firmware/src/robot_description.rs

#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct ActuatorCommand {
    pub qpos: f64, // Position (radians)
    pub qvel: f64, // Velocity (rad/s)
    pub qfrc: f64, // Force/Torque (Nm)
    pub kp: f64,   // Position gain
    pub kd: f64,   // Velocity gain
}

#[derive(Debug, Default)]
pub struct ActuatorFeedback {
    pub qpos: f64,   // Position
    pub qvel: f64,   // Velocity
    pub qfrc: f64,   // Force
    pub kp: f64,     // Position gain
    pub kd: f64,     // Velocity gain
    pub temp: f64,   // Temperature
    pub faults: u32, // Fault flags
}

pub struct ActuatorFeedbackUpdate {
    pub qpos: Option<f64>,
    pub qvel: Option<f64>,
    pub qfrc: Option<f64>,
    pub kp: Option<f64>,
    pub kd: Option<f64>,
    pub temp: Option<f64>,
    pub faults: Option<u32>,
}

impl ActuatorFeedback {
    pub fn merge(&mut self, update: ActuatorFeedbackUpdate) {
        if let Some(qpos) = update.qpos {
            self.qpos = qpos;
        }
        if let Some(qvel) = update.qvel {
            self.qvel = qvel;
        }
        if let Some(qfrc) = update.qfrc { 
            self.qfrc = qfrc;
        }
        if let Some(kp) = update.kp {
            self.kp = kp;
        }
        if let Some(kd) = update.kd {
            self.kd = kd;
        }
        if let Some(temp) = update.temp {
            self.temp = temp;
        }
        if let Some(faults) = update.faults {
            self.faults = faults;
        }
    }
}

#[derive(Debug, Default)]
pub struct ActuatorState {
    pub feedback: ActuatorFeedback,
    pub command: ActuatorCommand,
}

impl ActuatorState {
    pub fn merge_feedback(&mut self, update: ActuatorFeedbackUpdate) {
        self.feedback.merge(update);
    }

    pub fn set_command(&mut self, command: ActuatorCommand) {
        self.command = command;
    }
}

// For convenience - same as ActuatorCommand but with clearer naming for external API
pub type ActuatorConfig = ActuatorCommand;

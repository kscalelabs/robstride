//! # Robstride Driver
//!
//! Robstride servo driver ( CAN-based communication ).
//! Provides an interface for controlling, inspecting and troubelshooting Robstride actuators.
mod actuator_types;
mod can;
mod client;
mod driver;
mod error;
mod protocol;
mod types;
mod parameters;

#[cfg(feature = "python")]
pub mod python_bindings;


pub use crate::driver::RobstrideDriver;
pub use crate::error::{Result, RobstrideError};
pub use crate::types::{ActuatorCommand, ActuatorState};
pub use crate::actuator_types::{RobstrideActuatorType};

#[cfg(feature = "python")]
pub use python_bindings::*;



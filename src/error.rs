use thiserror::Error;

pub type Result<T> = std::result::Result<T, RobstrideError>;

#[derive(Error, Debug)]
pub enum RobstrideError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("CAN interface error: {0}")]
    Can(String),

    #[error("Protocol error: {0}")]
    Protocol(String),

    #[error("Actuator not found: {0}")]
    ActuatorNotFound(u8),

    #[error("Invalid actuator type for CAN ID: {0}")]
    InvalidActuatorType(u8),

    #[error("Timeout waiting for response")]
    Timeout,

    #[error("Communication error: {0}")]
    Communication(String),
}

impl From<tokio::time::error::Elapsed> for RobstrideError {
    fn from(_: tokio::time::error::Elapsed) -> Self {
        RobstrideError::Timeout
    }
}

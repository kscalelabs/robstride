//! Python bindings for robstride-driver

#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
use crate::{RobstrideDriver, RobstrideError, ActuatorCommand, ActuatorState, RobstrideActuatorType};
#[cfg(feature = "python")]
use std::collections::HashMap;

#[cfg(feature = "python")]
#[pyclass]
#[derive(Debug, Clone)]
pub struct PyActuatorCommand {
    #[pyo3(get, set)]
    pub position: f64,
    #[pyo3(get, set)]
    pub velocity: f64,
    #[pyo3(get, set)]
    pub torque: f64,
    #[pyo3(get, set)]
    pub kp: f64,
    #[pyo3(get, set)]
    pub kd: f64,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyActuatorCommand {
    #[new]
    fn new(position: Option<f64>, velocity: Option<f64>, torque: Option<f64>, 
           kp: Option<f64>, kd: Option<f64>) -> Self {
        Self {
            position: position.unwrap_or(0.0),
            velocity: velocity.unwrap_or(0.0),
            torque: torque.unwrap_or(0.0),
            kp: kp.unwrap_or(0.0),
            kd: kd.unwrap_or(0.0),
        }
    }

    fn __repr__(&self) -> String {
        format!("ActuatorCommand(pos={:.3}, vel={:.3}, torque={:.3}, kp={:.1}, kd={:.1})", 
                self.position, self.velocity, self.torque, self.kp, self.kd)
    }
}

#[cfg(feature = "python")]
impl From<PyActuatorCommand> for ActuatorCommand {
    fn from(cmd: PyActuatorCommand) -> Self {
        ActuatorCommand {
            qpos: cmd.position,
            qvel: cmd.velocity,
            qfrc: cmd.torque,
            kp: cmd.kp,
            kd: cmd.kd,
        }
    }
}

#[cfg(feature = "python")]
#[pyclass]
#[derive(Debug, Clone)]
pub struct PyActuatorState {
    #[pyo3(get)]
    pub position: f64,
    #[pyo3(get)]
    pub velocity: f64,
    #[pyo3(get)]
    pub torque: f64,
    #[pyo3(get)]
    pub temperature: f64,
    #[pyo3(get)]
    pub faults: u32,
    #[pyo3(get)]
    pub kp: f64,
    #[pyo3(get)]
    pub kd: f64,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyActuatorState {
    fn __repr__(&self) -> String {
        format!("ActuatorState(pos={:.3}, vel={:.3}, torque={:.3}, temp={:.1}°C, faults=0x{:x})", 
                self.position, self.velocity, self.torque, self.temperature, self.faults)
    }
}

#[cfg(feature = "python")]
impl From<ActuatorState> for PyActuatorState {
    fn from(state: ActuatorState) -> Self {
        Self {
            position: state.feedback.qpos,
            velocity: state.feedback.qvel,
            torque: state.feedback.qfrc,
            temperature: state.feedback.temp,
            faults: state.feedback.faults,
            kp: state.feedback.kp,
            kd: state.feedback.kd,
        }
    }
}

#[cfg(feature = "python")]
#[pyclass]
#[derive(Debug, Clone, Copy)]
pub enum PyRobstrideActuatorType {
    Robstride00,
    Robstride01,
    Robstride02,
    Robstride03,
    Robstride04,
}

#[cfg(feature = "python")]
impl From<PyRobstrideActuatorType> for RobstrideActuatorType {
    fn from(py_type: PyRobstrideActuatorType) -> Self {
        match py_type {
            PyRobstrideActuatorType::Robstride00 => RobstrideActuatorType::Robstride00,
            PyRobstrideActuatorType::Robstride01 => RobstrideActuatorType::Robstride01,
            PyRobstrideActuatorType::Robstride02 => RobstrideActuatorType::Robstride02,
            PyRobstrideActuatorType::Robstride03 => RobstrideActuatorType::Robstride03,
            PyRobstrideActuatorType::Robstride04 => RobstrideActuatorType::Robstride04,
        }
    }
}


#[cfg(feature = "python")]
#[pyclass]
pub struct PyRobstrideDriver {
    driver: Option<RobstrideDriver>,
    rt: tokio::runtime::Runtime,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyRobstrideDriver {
    #[new]
    fn new(interface_name: String) -> PyResult<Self> {
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
            
        Ok(PyRobstrideDriver {
            driver: None,
            rt,
        })
    }
    
    fn connect(&mut self, interface_name: String) -> PyResult<()> {
        let driver = self.rt.block_on(async {
            RobstrideDriver::new(&interface_name).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        self.driver = Some(driver);
        Ok(())
    }
    
    fn scan_actuators(&mut self, start_id: u8, end_id: u8) -> PyResult<Vec<u8>> {
        let driver = self.driver.as_mut()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        let result = self.rt.block_on(async {
            driver.scan_actuators(start_id..=end_id).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        Ok(result)
    }

    fn add_actuator(&mut self, can_id: u8, actuator_type: PyRobstrideActuatorType) -> PyResult<()> {
        let driver = self.driver.as_mut()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        driver.add_actuator(can_id, actuator_type.into());
        
        // Also ping the actuator to establish connection
        let result = self.rt.block_on(async {
            driver.ping_actuator(can_id, actuator_type.into()).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        if !result {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to ping actuator {}", can_id)
            ));
        }
        
        Ok(())
    }

    /// Enable an actuator for operation
    fn enable_actuator(&mut self, actuator_id: u8) -> PyResult<()> {
        let driver = self.driver.as_mut()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        self.rt.block_on(async {
            driver.enable_actuator(actuator_id).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        Ok(())
    }

    /// Zero position an actuator (set current position as zero)
    fn zero_actuator(&mut self, actuator_id: u8) -> PyResult<()> {
        let driver = self.driver.as_mut()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        self.rt.block_on(async {
            driver.zero_actuator(actuator_id).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        Ok(())
    }

    /// Get current state of an actuator
    fn get_actuator_state(&mut self, actuator_id: u8) -> PyResult<PyActuatorState> {
        let driver = self.driver.as_mut()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        let state = self.rt.block_on(async {
            driver.get_actuator_state(actuator_id).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        Ok(PyActuatorState::from(state))
    }

    /// Send a command to an actuator  
    fn send_command(&mut self, actuator_id: u8, command: PyActuatorCommand) -> PyResult<()> {
        let driver = self.driver.as_mut()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        self.rt.block_on(async {
            driver.move_actuator(actuator_id, command.into()).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        Ok(())
    }

    /// Get list of registered actuators
    fn get_registered_actuators(&self) -> PyResult<Vec<u8>> {
        let driver = self.driver.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        Ok(driver.get_registered_actuators())
    }

    /// Check if actuator is registered
    fn has_actuator(&self, actuator_id: u8) -> PyResult<bool> {
        let driver = self.driver.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        Ok(driver.has_actuator(actuator_id))
    }

    /// Read raw parameter data from actuator
    fn read_raw_parameter(&mut self, actuator_id: u8, param_index: u16) -> PyResult<Option<Vec<u8>>> {
        let driver = self.driver.as_mut()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        let result = self.rt.block_on(async {
            driver.read_raw_parameter(actuator_id, param_index).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        Ok(result)
    }
    
    /// Dump all parameters from actuator (returns raw data)
    fn dump_all_parameters(&mut self, actuator_id: u8) -> PyResult<HashMap<u16, Vec<u8>>> {
        let driver = self.driver.as_mut()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Not connected"))?;
            
        let result = self.rt.block_on(async {
            driver.dump_all_parameters(actuator_id).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        Ok(result)
    }
        

    /// Scan multiple CAN interfaces for actuators (static method)
    #[staticmethod]
    fn scan_multiple_interfaces(interfaces: Vec<String>, start_id: u8, end_id: u8) -> PyResult<HashMap<String, Vec<u8>>> {
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
            
        let interface_strs: Vec<&str> = interfaces.iter().map(|s| s.as_str()).collect();
        
        let result = rt.block_on(async {
            RobstrideDriver::scan_multiple_interfaces(&interface_strs, start_id..=end_id).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        Ok(result)
    }
    
}

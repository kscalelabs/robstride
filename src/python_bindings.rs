//! Python bindings for robstride-driver

#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
use crate::{RobstrideDriver, RobstrideError};
#[cfg(feature = "python")]
use std::collections::HashMap;


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

/// Python module
#[cfg(feature = "python")]
#[pymodule]
fn robstride_driver(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyRobstrideDriver>()?;
    Ok(())
}

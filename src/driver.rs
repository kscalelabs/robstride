//! High-level Robstride driver interface - robot agnostic

use crate::actuator_types::RobstrideActuatorType;
use crate::can::CanInterface;
use crate::client::ActuatorClient;
use crate::protocol::ActuatorRequestParams;
use crate::types::{ActuatorCommand, ActuatorState};
use crate::parameters::{ParameterInfo, ParameterValue, get_parameter_table};
use std::collections::HashMap;
use std::time::Duration;
use tokio::time::timeout;

pub struct RobstrideDriver {
    can_interface: CanInterface,
    clients: HashMap<u8, ActuatorClient>,
}

impl RobstrideDriver {
    pub async fn new(interface_name: &str) -> crate::Result<Self> {
        let can_interface = CanInterface::new(interface_name)?;
        Ok(RobstrideDriver {
            can_interface,
            clients: HashMap::new(),
        })
    }

    /// Add an actuator with explicit CAN ID and type
    /// The caller is responsible for knowing which actuator type corresponds to which CAN ID
    pub fn add_actuator(&mut self, can_id: u8, actuator_type: RobstrideActuatorType) {
        let client = ActuatorClient::new(can_id, actuator_type);
        self.clients.insert(can_id, client);
    }

    /// Scan for actuators on the current interface
    pub async fn scan_actuators(
        &mut self,
        id_range: std::ops::RangeInclusive<u8>,
    ) -> crate::Result<Vec<u8>> {
        let mut discovered = Vec::new();

        for can_id in id_range {
            if self.ping_actuator_raw(can_id).await? {
                // Try to register the actuator with different types until one works
                let actuator_types = [
                    RobstrideActuatorType::Robstride01,
                    RobstrideActuatorType::Robstride00,
                    RobstrideActuatorType::Robstride02,
                    RobstrideActuatorType::Robstride03,
                    RobstrideActuatorType::Robstride04,
                ];
                
                let mut registered = false;
                for actuator_type in actuator_types {
                    if self.ping_actuator(can_id, actuator_type).await.unwrap_or(false) {
                        registered = true;
                        break;
                    }
                }
                
                if registered {
                    discovered.push(can_id);
                }
            }
        }

        Ok(discovered)
    }

    /// Scan multiple CAN interfaces for actuators
    pub async fn scan_multiple_interfaces(
        interfaces: &[&str],
        id_range: std::ops::RangeInclusive<u8>,
    ) -> crate::Result<std::collections::HashMap<String, Vec<u8>>> {
        let mut all_discovered = std::collections::HashMap::new();

        for interface in interfaces {
            match Self::new(interface).await {
                Ok(mut driver) => match driver.scan_actuators(id_range.clone()).await {
                    Ok(discovered) => {
                        if !discovered.is_empty() {
                            all_discovered.insert(interface.to_string(), discovered);
                        }
                    }
                    Err(e) => {
                        tracing::warn!("Failed to scan {}: {}", interface, e);
                    }
                },
                Err(e) => {
                    tracing::warn!("Failed to connect to {}: {}", interface, e);
                }
            }
        }

        Ok(all_discovered)
    }

    /// Create ObtainId request frame (universal for all actuator types)
    fn create_obtain_id_request(&self, can_id: u8) -> crate::can::CanFrame {
        use crate::can::{CanFrame, CAN_MAX_DLEN};

        let mut frame = CanFrame::default();
        frame.can_id = 0x8000_0000; // EFF flag
        frame.len = 8;
        frame.len8_dlc = 8;

        // Pack ObtainId request data
        frame.can_data[0] = can_id; // actuator_can_id
        frame.can_data[1] = 0xFD; // host_id low byte
        frame.can_data[2] = 0x00; // host_id high byte
        frame.can_data[3] = 0x00; // mux = 0x00 for ObtainId
                                  // rest default to zeros

        frame
    }

    /// Check if response frame is for the specified CAN ID
    fn is_response_for_can_id(&self, frame: &crate::can::CanFrame, expected_can_id: u8) -> bool {
        // Check mux is 0x00 (ObtainId response)
        let mux = frame.can_data[3] & 0x1F;
        if mux != 0x00 {
            return false;
        }

        // For ObtainId response, actuator_can_id is at bytes 1-2 (u16 little endian)
        let response_can_id = frame.can_data[1] as u16 | ((frame.can_data[2] as u16) << 8);
        response_can_id as u8 == expected_can_id
    }

    /// Get the interface name
    pub fn interface_name(&self) -> &str {
        self.can_interface.interface_name()
    }

    /// Send raw ping to actuator (no actuator type needed)
    pub async fn ping_actuator_raw(&mut self, can_id: u8) -> crate::Result<bool> {
        use crate::protocol::{ObtainIdRequest, mux_from_can_frame, actuator_can_id_from_response};
        
        // Use proper protocol structure
        let request = ObtainIdRequest::new(0xFD, can_id);  // 0xFD is default host_id
        let frame: crate::can::CanFrame = request.into();
        
        // Send ping
        self.can_interface.send_frame(&frame).await.ok();
        
        // Wait for response with reasonable timeout
        match tokio::time::timeout(
            std::time::Duration::from_millis(100),
            self.can_interface.recv_frame(),
        )
        .await
        {
            Ok(Ok(response)) => {
                // Check if it's an ObtainId response and matches our CAN ID
                let mux = mux_from_can_frame(&response);
                if mux == 0x00 {
                    let response_can_id = actuator_can_id_from_response(&response);
                    Ok(response_can_id == can_id)
                } else {
                    Ok(false)
                }
            }
            _ => Ok(false),
        }
    }


    /// Read all parameters from actuator (with debugging)
    /// This uses the correct ReadAllParams protocol that returns parameter fragments
    pub async fn read_all_params_debug(&mut self, actuator_id: u8) -> crate::Result<Vec<(u16, u8, Vec<u8>)>> {
        use crate::protocol::{ReadAllParamsRequest, ActuatorRequest, ActuatorResponse};
        
        println!("Reading all parameters from actuator {}", actuator_id);
        
        // First, ensure we have the mcu_uid by checking if client exists
        let client = self.clients.get(&actuator_id)
            .ok_or_else(|| crate::RobstrideError::ActuatorNotFound(actuator_id))?;
        
        let mcu_uid = client.mcu_uid()
            .ok_or_else(|| crate::RobstrideError::Protocol("No MCU UID available. Call obtain_id first.".into()))?;
            
        
        println!("Using MCU UID: 0x{:016X}", mcu_uid);
        
        let request = ReadAllParamsRequest::new(0xFD, actuator_id, mcu_uid);
        let frame: crate::can::CanFrame = ActuatorRequest::ReadAllParams(request).into();
        
        // Debug: Print request frame
        println!("Sending ReadAllParams request:");
        let can_id = frame.can_id;
        let can_data = frame.can_data;
        println!("   CAN ID: 0x{:08X}", can_id);
        println!("   Data: {:02X?}", &can_data);
        
        // Send request
        self.can_interface.send_frame(&frame).await?;
        
        let mut fragments = Vec::new();
        let start_time = std::time::Instant::now();
        
        // Collect all parameter fragments (this may take multiple responses)
        while start_time.elapsed() < Duration::from_millis(2000) {
            match tokio::time::timeout(Duration::from_millis(100), self.can_interface.recv_frame()).await {
                Ok(Ok(response_frame)) => {
                    println!("Received response frame:");
                    let response_can_id = response_frame.can_id;
                    let response_can_data = response_frame.can_data;
                    println!("   CAN ID: 0x{:08X}", response_can_id);
                    println!("   Data: {:02X?}", &response_can_data);
                    
                    // Try to parse as ReadAllParamsResponse
                    let response: ActuatorResponse = response_frame.into();
                    match response {
                        ActuatorResponse::ReadAllParams(param_resp) => {
                            println!("Parsed as ReadAllParamsResponse:");
                            
                            let param_idx = param_resp.param_idx;
                            let byte_marker = param_resp.byte_marker;
                            let can_data = &param_resp.can_data;
                            println!("   Param Index: 0x{:04X}", param_idx);
                            println!("   Byte Marker: 0x{:02X}", byte_marker); 
                            println!("   Data: {:02X?}", can_data);
                            // Store fragment: (param_idx, byte_marker, data)
                            fragments.push((param_resp.param_idx, param_resp.byte_marker, param_resp.can_data.to_vec()));
                        }
                        _ => {
                            println!("Response was not a ReadAllParams response");
                        }
                    }
                }
                Ok(Err(e)) => {
                    println!("CAN error: {}", e);
                    break;
                }
                Err(_) => {
                    // Timeout on this iteration, but continue collecting fragments
                    // Some actuators may send fragments slowly
                    continue;
                }
            }
        }
        
        println!("Collected {} parameter fragments", fragments.len());
        Ok(fragments)
    }



    
    /// Discover actuators by scanning specific CAN IDs
    /// Caller provides the list of CAN IDs to scan and their expected types
    pub async fn discover_actuators(
        &mut self,
        scan_list: &[(u8, RobstrideActuatorType)],
    ) -> crate::Result<Vec<u8>> {
        let mut found_actuators = Vec::new();

        for &(can_id, actuator_type) in scan_list {
            let mut client = ActuatorClient::new(can_id, actuator_type);
            let request = client.stage_request(&ActuatorRequestParams::ObtainId);

            if let Err(_) = self.can_interface.send_frame(&request).await {
                continue; // Skip if send fails
            }

            // Wait for response with timeout
            match timeout(Duration::from_millis(100), self.can_interface.recv_frame()).await {
                Ok(Ok(response)) => {
                    if let Ok(_) = client.handle_response(&response) {
                        found_actuators.push(can_id);
                        self.clients.insert(can_id, client);
                    }
                }
                _ => {} // Timeout or error - actuator not found
            }
        }

        Ok(found_actuators)
    }

    /// Send ObtainId request to a specific CAN ID
    pub async fn ping_actuator(
        &mut self,
        can_id: u8,
        actuator_type: RobstrideActuatorType,
    ) -> crate::Result<bool> {
        let mut client = ActuatorClient::new(can_id, actuator_type);
        let request = client.stage_request(&ActuatorRequestParams::ObtainId);

        self.can_interface.send_frame(&request).await?;

        match timeout(Duration::from_millis(100), self.can_interface.recv_frame()).await {
            Ok(Ok(response)) => match client.handle_response(&response) {
                Ok(_) => {
                    self.clients.insert(can_id, client);
                    Ok(true)
                }
                Err(_) => Ok(false),
            },
            _ => Ok(false),
        }
    }

    pub async fn enable_actuator(&mut self, can_id: u8) -> crate::Result<()> {
        let client = self
            .clients
            .get_mut(&can_id)
            .ok_or(crate::RobstrideError::ActuatorNotFound(can_id))?;

        let request = client.stage_request(&ActuatorRequestParams::MotorEnable);
        self.can_interface.send_frame(&request).await?;

        // Wait for response
        let response = timeout(Duration::from_secs(1), self.can_interface.recv_frame()).await??;
        client.handle_response(&response)?;

        Ok(())
    }

    pub async fn move_actuator(
        &mut self,
        can_id: u8,
        command: ActuatorCommand,
    ) -> crate::Result<()> {
        let client = self
            .clients
            .get_mut(&can_id)
            .ok_or(crate::RobstrideError::ActuatorNotFound(can_id))?;

        let request = client.stage_request(&ActuatorRequestParams::Control(command));
        self.can_interface.send_frame(&request).await?;

        Ok(())
    }

    pub async fn get_actuator_state(&mut self, can_id: u8) -> crate::Result<ActuatorState> {
        let client = self
            .clients
            .get_mut(&can_id)
            .ok_or(crate::RobstrideError::ActuatorNotFound(can_id))?;

        let request = client.stage_request(&ActuatorRequestParams::Feedback);
        self.can_interface.send_frame(&request).await?;

        // Wait for response
        let response = timeout(Duration::from_secs(1), self.can_interface.recv_frame()).await??;

        let mut state = ActuatorState::default();
        if let Some(update) = client.handle_response(&response)? {
            state.merge_feedback(update);
        }

        Ok(state)
    }

    pub fn get_registered_actuators(&self) -> Vec<u8> {
        self.clients.keys().copied().collect()
    }

    pub fn has_actuator(&self, can_id: u8) -> bool {
        self.clients.contains_key(&can_id)
    }

    /// Read raw parameter data from actuator (for Python bindings)
    pub async fn read_raw_parameter(&mut self, actuator_id: u8, param_index: u16) -> crate::Result<Option<Vec<u8>>> {
        use crate::protocol::{ReadAllParamsRequest, ActuatorRequest, ActuatorResponse};
        
        // Ensure we have the mcu_uid by checking if client exists
        let client = self.clients.get(&actuator_id)
            .ok_or_else(|| crate::RobstrideError::ActuatorNotFound(actuator_id))?;
        
        let mcu_uid = client.mcu_uid()
            .ok_or_else(|| crate::RobstrideError::Protocol("No MCU UID available. Call scan_actuators or ping_actuator first.".into()))?;
        
        // Send ReadAllParams request
        let request = ReadAllParamsRequest::new(0xFD, actuator_id, mcu_uid);
        let frame: crate::can::CanFrame = ActuatorRequest::ReadAllParams(request).into();
        self.can_interface.send_frame(&frame).await?;
        
        // Collect responses for the specific parameter
        let start_time = std::time::Instant::now();
        let mut parameter_data = Vec::new();
        
        while start_time.elapsed() < Duration::from_millis(1000) {
            match tokio::time::timeout(Duration::from_millis(100), self.can_interface.recv_frame()).await {
                Ok(Ok(response_frame)) => {
                    let response: ActuatorResponse = response_frame.into();
                    match response {
                        ActuatorResponse::ReadAllParams(param_resp) => {
                            if param_resp.param_idx == param_index {
                                parameter_data.extend_from_slice(&param_resp.can_data);
                                // For single parameter, we can return after first match
                                return Ok(Some(parameter_data));
                            }
                        }
                        _ => continue,
                    }
                }
                _ => break,
            }
        }
        
        Ok(None)
    }

    /// Dump all parameters from actuator (for Python bindings)
    pub async fn dump_all_parameters(&mut self, actuator_id: u8) -> crate::Result<std::collections::HashMap<u16, Vec<u8>>> {
        use crate::protocol::{ReadAllParamsRequest, ActuatorRequest, ActuatorResponse};
        use std::collections::HashMap;
        
        // Ensure we have the mcu_uid by checking if client exists
        let client = self.clients.get(&actuator_id)
            .ok_or_else(|| crate::RobstrideError::ActuatorNotFound(actuator_id))?;
        
        let mcu_uid = client.mcu_uid()
            .ok_or_else(|| crate::RobstrideError::Protocol("No MCU UID available. Call scan_actuators or ping_actuator first.".into()))?;
        
        // Send ReadAllParams request
        let request = ReadAllParamsRequest::new(0xFD, actuator_id, mcu_uid);
        let frame: crate::can::CanFrame = ActuatorRequest::ReadAllParams(request).into();
        self.can_interface.send_frame(&frame).await?;
        
        // Collect all parameter responses
        let start_time = std::time::Instant::now();
        let mut parameters: HashMap<u16, Vec<u8>> = HashMap::new();
        
        while start_time.elapsed() < Duration::from_millis(2000) {
            match tokio::time::timeout(Duration::from_millis(100), self.can_interface.recv_frame()).await {
                Ok(Ok(response_frame)) => {
                    let response: ActuatorResponse = response_frame.into();
                    match response {
                        ActuatorResponse::ReadAllParams(param_resp) => {
                            let param_idx = param_resp.param_idx;
                            let data = param_resp.can_data.to_vec();
                            
                            // Accumulate data for each parameter
                            parameters.entry(param_idx)
                                .and_modify(|existing| existing.extend_from_slice(&data))
                                .or_insert(data);
                        }
                        _ => continue,
                    }
                }
                _ => {
                    // If we got some parameters and timeout, break
                    if !parameters.is_empty() {
                        break;
                    }
                }
            }
        }
        
        Ok(parameters)
    }
}

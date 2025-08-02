//! Robstride CAN protocol implementation
//!
//! Extracted from firmware/src/robstride.rs

use crate::can::{CanFrame, CAN_MAX_DLEN};
use crate::types::ActuatorCommand;
use bytemuck::{Pod, Zeroable};
use tracing::warn;

pub trait RobstrideActuatorFrame {}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct ObtainIdRequest {
    pub actuator_can_id: u8,
    pub host_id: u16,
    mux: u8, /* 0x00 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    can_data: [u8; CAN_MAX_DLEN],
}

impl RobstrideActuatorFrame for ObtainIdRequest {}

impl ObtainIdRequest {
    pub fn new(host_id: u16, actuator_can_id: u8) -> Self {
        Self {
            mux: 0x00,
            host_id,
            actuator_can_id,
            len: 8,
            ..Default::default()
        }
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct ObtainIdResponse {
    fe: u8,
    pub actuator_can_id: u16,
    mux: u8, /* 0x00 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    pub mcu_uid: u64,
}

impl RobstrideActuatorFrame for ObtainIdResponse {}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct ControlCommandRequest {
    pub actuator_can_id: u8,
    pub torque_scale: u16,
    mux: u8, /* 0x01 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    pub angle_scale: u16,
    pub angular_vel_scale: u16,
    pub kp_scale: u16,
    pub kd_scale: u16,
}

impl RobstrideActuatorFrame for ControlCommandRequest {}

impl ControlCommandRequest {
    pub fn new(
        actuator_can_id: u8,
        torque_scale: u16,
        angle_scale: u16,
        angular_vel_scale: u16,
        kd_scale: u16,
        kp_scale: u16,
    ) -> Self {
        Self {
            mux: 0x01,
            torque_scale,
            actuator_can_id,
            len: 8,
            angle_scale: angle_scale.to_be(),
            angular_vel_scale: angular_vel_scale.to_be(),
            kp_scale: kp_scale.to_be(),
            kd_scale: kd_scale.to_be(),
            ..Default::default()
        }
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct MotorEnableRequest {
    pub actuator_can_id: u8,
    pub host_id: u16,
    mux: u8, /* 0x03 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    can_data: [u8; CAN_MAX_DLEN],
}

impl RobstrideActuatorFrame for MotorEnableRequest {}

impl MotorEnableRequest {
    pub fn new(host_id: u16, actuator_can_id: u8) -> Self {
        Self {
            mux: 0x03,
            host_id,
            actuator_can_id,
            len: 8,
            ..Default::default()
        }
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct FeedbackRequest {
    pub actuator_can_id: u8,
    pub host_id: u16,
    mux: u8, /* 0x02 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    can_data: [u8; CAN_MAX_DLEN],
}

impl RobstrideActuatorFrame for FeedbackRequest {}

impl FeedbackRequest {
    pub fn new(host_id: u16, actuator_can_id: u8) -> Self {
        Self {
            mux: 0x02,
            host_id,
            actuator_can_id,
            len: 8,
            ..Default::default()
        }
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct FeedbackResponse {
    host_id: u8,
    pub actuator_can_id: u8,
    fault_flags: u8,
    mux: u8, /* 0x2 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    pub angle_scale_be: u16,
    pub angular_vel_scale_be: u16,
    pub torque_be: u16,
    pub temp_be: u16,
}

impl RobstrideActuatorFrame for FeedbackResponse {}


#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct SingleParameterReadRequest {
    pub actuator_can_id: u8,
    pub host_id: u16,
    mux: u8, /* 0x11 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    pub param_index: u16, // Parameter index to read
    reserved1: u16,       // Bytes 2-3: 00
    reserved2: u32,       // Bytes 4-7: 00
}

impl RobstrideActuatorFrame for SingleParameterReadRequest {}

impl SingleParameterReadRequest {
    pub fn new(host_id: u16, actuator_can_id: u8, param_index: u16) -> Self {
        Self {
            mux: 0x11,
            host_id,
            actuator_can_id,
            len: 8,
            param_index,
            reserved1: 0,
            reserved2: 0,
            ..Default::default()
        }
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct SingleParameterReadResponse {
    pub host_id: u8,
    pub actuator_can_id: u8,
    pub status: u8,       // 0x00 = success, 0x01 = error
    mux: u8,              /* 0x11 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    pub param_index: u16, // Parameter index that was read
    reserved: u16,        // Bytes 2-3: 00
    pub param_data: u32,  // Bytes 4-7: Parameter data (little endian)
}

impl RobstrideActuatorFrame for SingleParameterReadResponse {}

impl SingleParameterReadResponse {
    /// Check if the parameter read was successful
    pub fn is_success(&self) -> bool {
        self.status == 0x00
    }

    /// Get parameter data as bytes (little endian)
    pub fn param_data_bytes(&self) -> [u8; 4] {
        self.param_data.to_le_bytes()
    }
}


#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct SingleParameterWriteRequest {
    pub actuator_can_id: u8,
    pub host_id: u16,
    mux: u8, /* 0x12 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    pub param_index: u16, // Parameter index to write
    reserved: u16,        // Bytes 2-3: 00
    pub param_data: u32,  // Bytes 4-7: Parameter data (little endian)
}

impl RobstrideActuatorFrame for SingleParameterWriteRequest {}

impl SingleParameterWriteRequest {
    pub fn new(host_id: u16, actuator_can_id: u8, param_index: u16, data: u32) -> Self {
        Self {
            mux: 0x12,
            host_id,
            actuator_can_id,
            len: 8,
            param_index,
            reserved: 0,
            param_data: data,
            ..Default::default()
        }
    }

    /// Create request for uint8 parameter
    pub fn new_uint8(host_id: u16, actuator_can_id: u8, param_index: u16, value: u8) -> Self {
        Self::new(host_id, actuator_can_id, param_index, value as u32)
    }

    /// Create request for uint16 parameter
    pub fn new_uint16(host_id: u16, actuator_can_id: u8, param_index: u16, value: u16) -> Self {
        Self::new(host_id, actuator_can_id, param_index, value as u32)
    }

    /// Create request for float parameter
    pub fn new_float(host_id: u16, actuator_can_id: u8, param_index: u16, value: f32) -> Self {
        Self::new(host_id, actuator_can_id, param_index, value.to_bits())
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct MotorDataSaveRequest {
    pub actuator_can_id: u8,
    pub host_id: u16,
    mux: u8, /* 0x16 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    save_data: [u8; 8], // Fixed sequence: 01 02 03 04 05 06 07 08
}

impl RobstrideActuatorFrame for MotorDataSaveRequest {}

impl MotorDataSaveRequest {
    pub fn new(host_id: u16, actuator_can_id: u8) -> Self {
        Self {
            mux: 0x16,
            host_id,
            actuator_can_id,
            len: 8,
            save_data: [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08],
            ..Default::default()
        }
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct ZeroPositionRequest {
    pub actuator_can_id: u8,
    pub host_id: u16,
    mux: u8, /* 0x06 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    can_data: [u8; CAN_MAX_DLEN],
}

impl RobstrideActuatorFrame for ZeroPositionRequest {}

impl ZeroPositionRequest {
    pub fn new(host_id: u16, actuator_can_id: u8) -> Self {
        let mut request = Self {
            mux: 0x06,
            host_id,
            actuator_can_id,
            len: 8,
            ..Default::default()
        };
        // Set the specific data bytes as per bash script: 01.01.CD.00.00.00.00.00
        // Byte[0] = 1 as per manual
        request.can_data[0] = 0x01;
        request.can_data[1] = 0x01;
        request.can_data[2] = 0xCD;
        // Remaining bytes stay as 0x00 from Default
        request
    }
}

#[derive(Debug, Clone)]
pub enum ActuatorRequest {
    ObtainId(ObtainIdRequest),
    Control(ControlCommandRequest),
    MotorEnable(MotorEnableRequest),
    Feedback(FeedbackRequest),
    ReadAllParams(ReadAllParamsRequest),
    ZeroPosition(ZeroPositionRequest),
    SingleParameterRead(SingleParameterReadRequest),
    SingleParameterWrite(SingleParameterWriteRequest),
    MotorDataSave(MotorDataSaveRequest),
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ActuatorRequestParams {
    ObtainId,
    MotorEnable,
    Control(ActuatorCommand),
    Feedback,
    ReadAllParams(u64), // mcu_uid required
    ZeroPosition,
    SingleParameterRead(u16),
    SingleParameterWrite(u16, u32),
    MotorDataSave,
}

#[derive(Debug, Clone)]
pub enum ActuatorResponse {
    ObtainId(ObtainIdResponse),
    Feedback(FeedbackResponse),
    ReadAllParams(ReadAllParamsResponse),
    SingleParameterRead(SingleParameterReadResponse),
}

// Frame conversion implementations (exact from firmware)
impl<T> From<T> for CanFrame
where
    T: RobstrideActuatorFrame + Pod + Zeroable,
{
    fn from(req: T) -> Self {
        let mut ret = bytemuck::must_cast::<T, Self>(req);
        ret.can_id |= 0x8000_0000; // EFF FLAG
        ret
    }
}

impl From<ActuatorRequest> for CanFrame {
    fn from(req: ActuatorRequest) -> Self {
        match req {
            ActuatorRequest::ObtainId(req) => req.into(),
            ActuatorRequest::Control(req) => req.into(),
            ActuatorRequest::MotorEnable(req) => req.into(),
            ActuatorRequest::Feedback(req) => req.into(),
            ActuatorRequest::ReadAllParams(req) => req.into(),
            ActuatorRequest::ZeroPosition(req) => req.into(),
            ActuatorRequest::SingleParameterRead(req) => req.into(),
            ActuatorRequest::SingleParameterWrite(req) => req.into(),
            ActuatorRequest::MotorDataSave(req) => req.into(),
        }
    }
}

impl From<CanFrame> for ActuatorResponse {
    fn from(mut frame: CanFrame) -> ActuatorResponse {
        frame.can_id ^= 0x8000_0000; // remove EFF FLAG
        let mux = mux_from_can_frame(&frame);
        match mux {
            0x00 => {
                ActuatorResponse::ObtainId(bytemuck::must_cast::<CanFrame, ObtainIdResponse>(frame))
            }
            0x02 => {
                ActuatorResponse::Feedback(bytemuck::must_cast::<CanFrame, FeedbackResponse>(frame))
            }
            0x11 => {
                ActuatorResponse::SingleParameterRead(bytemuck::must_cast::<CanFrame, SingleParameterReadResponse>(frame))
            }
            0x13 => {
                ActuatorResponse::ReadAllParams(bytemuck::must_cast::<CanFrame, ReadAllParamsResponse>(frame))
            }
            
            _ => panic!("Unknown mux value: {}", mux),
        }
    }
}

pub fn mux_from_can_frame(frame: &CanFrame) -> u8 {
    let frame: &[u8; std::mem::size_of::<CanFrame>()] = bytemuck::cast_ref(frame);
    frame[3] & 0x1F // Mask to get the mux (5 bits)
}

pub fn actuator_can_id_from_response(frame: &CanFrame) -> u8 {
    let mux = mux_from_can_frame(frame);
    match mux {
        0x00 => bytemuck::must_cast::<CanFrame, ObtainIdResponse>(*frame).actuator_can_id as u8,
        0x02 => bytemuck::must_cast::<CanFrame, FeedbackResponse>(*frame).actuator_can_id as u8,
        0x11 => bytemuck::must_cast::<CanFrame, SingleParameterReadResponse>(*frame).actuator_can_id as u8,
        0x13 => bytemuck::must_cast::<CanFrame, ReadAllParamsResponse>(*frame).actuator_can_id as u8,
        _ => {
            warn!(
                "Unknown mux value: {} in actuator_can_id_from_response, returning 0x7F",
                mux
            );
            0x7F
        }
    }
}

impl ActuatorRequest {
    pub fn response_mux(&self) -> u8 {
        match self {
            Self::ObtainId(_) => 0x0,
            Self::Control(_) => 0x2,
            Self::MotorEnable(_) => 0x02,
            Self::Feedback(_) => 0x02,
            Self::ReadAllParams(_) => 0x13,
            Self::ZeroPosition(_) => 0x02,
            Self::SingleParameterRead(_) => 0x11,
            Self::SingleParameterWrite(_) => 0x02,
            Self::MotorDataSave(_) => 0x02,
        }
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct ReadAllParamsRequest {
    pub actuator_can_id: u8,
    pub host_id: u8,
    pub res_id: u8,
    mux: u8, /* 0x13 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    mcu_uid: u64, /* payload */
}

impl RobstrideActuatorFrame for ReadAllParamsRequest {}

impl ReadAllParamsRequest {
    pub fn new(host_id: u8, actuator_can_id: u8, mcu_uid: u64) -> Self {
        Self {
            mux: 0x13,
            actuator_can_id,
            host_id,
            len: 8,
            mcu_uid,
            ..Default::default()
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Pod, Zeroable)]
#[repr(C, packed)]
pub struct ReadAllParamsResponse {
    pub host_id: u8,
    pub actuator_can_id: u8,
    // 0x0 => 0, 0x1 => 1, 0x2 => 2, 0x6 => 3, 0x7 => 4 0x8 => 5
    pub byte_marker: u8, 
    mux: u8, /* 0x13 */
    len: u8,
    pad: u8,
    res0: u8,
    len8_dlc: u8,
    pub param_idx: u16,
    pub can_data: [u8; 6], // CAN_MAX_DLEN - 2 = 6 bytes
}

impl RobstrideActuatorFrame for ReadAllParamsResponse {}

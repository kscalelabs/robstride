//! Robstride CAN protocol implementation
//! 
//! Extracted from firmware/src/robstride.rs

use crate::can::{CanFrame, CAN_MAX_DLEN};
use crate::types::{ActuatorCommand, ActuatorFeedbackUpdate};
use crate::actuator_types::{RobstrideActuatorType, RangeSet};
use bytemuck::{Pod, Zeroable};
use tracing::{debug, warn};

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

#[derive(Debug, Clone)]
pub enum ActuatorRequest {
    ObtainId(ObtainIdRequest),
    Control(ControlCommandRequest),
    MotorEnable(MotorEnableRequest),
    Feedback(FeedbackRequest),
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ActuatorRequestParams {
    ObtainId,
    MotorEnable,
    Control(ActuatorCommand),
    Feedback,
}

#[derive(Debug, Clone)]
pub enum ActuatorResponse {
    ObtainId(ObtainIdResponse),
    Feedback(FeedbackResponse),
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
        }
    }
}

impl From<CanFrame> for ActuatorResponse {
    fn from(mut frame: CanFrame) -> ActuatorResponse {
        frame.can_id ^= 0x8000_0000; // remove EFF FLAG
        let mux = mux_from_can_frame(&frame);
        match mux {
            0x00 => ActuatorResponse::ObtainId(bytemuck::must_cast::<CanFrame, ObtainIdResponse>(frame)),
            0x02 => ActuatorResponse::Feedback(bytemuck::must_cast::<CanFrame, FeedbackResponse>(frame)),
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
        _ => {
            warn!("Unknown mux value: {} in actuator_can_id_from_response, returning 0x7F", mux);
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
        }
    }
}
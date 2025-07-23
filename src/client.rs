use crate::actuator_types::{RangeSet, RobstrideActuatorType};
use crate::can::CanFrame;
use crate::protocol::{ActuatorRequest, ActuatorRequestParams, ActuatorResponse, FeedbackResponse, ReadAllParamsRequest};
use crate::types::{ActuatorCommand, ActuatorFeedbackUpdate};
use tracing::debug;

#[derive(Debug)]
enum ActuatorClientState {
    Reset,
    Ready,
    AwaitingResponse,
}

#[derive(Debug)]
pub struct ActuatorClient {
    host_id: u16,
    pub actuator_can_id: u8,
    mcu_uid: Option<u64>,
    last_request: Option<ActuatorRequest>,
    state: ActuatorClientState,
    actuator_ranges: RangeSet<f64>,
    can_range: RangeSet<f64>,
}

impl ActuatorClient {
    /// Create a new actuator client with explicit actuator type
    /// Caller must specify both CAN ID and actuator type
    pub fn new(actuator_can_id: u8, actuator_type: RobstrideActuatorType) -> Self {
        ActuatorClient {
            host_id: 0xFD00,
            actuator_can_id,
            mcu_uid: None,
            state: ActuatorClientState::Reset,
            last_request: None,
            actuator_ranges: actuator_type.actuator_ranges(),
            can_range: actuator_type.can_ranges(),
        }
    }

    pub fn mcu_uid(&self) -> Option<u64> {
        self.mcu_uid
    }

    pub fn reset(&mut self) {
        self.state = ActuatorClientState::Reset;
        self.last_request = None;
    }

    pub fn build_request(&self, params: &ActuatorRequestParams) -> ActuatorRequest {
        use crate::protocol::{
            ControlCommandRequest, FeedbackRequest, MotorEnableRequest, ObtainIdRequest,
        };

        match params {
            ActuatorRequestParams::ObtainId => {
                ActuatorRequest::ObtainId(ObtainIdRequest::new(self.host_id, self.actuator_can_id))
            }
            ActuatorRequestParams::MotorEnable => ActuatorRequest::MotorEnable(
                MotorEnableRequest::new(self.host_id, self.actuator_can_id),
            ),
            ActuatorRequestParams::Feedback => {
                ActuatorRequest::Feedback(FeedbackRequest::new(self.host_id, self.actuator_can_id))
            }
            ActuatorRequestParams::ReadAllParams(mcu_uid) => {
                ActuatorRequest::ReadAllParams(ReadAllParamsRequest::new(self.host_id as u8, self.actuator_can_id, *mcu_uid))
            }
            ActuatorRequestParams::Control(cmd) => {
                ActuatorRequest::Control(ControlCommandRequest::new(
                    self.actuator_can_id,
                    self.actuator_ranges
                        .torque
                        .scale_value(cmd.qfrc, &self.can_range.torque) as u16,
                    self.actuator_ranges
                        .angle
                        .scale_value(cmd.qpos, &self.can_range.angle) as u16,
                    self.actuator_ranges
                        .velocity
                        .scale_value(cmd.qvel, &self.can_range.velocity) as u16,
                    self.actuator_ranges
                        .kd
                        .scale_value(cmd.kd, &self.can_range.kd) as u16,
                    self.actuator_ranges
                        .kp
                        .scale_value(cmd.kp, &self.can_range.kp) as u16,
                ))
            }
        }
    }

    pub fn stage_request(&mut self, params: &ActuatorRequestParams) -> CanFrame {
        self.state = ActuatorClientState::AwaitingResponse;
        let request = self.build_request(params);
        self.last_request = Some(request.clone());
        request.into()
    }

    pub fn handle_response(
        &mut self,
        response: &CanFrame,
    ) -> crate::Result<Option<ActuatorFeedbackUpdate>> {
        let response: ActuatorResponse = (*response).into();

        match response {
            ActuatorResponse::ObtainId(resp) => {
                debug!("Received ObtainId response: {:?}", resp);
                if resp.actuator_can_id as u8 != self.actuator_can_id {
                    return Err(crate::RobstrideError::Protocol(
                        "Response CAN ID mismatch".into(),
                    ));
                }
                self.mcu_uid = Some(resp.mcu_uid);
                self.state = ActuatorClientState::Ready;
                Ok(None)
            }
            ActuatorResponse::Feedback(resp) => {
                debug!("Received Feedback response: {:?}", resp);
                if resp.actuator_can_id != self.actuator_can_id {
                    return Err(crate::RobstrideError::Protocol(
                        "Feedback CAN ID mismatch".into(),
                    ));
                }
                self.state = ActuatorClientState::Ready;
                Ok(Some(self.update_from_feedback(&resp)))
            }
            ActuatorResponse::ReadAllParams(_) => {
                // ReadAllParams responses are handled at the driver level, not by individual clients
                self.state = ActuatorClientState::Ready;
                Ok(None)
            }
        }
    }

    fn update_from_feedback(&self, resp: &FeedbackResponse) -> ActuatorFeedbackUpdate {
        ActuatorFeedbackUpdate {
            qpos: Some(self.can_range.angle.scale_value(
                resp.angle_scale_be.swap_bytes() as f64,
                &self.actuator_ranges.angle,
            )),
            qvel: Some(self.can_range.velocity.scale_value(
                resp.angular_vel_scale_be.swap_bytes() as f64,
                &self.actuator_ranges.velocity,
            )),
            qfrc: Some(self.can_range.torque.scale_value(
                resp.torque_be.swap_bytes() as f64,
                &self.actuator_ranges.torque,
            )),
            kp: None,
            kd: None,
            temp: None,
            faults: None,
        }
    }

    pub fn can_id(&self) -> u8 {
        self.actuator_can_id
    }
}

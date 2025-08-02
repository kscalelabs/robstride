//! Robstride actuator parameter definitions
use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ParameterType {
    String,
    Uint8,
    Uint16,
    Uint32,
    Int16,
    Int32,
    Float,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ParameterAccess {
    ReadOnly,
    ReadWrite,
    Settings,
    Disposition,
}

#[derive(Debug, Clone)]
pub struct ParameterInfo {
    pub code: u16,
    pub name: &'static str,
    pub param_type: ParameterType,
    pub access: ParameterAccess,
    pub description: &'static str,
}

#[derive(Debug, Clone)]
pub enum ParameterValue {
    String(String),
    Uint8(u8),
    Uint16(u16),
    Uint32(u32),
    Int16(i16),
    Int32(i32),
    Float(f32),
}

impl ParameterValue {
    pub fn from_bytes(bytes: &[u8], param_type: ParameterType) -> Option<Self> {
        match param_type {
            ParameterType::String => {
                // Find null terminator or use full length
                let end = bytes.iter().position(|&b| b == 0).unwrap_or(bytes.len());
                let string = String::from_utf8_lossy(&bytes[..end]).to_string();
                Some(ParameterValue::String(string))
            }
            ParameterType::Uint8 => {
                if bytes.len() >= 1 {
                    Some(ParameterValue::Uint8(bytes[0]))
                } else { None }
            }
            ParameterType::Uint16 => {
                if bytes.len() >= 2 {
                    let val = u16::from_le_bytes([bytes[0], bytes[1]]);
                    Some(ParameterValue::Uint16(val))
                } else { None }
            }
            ParameterType::Uint32 => {
                if bytes.len() >= 4 {
                    let val = u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]);
                    Some(ParameterValue::Uint32(val))
                } else { None }
            }
            ParameterType::Int16 => {
                if bytes.len() >= 2 {
                    let val = i16::from_le_bytes([bytes[0], bytes[1]]);
                    Some(ParameterValue::Int16(val))
                } else { None }
            }
            ParameterType::Int32 => {
                if bytes.len() >= 4 {
                    let val = i32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]);
                    Some(ParameterValue::Int32(val))
                } else { None }
            }
            ParameterType::Float => {
                if bytes.len() >= 4 {
                    let val = f32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]);
                    Some(ParameterValue::Float(val))
                } else { None }
            }
        }
    }
}

impl std::fmt::Display for ParameterValue {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ParameterValue::String(s) => write!(f, "{}", s),
            ParameterValue::Uint8(v) => write!(f, "{}", v),
            ParameterValue::Uint16(v) => write!(f, "{}", v),
            ParameterValue::Uint32(v) => write!(f, "{}", v),
            ParameterValue::Int16(v) => write!(f, "{}", v),
            ParameterValue::Int32(v) => write!(f, "{}", v),
            ParameterValue::Float(v) => write!(f, "{:.6}", v),
        }
    }
}
    
pub fn get_parameter_table() -> HashMap<u16, ParameterInfo> {
        let mut params = HashMap::new();
    
        /* ───────────────────────────── Device identification ───────────────────────────── */
        params.insert(0x0000, ParameterInfo { code: 0x0000, name: "Name",        param_type: ParameterType::String,  access: ParameterAccess::ReadWrite, description: "Device name" });
        params.insert(0x0001, ParameterInfo { code: 0x0001, name: "BarCode",     param_type: ParameterType::String,  access: ParameterAccess::ReadWrite, description: "Device barcode / serial" });
    
        /* ───────────────────────────── Boot / firmware info ────────────────────────────── */
        params.insert(0x1000, ParameterInfo { code: 0x1000, name: "BootCodeVersion", param_type: ParameterType::String, access: ParameterAccess::ReadOnly,  description: "Bootloader version string" });
        params.insert(0x1001, ParameterInfo { code: 0x1001, name: "BootBuildDate",  param_type: ParameterType::String, access: ParameterAccess::ReadOnly,  description: "Bootloader build date" });
        params.insert(0x1002, ParameterInfo { code: 0x1002, name: "BootBuildTime",  param_type: ParameterType::String, access: ParameterAccess::ReadOnly,  description: "Bootloader build time" });
        params.insert(0x1003, ParameterInfo { code: 0x1003, name: "AppCodeVersion", param_type: ParameterType::String, access: ParameterAccess::ReadOnly,  description: "Application firmware version" });
        params.insert(0x1004, ParameterInfo { code: 0x1004, name: "AppGitVersion",  param_type: ParameterType::String, access: ParameterAccess::ReadOnly,  description: "Git commit hash of firmware" });
        params.insert(0x1005, ParameterInfo { code: 0x1005, name: "AppBuildDate",   param_type: ParameterType::String, access: ParameterAccess::ReadOnly,  description: "Application build date" });
        params.insert(0x1006, ParameterInfo { code: 0x1006, name: "AppBuildTime",   param_type: ParameterType::String, access: ParameterAccess::ReadOnly,  description: "Application build time" });
        params.insert(0x1007, ParameterInfo { code: 0x1007, name: "AppCodeName",   param_type: ParameterType::String, access: ParameterAccess::ReadOnly,  description: "Firmware code‑name" });
    
        /* ───────────────────────────── Configuration (0x2000) ──────────────────────────── */
        params.insert(0x2000, ParameterInfo { code: 0x2000, name: "echoPara1",          param_type: ParameterType::Uint16, access: ParameterAccess::Disposition, description: "Echo parameter 1" });
        params.insert(0x2001, ParameterInfo { code: 0x2001, name: "echoPara2",          param_type: ParameterType::Uint16, access: ParameterAccess::Disposition, description: "Echo parameter 2" });
        params.insert(0x2002, ParameterInfo { code: 0x2002, name: "echoPara3",          param_type: ParameterType::Uint16, access: ParameterAccess::Disposition, description: "Echo parameter 3" });
        params.insert(0x2003, ParameterInfo { code: 0x2003, name: "echoPara4",          param_type: ParameterType::Uint16, access: ParameterAccess::Disposition, description: "Echo parameter 4" });
        params.insert(0x2004, ParameterInfo { code: 0x2004, name: "echoFreHz",          param_type: ParameterType::Uint32, access: ParameterAccess::ReadWrite,   description: "Echo frequency (Hz)" });
        params.insert(0x2005, ParameterInfo { code: 0x2005, name: "MechOffset",         param_type: ParameterType::Float,  access: ParameterAccess::Settings,    description: "Mechanical encoder offset" });
        params.insert(0x2006, ParameterInfo { code: 0x2006, name: "status2_f32",       param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Reserved parameter (float)" });
        params.insert(0x2007, ParameterInfo { code: 0x2007, name: "limit_torque",       param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Maximum torque limit (Nm)" });
        params.insert(0x2008, ParameterInfo { code: 0x2008, name: "I_FW_MAX",           param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Field‑weakening current max" });
        params.insert(0x2009, ParameterInfo { code: 0x2009, name: "motor_baud",         param_type: ParameterType::Uint8,  access: ParameterAccess::Settings,    description: "Baud‑rate configuration flag" });
        params.insert(0x200A, ParameterInfo { code: 0x200A, name: "CAN_ID",             param_type: ParameterType::Uint8,  access: ParameterAccess::Settings,    description: "Node CAN‑ID" });
        params.insert(0x200B, ParameterInfo { code: 0x200B, name: "CAN_MASTER",         param_type: ParameterType::Uint8,  access: ParameterAccess::Settings,    description: "Master CAN‑ID" });
        params.insert(0x200C, ParameterInfo { code: 0x200C, name: "CAN_TIMEOUT",        param_type: ParameterType::Uint32, access: ParameterAccess::ReadWrite,   description: "CAN timeout threshold (µs)" });
        params.insert(0x200D, ParameterInfo { code: 0x200D, name: "status2_i16",       param_type: ParameterType::Int16,  access: ParameterAccess::ReadWrite,   description: "Reserved parameter (int16)" });
        params.insert(0x200E, ParameterInfo { code: 0x200E, name: "status3",            param_type: ParameterType::Uint32, access: ParameterAccess::ReadWrite,   description: "Reserved parameter (uint32)" });
        params.insert(0x200F, ParameterInfo { code: 0x200F, name: "status1",            param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Reserved parameter (float)" });
        params.insert(0x2010, ParameterInfo { code: 0x2010, name: "status6",            param_type: ParameterType::Uint8,  access: ParameterAccess::ReadWrite,   description: "Reserved parameter (uint8)" });
        params.insert(0x2011, ParameterInfo { code: 0x2011, name: "cur_filt_gain",      param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Current‑loop filter gain" });
        params.insert(0x2012, ParameterInfo { code: 0x2012, name: "cur_kp",             param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Current‑loop Kp" });
        params.insert(0x2013, ParameterInfo { code: 0x2013, name: "cur_ki",             param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Current‑loop Ki" });
        params.insert(0x2014, ParameterInfo { code: 0x2014, name: "spd_kp",             param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Speed‑loop Kp" });
        params.insert(0x2015, ParameterInfo { code: 0x2015, name: "spd_ki",             param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Speed‑loop Ki" });
        params.insert(0x2016, ParameterInfo { code: 0x2016, name: "loc_kp",             param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Position‑loop Kp" });
        params.insert(0x2017, ParameterInfo { code: 0x2017, name: "spd_filt_gain",      param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Speed‑loop filter gain" });
        params.insert(0x2018, ParameterInfo { code: 0x2018, name: "limit_spd",          param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Maximum speed limit (location mode)" });
        params.insert(0x2019, ParameterInfo { code: 0x2019, name: "limit_cur",          param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Current limit (loc/vel modes)" });
        params.insert(0x201A, ParameterInfo { code: 0x201A, name: "loc_ref_filt_gain",  param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Reserved parameter (float)" });
        params.insert(0x201B, ParameterInfo { code: 0x201B, name: "limit_loc",          param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Reserved parameter (float)" });
        params.insert(0x201C, ParameterInfo { code: 0x201C, name: "position_offset",    param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "High‑speed segment offset" });
        params.insert(0x201D, ParameterInfo { code: 0x201D, name: "chasu_angle_offset", param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Low‑speed segment offset" });
        params.insert(0x201E, ParameterInfo { code: 0x201E, name: "zero_sta",           param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Zero‑marker status" });
        params.insert(0x201F, ParameterInfo { code: 0x201F, name: "protocol_1",        param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Protocol flag" });
    
        /* ───────────────────────────── Timing diagnostics ──────────────────────────────── */
        params.insert(0x3000, ParameterInfo { code: 0x3000, name: "timeUse0",      param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Benchmark timer 0 (µs)" });
        params.insert(0x3001, ParameterInfo { code: 0x3001, name: "timeUse1",      param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite,   description: "Benchmark timer 1 (µs)" });
        params.insert(0x3002, ParameterInfo { code: 0x3002, name: "timeUse2",      param_type: ParameterType::Uint16, access: ParameterAccess::ReadOnly,    description: "Benchmark timer 2 (µs)" });
        params.insert(0x3003, ParameterInfo { code: 0x3003, name: "timeUse3",      param_type: ParameterType::Uint16, access: ParameterAccess::ReadOnly,    description: "Benchmark timer 3 (µs)" });
    
        /* ───────────────────────────── Telemetry & sensor values ───────────────────────── */
        params.insert(0x3004, ParameterInfo { code: 0x3004, name: "encoderRaw",        param_type: ParameterType::Uint16, access: ParameterAccess::ReadOnly,  description: "Magnetic encoder raw sample" });
        params.insert(0x3005, ParameterInfo { code: 0x3005, name: "mcuTemp",           param_type: ParameterType::Uint16, access: ParameterAccess::ReadOnly,  description: "MCU internal temperature (×0.1 °C)" });
        params.insert(0x3006, ParameterInfo { code: 0x3006, name: "motorTemp",         param_type: ParameterType::Int16,  access: ParameterAccess::ReadOnly,  description: "Motor NTC temperature (×0.1 °C)" });
        params.insert(0x3007, ParameterInfo { code: 0x3007, name: "vBus_mv",          param_type: ParameterType::Int16,  access: ParameterAccess::ReadOnly,  description: "Bus voltage (mV)" });
        params.insert(0x3008, ParameterInfo { code: 0x3008, name: "adc1Offset",        param_type: ParameterType::Int16,  access: ParameterAccess::ReadOnly,  description: "ADC channel‑1 zero‑current bias" });
        params.insert(0x3009, ParameterInfo { code: 0x3009, name: "adc2Offset",        param_type: ParameterType::Uint16, access: ParameterAccess::ReadOnly,  description: "ADC channel‑2 zero‑current bias" });
        params.insert(0x300A, ParameterInfo { code: 0x300A, name: "adc1Raw",           param_type: ParameterType::Int32,  access: ParameterAccess::ReadOnly,  description: "ADC channel‑1 raw value" });
        params.insert(0x300B, ParameterInfo { code: 0x300B, name: "adc2Raw",           param_type: ParameterType::Int32,  access: ParameterAccess::ReadOnly,  description: "ADC channel‑2 raw value" });
        params.insert(0x300C, ParameterInfo { code: 0x300C, name: "VBUS",              param_type: ParameterType::Uint16, access: ParameterAccess::ReadOnly,  description: "Bus voltage mirror (mV)" });
        params.insert(0x300D, ParameterInfo { code: 0x300D, name: "cmdId",             param_type: ParameterType::Uint16, access: ParameterAccess::ReadOnly,  description: "Command ring identifier" });
        params.insert(0x300E, ParameterInfo { code: 0x300E, name: "cmdIq",             param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Commanded iq (A)" });
        params.insert(0x300F, ParameterInfo { code: 0x300F, name: "cmdLocRef",         param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Commanded position reference" });
        params.insert(0x3010, ParameterInfo { code: 0x3010, name: "cmdSpdRef",         param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Commanded speed reference" });
        params.insert(0x3011, ParameterInfo { code: 0x3011, name: "cmdTorque",         param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Commanded torque (Nm)" });
        params.insert(0x3012, ParameterInfo { code: 0x3012, name: "cmdPos",            param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "MIT protocol position command" });
        params.insert(0x3013, ParameterInfo { code: 0x3013, name: "cmdVel",            param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "MIT protocol speed command" });
        params.insert(0x3014, ParameterInfo { code: 0x3014, name: "rotation",          param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Total rotations counted" });
        params.insert(0x3015, ParameterInfo { code: 0x3015, name: "modPos",            param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Modulo mechanical angle (rad)" });
        params.insert(0x3016, ParameterInfo { code: 0x3016, name: "mechPos",           param_type: ParameterType::Int16,  access: ParameterAccess::ReadOnly,  description: "Load mechanical angle (rad)" });
        params.insert(0x3017, ParameterInfo { code: 0x3017, name: "mechVel",           param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Load speed (rad/s)" });
        params.insert(0x3018, ParameterInfo { code: 0x3018, name: "elecPos",           param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Electrical angle (rad)" });
        params.insert(0x3019, ParameterInfo { code: 0x3019, name: "ia",                param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Phase‑U current (A)" });
        params.insert(0x301A, ParameterInfo { code: 0x301A, name: "ib",                param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Phase‑V current (A)" });
        params.insert(0x301B, ParameterInfo { code: 0x301B, name: "ic",                param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Phase‑W current (A)" });
        params.insert(0x301C, ParameterInfo { code: 0x301C, name: "timeout_cnt",       param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Timeout counter value" });
        params.insert(0x301D, ParameterInfo { code: 0x301D, name: "phaseOrder",        param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Phase order marker" });
        params.insert(0x301E, ParameterInfo { code: 0x301E, name: "iq_filter",         param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Filtered iq value" });
        params.insert(0x301F, ParameterInfo { code: 0x301F, name: "boardTemp",         param_type: ParameterType::Uint8,  access: ParameterAccess::ReadOnly,  description: "Board temperature (×0.1 °C)" });
        params.insert(0x3020, ParameterInfo { code: 0x3020, name: "iq",               param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Instantaneous iq (A)" });
        params.insert(0x3021, ParameterInfo { code: 0x3021, name: "id",               param_type: ParameterType::Int16,  access: ParameterAccess::ReadOnly,  description: "Instantaneous id (A)" });
        params.insert(0x3022, ParameterInfo { code: 0x3022, name: "faultSta",          param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Fault status flags" });
        params.insert(0x3023, ParameterInfo { code: 0x3023, name: "warnSta",           param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Warning status flags" });
        params.insert(0x3024, ParameterInfo { code: 0x3024, name: "drv_fault",         param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Driver fault value" });
        params.insert(0x3025, ParameterInfo { code: 0x3025, name: "drv_temp",          param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Driver temperature value" });
        params.insert(0x3026, ParameterInfo { code: 0x3026, name: "Uq",               param_type: ParameterType::Uint16, access: ParameterAccess::ReadOnly,  description: "Q‑axis voltage" });
        params.insert(0x3027, ParameterInfo { code: 0x3027, name: "Ud",               param_type: ParameterType::Int16,  access: ParameterAccess::ReadOnly,  description: "D‑axis voltage" });
        params.insert(0x3028, ParameterInfo { code: 0x3028, name: "dtc_u",            param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "PWM duty‑cycle phase‑U" });
        params.insert(0x3029, ParameterInfo { code: 0x3029, name: "dtc_v",            param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "PWM duty‑cycle phase‑V" });
        params.insert(0x302A, ParameterInfo { code: 0x302A, name: "dtc_w",            param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "PWM duty‑cycle phase‑W" });
        params.insert(0x302B, ParameterInfo { code: 0x302B, name: "v_bus",            param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Vbus (filtered)" });
        params.insert(0x302C, ParameterInfo { code: 0x302C, name: "torque_fdb",        param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Torque feedback (Nm)" });
        params.insert(0x302D, ParameterInfo { code: 0x302D, name: "rated_i",          param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Rated motor current (A)" });
        params.insert(0x302E, ParameterInfo { code: 0x302E, name: "limit_i",          param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Current limit (A)" });
        params.insert(0x302F, ParameterInfo { code: 0x302F, name: "spd_ref",          param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Speed reference (rad/s)" });
        params.insert(0x3030, ParameterInfo { code: 0x3030, name: "motor_mech_angle", param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Motor mechanical angle (rad)" });
        params.insert(0x3031, ParameterInfo { code: 0x3031, name: "position",         param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Position determination parameter" });
        params.insert(0x3032, ParameterInfo { code: 0x3032, name: "chasu_angle_init", param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Position determination parameter" });
        params.insert(0x3033, ParameterInfo { code: 0x3033, name: "chasu_angle_out",  param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Position determination parameter" });
        params.insert(0x3034, ParameterInfo { code: 0x3034, name: "motormechinit1",   param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Position determination parameter" });
        params.insert(0x3035, ParameterInfo { code: 0x3035, name: "mech_angle_init2", param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Position determination parameter" });
        params.insert(0x3036, ParameterInfo { code: 0x3036, name: "mech_angle_rotations", param_type: ParameterType::Float, access: ParameterAccess::ReadOnly, description: "Position determination parameter" });
        params.insert(0x3037, ParameterInfo { code: 0x3037, name: "cmdlocref_1",      param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Position determination parameter" });
        params.insert(0x3038, ParameterInfo { code: 0x3038, name: "status_1",         param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Retention parameter" });
        params.insert(0x3039, ParameterInfo { code: 0x3039, name: "ElecOffset",       param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Electrical angle offset" });
        params.insert(0x303A, ParameterInfo { code: 0x303A, name: "mcOverTemp",       param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "MC over‑temperature threshold" });
        params.insert(0x303B, ParameterInfo { code: 0x303B, name: "Kt_Nm_Amp",        param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Torque constant (Nm/A)" });
        params.insert(0x303C, ParameterInfo { code: 0x303C, name: "Tqcali_Type",      param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Torque calibration type" });
        params.insert(0x303D, ParameterInfo { code: 0x303D, name: "fault1",           param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Fault log entry 1" });
        params.insert(0x303E, ParameterInfo { code: 0x303E, name: "fault2",           param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Fault log entry 2" });
        params.insert(0x303F, ParameterInfo { code: 0x303F, name: "fault3",           param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Fault log entry 3" });
        params.insert(0x3040, ParameterInfo { code: 0x3040, name: "fault4",           param_type: ParameterType::Uint32, access: ParameterAccess::ReadOnly,  description: "Fault log entry 4" });
        params.insert(0x3041, ParameterInfo { code: 0x3041, name: "fault5",           param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Fault log entry 5" });
        params.insert(0x3042, ParameterInfo { code: 0x3042, name: "fault6",           param_type: ParameterType::Int16,  access: ParameterAccess::ReadOnly,  description: "Fault log entry 6" });
        params.insert(0x3043, ParameterInfo { code: 0x3043, name: "fault7",           param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Fault log entry 7" });
        params.insert(0x3044, ParameterInfo { code: 0x3044, name: "fault8",           param_type: ParameterType::Uint8,  access: ParameterAccess::ReadOnly,  description: "Fault log entry 8" });
        params.insert(0x3045, ParameterInfo { code: 0x3045, name: "theta_mech_1",     param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Mechanical angle θ1" });
    
        /* ───────────────────────────── Control mode parameters (0x7000) ─────────────────────── */
        params.insert(0x7005, ParameterInfo { code: 0x7005, name: "run_mode",        param_type: ParameterType::Uint8,  access: ParameterAccess::ReadWrite, description: "Operation mode: 0=operation, 1=position PP, 2=velocity, 3=operation, 5=position CSP" });
        params.insert(0x7006, ParameterInfo { code: 0x7006, name: "iq_ref",          param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Current mode Iq command (A)" });
        params.insert(0x700A, ParameterInfo { code: 0x700A, name: "spd_ref",         param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Rotational speed command (rad/s)" });
        params.insert(0x700B, ParameterInfo { code: 0x700B, name: "limit_torque",    param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Torque limit (Nm)" });
        params.insert(0x7010, ParameterInfo { code: 0x7010, name: "cur_kp",          param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Current loop Kp" });
        params.insert(0x7011, ParameterInfo { code: 0x7011, name: "cur_ki",          param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Current loop Ki" });
        params.insert(0x7014, ParameterInfo { code: 0x7014, name: "cur_filt_gain",   param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Current filter gain" });
        params.insert(0x7016, ParameterInfo { code: 0x7016, name: "loc_ref",         param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Position mode angle instruction (rad)" });
        params.insert(0x7017, ParameterInfo { code: 0x7017, name: "limit_spd",       param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Location mode CSP speed limit (rad/s)" });
        params.insert(0x7018, ParameterInfo { code: 0x7018, name: "limit_cur",       param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Velocity/position mode current limitation (A)" });
        params.insert(0x7019, ParameterInfo { code: 0x7019, name: "mechPos",         param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Mechanical angle of the loading coil (rad)" });
        params.insert(0x701A, ParameterInfo { code: 0x701A, name: "iqf",             param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Iq filter (A)" });
        params.insert(0x701B, ParameterInfo { code: 0x701B, name: "mechVel",         param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Speed of the load (rad/s)" });
        params.insert(0x701C, ParameterInfo { code: 0x701C, name: "VBUS",            param_type: ParameterType::Float,  access: ParameterAccess::ReadOnly,  description: "Bus voltage (V)" });
        params.insert(0x701E, ParameterInfo { code: 0x701E, name: "loc_kp",          param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Position loop Kp" });
        params.insert(0x701F, ParameterInfo { code: 0x701F, name: "spd_kp",          param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Speed loop Kp" });
        params.insert(0x7020, ParameterInfo { code: 0x7020, name: "spd_ki",          param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Speed loop Ki" });
        params.insert(0x7021, ParameterInfo { code: 0x7021, name: "spd_filt_gain",   param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Speed filter gain" });
        params.insert(0x7022, ParameterInfo { code: 0x7022, name: "acc_rad",         param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Velocity mode acceleration (rad/s²)" });
        params.insert(0x7024, ParameterInfo { code: 0x7024, name: "vel_max",         param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Location mode PP speed (rad/s)" });
        params.insert(0x7025, ParameterInfo { code: 0x7025, name: "acc_set",         param_type: ParameterType::Float,  access: ParameterAccess::ReadWrite, description: "Location mode PP acceleration (rad/s²)" });
        params.insert(0x7026, ParameterInfo { code: 0x7026, name: "EPScan_time",     param_type: ParameterType::Uint16, access: ParameterAccess::ReadWrite, description: "Report time (10ms units)" });
        params.insert(0x7028, ParameterInfo { code: 0x7028, name: "canTimeout",      param_type: ParameterType::Uint32, access: ParameterAccess::ReadWrite, description: "CAN timeout threshold (20000 = 1s)" });
        params.insert(0x7029, ParameterInfo { code: 0x7029, name: "zero_sta",        param_type: ParameterType::Uint8,  access: ParameterAccess::ReadWrite, description: "Zero flag bit: 0=0-2π, 1=-π-π" });

        
        params
    }

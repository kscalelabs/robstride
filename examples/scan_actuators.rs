//! Simple actuator scanner using built-in driver methods

use robstride_driver::RobstrideDriver;
use std::collections::HashMap;
use tracing::{info, warn};

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    info!("Scanning for Robstride actuators");

    // Scan all CAN interfaces for actuators
    let interfaces = ["can0", "can1", "can2", "can3", "can4"];
    let id_range = 10..=50;

    let discovered = RobstrideDriver::scan_multiple_interfaces(&interfaces, id_range).await?;

    if discovered.is_empty() {
        warn!("No actuators found on any interface");
        info!("Make sure CAN interfaces are up: sudo ip link set can0 up");
    } else {
        info!("Discovered actuators:");
        for (interface, actuators) in &discovered {
            info!(
                "  {}: {} actuators - {:?}",
                interface,
                actuators.len(),
                actuators
            );
        }

        let total: usize = discovered.values().map(|v| v.len()).sum();
        info!("Total: {} actuators", total);
    }

    Ok(())
}

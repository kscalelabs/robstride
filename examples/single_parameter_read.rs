//! Example demonstrating single parameter read functionality
//! 
//! This example shows how to read individual parameters from robstride actuators
//! using Communication type 17: Single parameter read.

use robstride::RobstrideDriver;
use std::time::Duration;
use tokio;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize the CAN interface and driver
    let mut driver = RobstrideDriver::new("can0").await?;
    
    // Scan for actuators
    println!("Scanning for actuators...");
    let actuators = driver.scan_actuators().await?;
    
    if actuators.is_empty() {
        println!("No actuators found!");
        return Ok(());
    }
    
    println!("Found {} actuator(s)", actuators.len());
    
    for &actuator_id in &actuators {
        println!("\n--- Reading parameters from actuator {} ---", actuator_id);
        
        // Read some common parameters using single parameter read
        let params_to_read = [
            (0x0000, "Name"),
            (0x0001, "BarCode"), 
            (0x200A, "CAN_ID"),
            (0x200B, "CAN_MASTER"),
            (0x2007, "limit_torque"),
            (0x2016, "loc_kp"),
        ];
        
        for (param_index, param_name) in params_to_read {
            match driver.read_single_parameter(actuator_id, param_index).await? {
                Some(value) => {
                    println!("  {}: {} = {}", param_name, param_index, value);
                }
                None => {
                    println!("  {}: {} = <no response>", param_name, param_index);
                }
            }
            
            // Small delay between reads
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
    }
    
    Ok(())
} 
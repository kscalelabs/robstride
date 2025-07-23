//! Debug parameter reading to understand why strings are blank

use robstride_driver::RobstrideDriver;
use robstride_driver::RobstrideActuatorType;
use tracing::info;

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::DEBUG)
        .init();

    info!("Parameter Debug Tool");
    
    let mut driver = RobstrideDriver::new("can0").await?;
    let actuator_id = 21; // Test with your known actuator


    if !driver.ping_actuator(actuator_id, RobstrideActuatorType::Robstride01).await? {
        println!("Actuator {} not found on can0", actuator_id);
        return Ok(());
    }
    println!("Discovered actuator {}", actuator_id);
    
    // Test specific parameters from the table
    let test_params = [
        (0x0000, "Name"),
        (0x0001, "BarCode"), 
        (0x1000, "BootCodeVersion"),
        (0x1001, "BootBuildDate"),
        (0x2005, "MechOffset"),
        (0x2007, "limit_torque"),
    ];
    
    for (param_index, name) in test_params {
        println!("\n{}", "=".repeat(50));
        println!("Testing parameter: {} (0x{:04X})", name, param_index);
        println!("{}", "=".repeat(50));
        
        match driver.read_all_params_debug(actuator_id).await {
            Ok(fragments) => {
                for (param_idx, byte_marker, data) in fragments {
                    println!("Param 0x{:04X} (marker 0x{:02X}): {:?}", 
                            param_idx, byte_marker, data);
                }
            }
            Err(e) => println!("Error: {}", e),
        }
        
        // Small delay between requests
        tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;
    }
    
    Ok(())
}
//! Parameter dump example

use robstride_driver::RobstrideDriver;

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt().init();
    
    let mut driver = RobstrideDriver::new("can0").await?;
    
    // First, find actuators
    let found = driver.scan_actuators(10..=50).await?;
    
    if found.is_empty() {
        println!("No actuators found");
        return Ok(());
    }
    
    println!("Found actuators: {:?}", found);
    
    // Dump parameters for first actuator found
    let actuator_id = found[0];
    
    // Read specific parameter
    match driver.read_parameter(actuator_id, 0x200a).await {
        Ok(value) => println!("CAN_ID parameter: {}", value),
        Err(e) => println!("Failed to read CAN_ID: {}", e),
    }
    
    // Full parameter dump
    driver.print_parameter_dump(actuator_id).await?;
    
    Ok(())
}
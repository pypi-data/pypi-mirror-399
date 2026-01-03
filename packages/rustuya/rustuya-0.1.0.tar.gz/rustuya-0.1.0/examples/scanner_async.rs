/**
 * Scanner Example (Async)
 *
 * This example demonstrates how to use the asynchronous UDP scanner to find
 * Tuya devices on the local network and detect their protocol versions.
 *
 * Author: 3735943886
 */
use rustuya::Scanner;
use std::time::Duration;

#[tokio::main]
async fn main() {
    // Initialize logger to see discovery details
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    println!("--- Rustuya - Scanner Async ---");
    println!("Scanning the network for Tuya devices (18s)...");

    // 1. Create a new scanner with a timeout of 18 seconds
    let scanner = Scanner::new().with_timeout(Duration::from_secs(18));

    // 2. Perform the scan
    match scanner.scan().await {
        Ok(devices) => {
            let count = devices.len();
            for dev in devices {
                println!("-------------------------------------------");
                // Mandatory fields
                println!("ID:      {}", dev.id);
                println!("IP:      {}", dev.ip);

                // Optional: Version
                if let Some(v) = dev.version {
                    println!("Version: {}", v);
                } else {
                    println!("Version: Unknown");
                }

                // Optional: Product Key
                if let Some(pk) = dev.product_key {
                    println!("Product: {}", pk);
                }
            }
            println!("-------------------------------------------");
            println!("\nTotal: {} devices found.", count);
        }
        Err(e) => {
            eprintln!("Scan failed: {}", e);
        }
    }
}

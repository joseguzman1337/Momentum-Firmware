use wifidevboarddetector::{detect_wifi_devboard, WifiDevboardState};

fn main() {
    match detect_wifi_devboard() {
        Ok(state) => {
            println!("{}", state);

            let code = match state {
                WifiDevboardState::NotDetected => 1,
                WifiDevboardState::GhostUsb { .. } => 2,
                _ => 0,
            };
            std::process::exit(code);
        }
        Err(e) => {
            eprintln!("Detection error: {}", e);
            std::process::exit(3);
        }
    }
}

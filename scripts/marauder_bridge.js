let serial = require("serial");
serial.setup("usart", 115200);

print("MARAUDER_BRIDGE_ACTIVE");

// Simple transparent bridge logic
while (true) {
    // Read from host (via CLI/USB) and write to ESP32
    // This is handled by the Python side sending commands to the bridge
    // The JS bridge just needs to stay alive and keep the UART open
    let data = serial.readAny(100);
    if (data) {
        print(data);
    }
}

serial.end();

/**
 * Autonomous Evolution: ESP32 AI OS (Neocortex)
 * Phase 1: RPC Foundation
 */

#include <Arduino.h>
#include <pb_decode.h>
#include <pb_encode.h>
#include "flipper.pb.h" // Generated from Flipper .proto

#define FLIPPER_SERIAL Serial1
#define RX_PIN         13 // Flipper TX
#define TX_PIN         14 // Flipper RX
#define BAUD_RATE      230400

void setup() {
    Serial.begin(115200); // Debug Serial
    FLIPPER_SERIAL.begin(BAUD_RATE, SERIAL_8N1, RX_PIN, TX_PIN);

    Serial.println("ESP32 Neocortex Initializing...");

    // Phase 1: Establish RPC Link
    delay(1000);
    FLIPPER_SERIAL.print("\r\n\r\n"); // Clear Flipper CLI
    delay(500);
    FLIPPER_SERIAL.print("start_rpc_session uart\r\n");
    Serial.println("Sent RPC start command to Flipper.");
}

bool send_rpc_message(const pb_msgdesc_t* fields, const void* src_struct) {
    uint8_t buffer[512];
    pb_ostream_t ostream = pb_ostream_from_buffer(buffer, sizeof(buffer));

    // Flipper RPC uses DELIMITED encoding (varint length prefix)
    if(!pb_encode_ex(&ostream, fields, src_struct, PB_ENCODE_DELIMITED)) {
        Serial.printf("Encoding failed: %s\n", PB_GET_ERROR(&ostream));
        return false;
    }

    FLIPPER_SERIAL.write(buffer, ostream.bytes_written);
    return true;
}

void loop() {
    static uint32_t last_info_req = 0;
    if(millis() - last_info_req > 5000) {
        last_info_req = millis();

        // Example: Send Ping or System Info request via RPC
        PB_Main rpc_msg = PB_Main_init_zero;
        rpc_msg.command_id = 1;
        rpc_msg.which_content = PB_Main_system_device_info_request_tag;

        if(send_rpc_message(PB_Main_fields, &rpc_msg)) {
            Serial.println("Sent SystemInfoRequest via RPC");
        }
    }

    // TODO: Implement RPC response decoding
    if(FLIPPER_SERIAL.available()) {
        char c = FLIPPER_SERIAL.read();
        // Serial.write(c); // Raw debug
    }
}

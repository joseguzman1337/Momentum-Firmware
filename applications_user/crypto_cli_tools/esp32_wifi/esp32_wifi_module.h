#pragma once

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <furi.h>

// ESP32 WiFi Module Types and Constants
#define ESP32_WIFI_MAX_SSID_LEN 32
#define ESP32_WIFI_MAX_PASSWORD_LEN 64
#define ESP32_WIFI_MAX_URL_LEN 256
#define ESP32_WIFI_MAX_POST_DATA_LEN 512
#define ESP32_WIFI_MAX_AP_RECORDS 10

typedef enum {
    ESP32_CMD_GET_STATUS = 0x01,
    ESP32_CMD_WIFI_SCAN = 0x02,
    ESP32_CMD_WIFI_CONNECT = 0x03,
    ESP32_CMD_WIFI_DISCONNECT = 0x04,
    ESP32_CMD_HTTP_GET = 0x05,
    ESP32_CMD_HTTP_POST = 0x06,
} Esp32CommandType;

typedef enum {
    ESP32_RESP_STATUS = 0x81,
    ESP32_RESP_ACK = 0x82,
    ESP32_RESP_NACK = 0x83,
    ESP32_RESP_WIFI_SCAN_RESULT = 0x84,
    ESP32_RESP_WIFI_SCAN_DONE = 0x85,
    ESP32_RESP_HTTP_START = 0x86,
    ESP32_RESP_HTTP_DATA = 0x87,
    ESP32_RESP_HTTP_END = 0x88,
} Esp32ResponseType;

typedef struct {
    char ssid[ESP32_WIFI_MAX_SSID_LEN];
    char password[ESP32_WIFI_MAX_PASSWORD_LEN];
} WifiConnectPayload;

typedef struct {
    char ssid[ESP32_WIFI_MAX_SSID_LEN];
    int8_t rssi;
    uint8_t channel;
    uint8_t auth_mode;
} wifi_ap_record_t;

// --- Application Interface Functions (6 functions from enumeration) ---
void app_get_esp32_status(void);
void app_wifi_scan_start(void);
void app_wifi_connect(const WifiConnectPayload* payload);
void app_wifi_disconnect(void);
void app_http_get_request(const char* url);
void app_http_post_request(const char* url, const char* post_data);

// --- UART Protocol Functions (12 functions) ---
void uart_protocol_init(void);
void uart_protocol_process_commands(void);
void uart_protocol_send_packet(Esp32ResponseType response_type, const uint8_t* payload, uint16_t payload_len);
void uart_protocol_send_status(uint8_t wifi_connected, uint32_t ip_address);
void uart_protocol_send_wifi_scan_result(const wifi_ap_record_t* ap_info);
void uart_protocol_send_wifi_scan_done(void);
void uart_protocol_send_ack(Esp32CommandType for_command);
void uart_protocol_send_nack(Esp32CommandType for_command, const char* error_message);
void uart_protocol_send_http_response_start(uint16_t status_code);
void uart_protocol_send_http_response_data(const uint8_t* data, uint16_t len);
void uart_protocol_send_http_response_end(void);
uint8_t uart_calculate_checksum(const uint8_t* data, uint16_t len);

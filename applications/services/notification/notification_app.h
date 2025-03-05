#include <furi.h>
#include <furi_hal.h>
#include "notification.h"
#include "notification_messages.h"
#include "notification_settings_filename.h"

#define NOTIFICATION_LED_COUNT      3
#define NOTIFICATION_EVENT_COMPLETE 0x00000001U

typedef enum {
    NotificationLayerMessage,
    InternalLayerMessage,
    SaveSettingsMessage,
    LoadSettingsMessage,
} NotificationAppMessageType;

typedef struct {
    const NotificationSequence* sequence;
    NotificationAppMessageType type;
    FuriEventFlag* back_event;
} NotificationAppMessage;

typedef enum {
    LayerInternal = 0,
    LayerNotification = 1,
    LayerMAX = 2,
} NotificationLedLayerIndex;

typedef struct {
    uint8_t value_last[LayerMAX];
    uint8_t value[LayerMAX];
    NotificationLedLayerIndex index;
    Light light;
} NotificationLedLayer;

#define NOTIFICATION_SETTINGS_VERSION 0x03
#define NOTIFICATION_SETTINGS_PATH    INT_PATH(NOTIFICATION_SETTINGS_FILE_NAME)

typedef struct {
    uint8_t version;
    float display_brightness;
    float led_brightness;
    float speaker_volume;
    uint32_t display_off_delay_ms;
    int8_t contrast;
    bool vibro_on;
    
    bool rgb_mod_installed;
    bool rgb_mod_rainbow;
    uint32_t rgb_mod_rainbow_speed_ms;
    uint16_t rgb_mod_rainbow_step;

} NotificationSettings;

struct NotificationApp {
    FuriMessageQueue* queue;
    FuriPubSub* event_record;
    FuriTimer* display_timer;

    NotificationLedLayer display;
    NotificationLedLayer led[NOTIFICATION_LED_COUNT];
    uint8_t display_led_lock;

    // rainbow mode section
    FuriTimer* rgb_mod_rainbow_timer;
    uint16_t rgb_mod_rainbow_red;
    uint16_t rgb_mod_rainbow_green;
    uint16_t rgb_mod_rainbow_blue;
  
    NotificationSettings settings;
};

void notification_message_save_settings(NotificationApp* app);

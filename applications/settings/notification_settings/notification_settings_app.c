#include <furi.h>
#include <furi_hal_rtc.h>
#include <notification/notification_app.h>
#include <gui/modules/variable_item_list.h>
#include <gui/view_dispatcher.h>
#include <lib/toolbox/value_index.h>
#include <applications/settings/notification_settings/rgb_backlight.h>

#define MAX_NOTIFICATION_SETTINGS 4

typedef struct {
    NotificationApp* notification;
    Gui* gui;
    ViewDispatcher* view_dispatcher;
    VariableItemList* variable_item_list;
    VariableItemList* variable_item_list_rgb;
} NotificationAppSettings;

static VariableItem* temp_item;

static const NotificationSequence sequence_note_c = {
    &message_note_c5,
    &message_delay_100,
    &message_sound_off,
    NULL,
};

#define CONTRAST_COUNT 17
const char* const contrast_text[CONTRAST_COUNT] = {
    "-8",
    "-7",
    "-6",
    "-5",
    "-4",
    "-3",
    "-2",
    "-1",
    "0",
    "+1",
    "+2",
    "+3",
    "+4",
    "+5",
    "+6",
    "+7",
    "+8",
};
const int32_t contrast_value[CONTRAST_COUNT] = {
    -8,
    -7,
    -6,
    -5,
    -4,
    -3,
    -2,
    -1,
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
};

#define BACKLIGHT_COUNT 21
const char* const backlight_text[BACKLIGHT_COUNT] = {
    "0%",  "5%",  "10%", "15%", "20%", "25%", "30%", "35%", "40%", "45%",  "50%",
    "55%", "60%", "65%", "70%", "75%", "80%", "85%", "90%", "95%", "100%",
};
const float backlight_value[BACKLIGHT_COUNT] = {
    0.00f, 0.05f, 0.10f, 0.15f, 0.20f, 0.25f, 0.30f, 0.35f, 0.40f, 0.45f, 0.50f,
    0.55f, 0.60f, 0.65f, 0.70f, 0.75f, 0.80f, 0.85f, 0.90f, 0.95f, 1.00f,
};

#define VOLUME_COUNT 21
const char* const volume_text[VOLUME_COUNT] = {
    "0%",  "5%",  "10%", "15%", "20%", "25%", "30%", "35%", "40%", "45%",  "50%",
    "55%", "60%", "65%", "70%", "75%", "80%", "85%", "90%", "95%", "100%",
};
const float volume_value[VOLUME_COUNT] = {
    0.00f, 0.05f, 0.10f, 0.15f, 0.20f, 0.25f, 0.30f, 0.35f, 0.40f, 0.45f, 0.50f,
    0.55f, 0.60f, 0.65f, 0.70f, 0.75f, 0.80f, 0.85f, 0.90f, 0.95f, 1.00f,
};

#define DELAY_COUNT 11
const char* const delay_text[DELAY_COUNT] = {
    "1s",
    "5s",
    "10s",
    "15s",
    "30s",
    "60s",
    "90s",
    "120s",
    "5min",
    "10min",
    "30min",
};
const uint32_t delay_value[DELAY_COUNT] =
    {1000, 5000, 10000, 15000, 30000, 60000, 90000, 120000, 300000, 600000, 1800000};

#define VIBRO_COUNT 2
const char* const vibro_text[VIBRO_COUNT] = {
    "OFF",
    "ON",
};
const bool vibro_value[VIBRO_COUNT] = {false, true};

// --- RGB MOD RAINBOW ---
#define RGB_MOD_COUNT 2
const char* const rgb_mod_text[RGB_MOD_COUNT] = {
    "OFF",
    "ON",
};
const bool rgb_mod_value[RGB_MOD_COUNT] = {false, true};

#define RGB_MOD_RAINBOW_MODE_COUNT 2
const char* const rgb_mod_rainbow_mode_text[RGB_MOD_RAINBOW_MODE_COUNT] = {
    "OFF",
    "Rainbow",
};
const uint32_t rgb_mod_rainbow_mode_value[RGB_MOD_RAINBOW_MODE_COUNT] = {0, 1};

#define RGB_MOD_RAINBOW_SPEED_COUNT 20
const char* const rgb_mod_rainbow_speed_text[RGB_MOD_RAINBOW_SPEED_COUNT] = {
    "0.1s", "0.2s", "0.3s", "0.4s", "0.5s", "0.6s", "0.7",  "0.8",  "0.9",  "1s",
    "1.1s", "1.2s", "1.3s", "1.4s", "1.5s", "1.6s", "1.7s", "1.8s", "1.9s", "2s"};
const uint32_t rgb_mod_rainbow_speed_value[RGB_MOD_RAINBOW_SPEED_COUNT] = {
    100,  200,  300,  400,  500,  600,  700,  800,  900,  1000,
    1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000};

#define RGB_MOD_RAINBOW_STEP_COUNT 10
const char* const rgb_mod_rainbow_step_text[RGB_MOD_RAINBOW_SPEED_COUNT] = {
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
};
const uint32_t rgb_mod_rainbow_step_value[RGB_MOD_RAINBOW_STEP_COUNT] =
    {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

typedef enum {
    MainViewId,
    RGBViewId,
} ViewId;

// --- END OF RGB MOD RAINBOW ---

static void contrast_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);

    variable_item_set_current_value_text(item, contrast_text[index]);
    app->notification->settings.contrast = contrast_value[index];
    notification_message(app->notification, &sequence_lcd_contrast_update);
}

static void backlight_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);

    variable_item_set_current_value_text(item, backlight_text[index]);
    app->notification->settings.display_brightness = backlight_value[index];
    notification_message(app->notification, &sequence_display_backlight_on);
}

static void screen_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);

    variable_item_set_current_value_text(item, delay_text[index]);
    app->notification->settings.display_off_delay_ms = delay_value[index];
    notification_message(app->notification, &sequence_display_backlight_on);
}

const NotificationMessage apply_message = {
    .type = NotificationMessageTypeLedBrightnessSettingApply,
};
const NotificationSequence apply_sequence = {
    &apply_message,
    NULL,
};

static void led_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);

    variable_item_set_current_value_text(item, backlight_text[index]);
    app->notification->settings.led_brightness = backlight_value[index];
    notification_message(app->notification, &apply_sequence);
    notification_internal_message(app->notification, &apply_sequence);
    notification_message(app->notification, &sequence_blink_white_100);
}

static void volume_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);

    variable_item_set_current_value_text(item, volume_text[index]);
    app->notification->settings.speaker_volume = volume_value[index];
    notification_message(app->notification, &sequence_note_c);
}

static void vibro_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);

    variable_item_set_current_value_text(item, vibro_text[index]);
    app->notification->settings.vibro_on = vibro_value[index];
    notification_message(app->notification, &sequence_single_vibro);
}

// --- RGB MOD AND RAINBOW ---

static void rgb_mod_installed_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);
    variable_item_set_current_value_text(item, rgb_mod_text[index]);
    app->notification->settings.rgb_mod_installed = rgb_mod_value[index];
}

static void rgb_mod_rainbow_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);
    variable_item_set_current_value_text(item, rgb_mod_rainbow_mode_text[index]);
    app->notification->settings.rgb_mod_rainbow_mode = rgb_mod_rainbow_mode_value[index];

    // Lock/Unlock color settings if rainbow mode Enabled/Disabled
    for(int i = 0; i < 4; i++) {
        VariableItem* t_item = variable_item_list_get(app->variable_item_list_rgb, i);
        if(app->notification->settings.rgb_mod_rainbow_mode > 0) {
            variable_item_set_locked(t_item, true, "Rainbow mode\nenabled!");
        } else {
            variable_item_set_locked(t_item, false, "Rainbow mode\nenabled!");
        }
    }
    //save settings and start/stop rgb_mod_rainbow_timer
    notification_message_save_settings(app->notification);

    // restore saved rgb backlight settings if we switch_off rainbow mode
    if(app->notification->settings.rgb_mod_rainbow_mode == 0) {
        rgb_backlight_update(app->notification->settings.display_brightness * 255, true);
    }
}

static void rgb_mod_rainbow_speed_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);
    variable_item_set_current_value_text(item, rgb_mod_rainbow_speed_text[index]);
    app->notification->settings.rgb_mod_rainbow_speed_ms = rgb_mod_rainbow_speed_value[index];
    //use message for restart rgb_mod_rainbow_timer with new delay
    notification_message_save_settings(app->notification);
}

static void rgb_mod_rainbow_step_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);
    variable_item_set_current_value_text(item, rgb_mod_rainbow_step_text[index]);
    app->notification->settings.rgb_mod_rainbow_step = rgb_mod_rainbow_step_value[index];
}

// Set RGB backlight color
static void color_changed(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);
    rgb_backlight_set_color(index);
    variable_item_set_current_value_text(item, rgb_backlight_get_color_text(index));
    notification_message(app->notification, &sequence_display_backlight_on);
}

// TODO: refactor and fix this
static void color_set_custom_red(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);
    rgb_backlight_set_custom_color(index, 0);
    char valtext[4] = {};
    snprintf(valtext, sizeof(valtext), "%d", index);
    variable_item_set_current_value_text(item, valtext);
    rgb_backlight_set_color(13);
    rgb_backlight_update(app->notification->settings.display_brightness * 0xFF, true);
    // Set to custom color explicitly
    variable_item_set_current_value_index(temp_item, 13);
    variable_item_set_current_value_text(temp_item, rgb_backlight_get_color_text(13));
    notification_message(app->notification, &sequence_display_backlight_on);
}
static void color_set_custom_green(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);
    rgb_backlight_set_custom_color(index, 1);
    char valtext[4] = {};
    snprintf(valtext, sizeof(valtext), "%d", index);
    variable_item_set_current_value_text(item, valtext);
    rgb_backlight_set_color(13);
    rgb_backlight_update(app->notification->settings.display_brightness * 0xFF, true);
    // Set to custom color explicitly
    variable_item_set_current_value_index(temp_item, 13);
    variable_item_set_current_value_text(temp_item, rgb_backlight_get_color_text(13));
    notification_message(app->notification, &sequence_display_backlight_on);
}
static void color_set_custom_blue(VariableItem* item) {
    NotificationAppSettings* app = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);
    rgb_backlight_set_custom_color(index, 2);
    char valtext[4] = {};
    snprintf(valtext, sizeof(valtext), "%d", index);
    variable_item_set_current_value_text(item, valtext);
    rgb_backlight_set_color(13);
    rgb_backlight_update(app->notification->settings.display_brightness * 0xFF, true);
    // Set to custom color explicitly
    variable_item_set_current_value_index(temp_item, 13);
    variable_item_set_current_value_text(temp_item, rgb_backlight_get_color_text(13));
    notification_message(app->notification, &sequence_display_backlight_on);
}

// open rgb_settings_view if user press OK on first (index=0) menu string and (debug mode or rgb_mod_install is true)
void variable_item_list_enter_callback(void* context, uint32_t index) {
    UNUSED(context);
    NotificationAppSettings* app = context;

    if(((app->notification->settings.rgb_mod_installed) ||
        (furi_hal_rtc_is_flag_set(FuriHalRtcFlagDebug))) &&
       (index == 0)) {
        view_dispatcher_switch_to_view(app->view_dispatcher, RGBViewId);
    }
}

// switch to main view on exit from rgb_settings_view
static uint32_t notification_app_rgb_settings_exit(void* context) {
    UNUSED(context);
    return MainViewId;
}
// --- END OF RGB MOD AND RAINBOW ---

static uint32_t notification_app_settings_exit(void* context) {
    UNUSED(context);
    return VIEW_NONE;
}

static NotificationAppSettings* alloc_settings(void) {
    NotificationAppSettings* app = malloc(sizeof(NotificationAppSettings));
    app->notification = furi_record_open(RECORD_NOTIFICATION);
    app->gui = furi_record_open(RECORD_GUI);

    app->variable_item_list = variable_item_list_alloc();
    View* view = variable_item_list_get_view(app->variable_item_list);

    //set callback for exit from view
    view_set_previous_callback(view, notification_app_settings_exit);

    // set callback for OK pressed in menu
    variable_item_list_set_enter_callback(
        app->variable_item_list, variable_item_list_enter_callback, app);

    VariableItem* item;
    uint8_t value_index;

    //Show RGB settings only when debug_mode or rgb_mod_installed is active
    if((app->notification->settings.rgb_mod_installed) ||
       (furi_hal_rtc_is_flag_set(FuriHalRtcFlagDebug))) {
        item = variable_item_list_add(app->variable_item_list, "RGB mod settings", 0, NULL, app);
    }

    item = variable_item_list_add(
        app->variable_item_list, "LCD Contrast", CONTRAST_COUNT, contrast_changed, app);
    value_index =
        value_index_int32(app->notification->settings.contrast, contrast_value, CONTRAST_COUNT);
    variable_item_set_current_value_index(item, value_index);
    variable_item_set_current_value_text(item, contrast_text[value_index]);

    item = variable_item_list_add(
        app->variable_item_list, "LCD Brightness", BACKLIGHT_COUNT, backlight_changed, app);
    value_index = value_index_float(
        app->notification->settings.display_brightness, backlight_value, BACKLIGHT_COUNT);
    variable_item_set_current_value_index(item, value_index);
    variable_item_set_current_value_text(item, backlight_text[value_index]);

    item = variable_item_list_add(
        app->variable_item_list, "Backlight Time", DELAY_COUNT, screen_changed, app);
    value_index = value_index_uint32(
        app->notification->settings.display_off_delay_ms, delay_value, DELAY_COUNT);
    variable_item_set_current_value_index(item, value_index);
    variable_item_set_current_value_text(item, delay_text[value_index]);

    item = variable_item_list_add(
        app->variable_item_list, "LED Brightness", BACKLIGHT_COUNT, led_changed, app);
    value_index = value_index_float(
        app->notification->settings.led_brightness, backlight_value, BACKLIGHT_COUNT);
    variable_item_set_current_value_index(item, value_index);
    variable_item_set_current_value_text(item, backlight_text[value_index]);

    if(furi_hal_rtc_is_flag_set(FuriHalRtcFlagStealthMode)) {
        item = variable_item_list_add(app->variable_item_list, "Volume", 1, NULL, app);
        value_index = 0;
        variable_item_set_current_value_index(item, value_index);
        variable_item_set_current_value_text(item, "Stealth");
    } else {
        item = variable_item_list_add(
            app->variable_item_list, "Volume", VOLUME_COUNT, volume_changed, app);
        value_index = value_index_float(
            app->notification->settings.speaker_volume, volume_value, VOLUME_COUNT);
        variable_item_set_current_value_index(item, value_index);
        variable_item_set_current_value_text(item, volume_text[value_index]);
    }

    if(furi_hal_rtc_is_flag_set(FuriHalRtcFlagStealthMode)) {
        item = variable_item_list_add(app->variable_item_list, "Vibro", 1, NULL, app);
        value_index = 0;
        variable_item_set_current_value_index(item, value_index);
        variable_item_set_current_value_text(item, "Stealth");
    } else {
        item = variable_item_list_add(
            app->variable_item_list, "Vibro", VIBRO_COUNT, vibro_changed, app);
        value_index =
            value_index_bool(app->notification->settings.vibro_on, vibro_value, VIBRO_COUNT);
        variable_item_set_current_value_index(item, value_index);
        variable_item_set_current_value_text(item, vibro_text[value_index]);
    }

    // --- RGB SETTINGS VIEW ---
    app->variable_item_list_rgb = variable_item_list_alloc();
    View* view_rgb = variable_item_list_get_view(app->variable_item_list_rgb);
    // set callback for OK pressed in rgb_settings_menu
    view_set_previous_callback(view_rgb, notification_app_rgb_settings_exit);

    // Show RGB_MOD_Installed_Swith only in Debug mode
    if(furi_hal_rtc_is_flag_set(FuriHalRtcFlagDebug)) {
        item = variable_item_list_add(
            app->variable_item_list_rgb,
            "RGB MOD Installed",
            RGB_MOD_COUNT,
            rgb_mod_installed_changed,
            app);
        value_index = value_index_bool(
            app->notification->settings.rgb_mod_installed, rgb_mod_value, RGB_MOD_COUNT);
        variable_item_set_current_value_index(item, value_index);
        variable_item_set_current_value_text(item, rgb_mod_text[value_index]);
    }

    // RGB Colors settings
    item = variable_item_list_add(
        app->variable_item_list_rgb,
        "LCD Color",
        rgb_backlight_get_color_count(),
        color_changed,
        app);
    value_index = rgb_backlight_get_settings()->display_color_index;
    variable_item_set_current_value_index(item, value_index);
    variable_item_set_current_value_text(item, rgb_backlight_get_color_text(value_index));
    variable_item_set_locked(
        item, (app->notification->settings.rgb_mod_rainbow_mode > 0), "Rainbow mode\nenabled!");
    temp_item = item;

    // Custom Color - REFACTOR THIS
    item = variable_item_list_add(
        app->variable_item_list_rgb, "Custom Red", 255, color_set_custom_red, app);
    value_index = rgb_backlight_get_settings()->custom_r;
    variable_item_set_current_value_index(item, value_index);
    char valtext[4] = {};
    snprintf(valtext, sizeof(valtext), "%d", value_index);
    variable_item_set_current_value_text(item, valtext);
    variable_item_set_locked(
        item, (app->notification->settings.rgb_mod_rainbow_mode > 0), "Rainbow mode\nenabled!");

    item = variable_item_list_add(
        app->variable_item_list_rgb, "Custom Green", 255, color_set_custom_green, app);
    value_index = rgb_backlight_get_settings()->custom_g;
    variable_item_set_current_value_index(item, value_index);
    snprintf(valtext, sizeof(valtext), "%d", value_index);
    variable_item_set_current_value_text(item, valtext);
    variable_item_set_locked(
        item, (app->notification->settings.rgb_mod_rainbow_mode > 0), "Rainbow mode\nenabled!");

    item = variable_item_list_add(
        app->variable_item_list_rgb, "Custom Blue", 255, color_set_custom_blue, app);
    value_index = rgb_backlight_get_settings()->custom_b;
    variable_item_set_current_value_index(item, value_index);
    snprintf(valtext, sizeof(valtext), "%d", value_index);
    variable_item_set_current_value_text(item, valtext);
    variable_item_set_locked(
        item, (app->notification->settings.rgb_mod_rainbow_mode > 0), "Rainbow mode\nenabled!");

    // Rainbow (based on Willy-JL idea) settings
    item = variable_item_list_add(
        app->variable_item_list_rgb,
        "Rainbow mode",
        RGB_MOD_RAINBOW_MODE_COUNT,
        rgb_mod_rainbow_changed,
        app);
    value_index = value_index_uint32(
        app->notification->settings.rgb_mod_rainbow_mode,
        rgb_mod_rainbow_mode_value,
        RGB_MOD_RAINBOW_MODE_COUNT);
    variable_item_set_current_value_index(item, value_index);
    variable_item_set_current_value_text(item, rgb_mod_rainbow_mode_text[value_index]);

    item = variable_item_list_add(
        app->variable_item_list_rgb,
        "Rainbow speed",
        RGB_MOD_RAINBOW_SPEED_COUNT,
        rgb_mod_rainbow_speed_changed,
        app);
    value_index = value_index_uint32(
        app->notification->settings.rgb_mod_rainbow_speed_ms,
        rgb_mod_rainbow_speed_value,
        RGB_MOD_RAINBOW_SPEED_COUNT);
    variable_item_set_current_value_index(item, value_index);
    variable_item_set_current_value_text(item, rgb_mod_rainbow_speed_text[value_index]);

    item = variable_item_list_add(
        app->variable_item_list_rgb,
        "Rainbow step",
        RGB_MOD_RAINBOW_STEP_COUNT,
        rgb_mod_rainbow_step_changed,
        app);
    value_index = value_index_uint32(
        app->notification->settings.rgb_mod_rainbow_step,
        rgb_mod_rainbow_step_value,
        RGB_MOD_RAINBOW_SPEED_COUNT);
    variable_item_set_current_value_index(item, value_index);
    variable_item_set_current_value_text(item, rgb_mod_rainbow_step_text[value_index]);

    // --- End of RGB SETTING VIEW ---

    app->view_dispatcher = view_dispatcher_alloc();
    view_dispatcher_attach_to_gui(app->view_dispatcher, app->gui, ViewDispatcherTypeFullscreen);
    view_dispatcher_add_view(app->view_dispatcher, MainViewId, view);
    view_dispatcher_add_view(app->view_dispatcher, RGBViewId, view_rgb);
    view_dispatcher_switch_to_view(app->view_dispatcher, MainViewId);
    return app;
}

static void free_settings(NotificationAppSettings* app) {
    view_dispatcher_remove_view(app->view_dispatcher, MainViewId);
    view_dispatcher_remove_view(app->view_dispatcher, RGBViewId);
    variable_item_list_free(app->variable_item_list);
    variable_item_list_free(app->variable_item_list_rgb);
    view_dispatcher_free(app->view_dispatcher);

    furi_record_close(RECORD_GUI);
    furi_record_close(RECORD_NOTIFICATION);
    free(app);
}

int32_t notification_settings_app(void* p) {
    UNUSED(p);
    NotificationAppSettings* app = alloc_settings();
    view_dispatcher_run(app->view_dispatcher);
    notification_message_save_settings(app->notification);

    // Automaticaly switch_off debug_mode when user exit from settings with enabled rgb_mod_installed
    // if(app->notification->settings.rgb_mod_installed) {
    //     furi_hal_rtc_reset_flag(FuriHalRtcFlagDebug);
    // }

    free_settings(app);
    return 0;
}

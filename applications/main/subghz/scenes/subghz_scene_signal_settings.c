#include "../subghz_i.h"
#include "subghz/types.h"
#include "../helpers/subghz_custom_event.h"
#include <dolphin/dolphin.h>
#include <lib/toolbox/value_index.h>

#define TAG "SubGhzSceneSignalSettings"

char * protocol_counter_allowed = "";
uint8_t counter_mode = 0xff;

#define COUNTER_MODE_COUNT 7
const char* const counter_mode_text[COUNTER_MODE_COUNT] = {
    "System",
    "Mode 1",
    "Mode 2",
    "Mode 3",
    "Mode 4",
    "Mode 5",
    "Mode 6",
};

const int32_t counter_mode_value[COUNTER_MODE_COUNT] = {
    0,
    1,
    2,
    3,
    4,
    5,
    6,
};

void subghz_scene_signal_settings_counter_mode_changed (VariableItem* item){
    SubGhz* subghz = variable_item_get_context(item);
    UNUSED (subghz);
    uint8_t index = variable_item_get_current_value_index(item);
    variable_item_set_current_value_text(item, counter_mode_text[index]);
    counter_mode = counter_mode_value[index];

}

void subghz_scene_signal_settings_on_enter(void* context) {
    // when we open saved file we do some check and fill up subghz->filepath. So now we use it to check is CounterMode in file
    SubGhz* subghz = context;

    FuriString* tmp_string = furi_string_alloc();
    const char* file_path = furi_string_get_cstr(subghz->file_path);

    furi_assert(subghz);
    furi_assert(file_path);

    Storage* storage = furi_record_open(RECORD_STORAGE);
    FlipperFormat* fff_data_file = flipper_format_file_alloc(storage);
    uint32_t tmp_counter_mode = 0;
    counter_mode = 0xff;

    if(!flipper_format_file_open_existing(fff_data_file, file_path)) {
        FURI_LOG_E(TAG, "Error open file %s", file_path);
    } else {
        flipper_format_read_string(fff_data_file, "Protocol", tmp_string);
        if((!strcmp(furi_string_get_cstr(tmp_string), "Nice FloR-S")) ||
           (!strcmp(furi_string_get_cstr(tmp_string), "CAME Atomo")) ||
           (!strcmp(furi_string_get_cstr(tmp_string), "Alutech AT-4N")) ||
           (!strcmp(furi_string_get_cstr(tmp_string), "KeeLoq")) ) {

                if(flipper_format_read_uint32(fff_data_file, "CounterMode", &tmp_counter_mode, 1)) {
                    counter_mode = (uint8_t)tmp_counter_mode;
                } else {
                    counter_mode = 0;
                }
            }
    }
    FURI_LOG_I(TAG, "CounterMode %i", counter_mode);

    furi_string_free(tmp_string);
    flipper_format_free(fff_data_file);
    furi_record_close(RECORD_STORAGE);

    VariableItemList* variable_item_list = subghz->variable_item_list;
    int32_t value_index;
    VariableItem* item;
    int32_t available_count = COUNTER_MODE_COUNT;

    item = variable_item_list_add(
        variable_item_list,
        "Counter Mode",
        available_count,
        subghz_scene_signal_settings_counter_mode_changed,
        subghz);
    value_index = value_index_int32(
        counter_mode,
        counter_mode_value,
        available_count);

    variable_item_set_current_value_index(item, value_index);
    variable_item_set_current_value_text(item, counter_mode_text[value_index]);
    variable_item_set_locked(item,(counter_mode == 0xff)," Not available \n for this \nprotocol !");

    view_dispatcher_switch_to_view(subghz->view_dispatcher, SubGhzViewIdVariableItemList);
}

bool subghz_scene_signal_settings_on_event(void* context, SceneManagerEvent event) {
    SubGhz* subghz = context;
    if(event.type == SceneManagerEventTypeBack) {
        scene_manager_previous_scene(subghz->scene_manager);
        return true;
        }
        else return false;
    }


void subghz_scene_signal_settings_on_exit(void* context) {
    SubGhz* subghz = context;
    variable_item_list_set_selected_item(subghz->variable_item_list, 0);
    variable_item_list_reset(subghz->variable_item_list);
}

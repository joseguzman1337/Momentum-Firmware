#include "../subghz_i.h"
#include "subghz/types.h"
#include "../helpers/subghz_custom_event.h"
#include <lib/subghz/protocols/raw.h>
#include <gui/modules/validators.h>
#include <dolphin/dolphin.h>
#include <toolbox/name_generator.h>

void subghz_scene_signal_settings_text_input_callback(void* context) {
    furi_assert(context);
    SubGhz* subghz = context;
    view_dispatcher_send_custom_event(subghz->view_dispatcher, SubGhzCustomEventSceneSignalSettings);
}

void subghz_scene_signal_settings_on_enter(void* context) {
    SubGhz* subghz = context;

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

}

#include "../subghz_i.h"
#include "../helpers/subghz_txrx_create_protocol_key.h"

#define TAG "SubGhzSetButton"

void subghz_scene_set_button_byte_input_callback(void* context) {
    SubGhz* subghz = context;

    view_dispatcher_send_custom_event(subghz->view_dispatcher, SubGhzCustomEventByteInputDone);
}

void subghz_scene_set_button_on_enter(void* context) {
    SubGhz* subghz = context;
    // Set default value (button 1) for first use
    subghz->secure_data->btn = 0x01;

    // Setup view
    ByteInput* byte_input = subghz->byte_input;
    byte_input_set_header_text(byte_input, "Enter BUTTON in hex");
    byte_input_set_result_callback(
        byte_input,
        subghz_scene_set_button_byte_input_callback,
        NULL,
        subghz,
        &subghz->secure_data->btn,
        1);
    view_dispatcher_switch_to_view(subghz->view_dispatcher, SubGhzViewIdByteInput);
}

bool subghz_scene_set_button_on_event(void* context, SceneManagerEvent event) {
    SubGhz* subghz = context;
    bool consumed = false;
    bool generated_protocol = false;

    if(event.type == SceneManagerEventTypeCustom) {
        if(event.event == SubGhzCustomEventByteInputDone) {
            SetType state =
                scene_manager_get_scene_state(subghz->scene_manager, SubGhzSceneSetType);

            if (state == SetTypeNiceFlorS_433_92 || state == SetTypeNiceOne_433_92) {
                uint64_t key = (uint64_t)rand();

                generated_protocol = subghz_txrx_gen_nice_flor_s_protocol(
                    subghz->txrx,
                    "AM650",
                    433920000,
                    key & 0x0FFFFFFF,
                    subghz->secure_data->btn,
                    0x03,
                    state == SetTypeNiceOne_433_92
                );

                if(!generated_protocol) {
                    furi_string_set(
                        subghz->error_str, "Function requires\nan SD card with\nfresh databases.");
                    scene_manager_next_scene(subghz->scene_manager, SubGhzSceneShowError);
                }

                consumed = true;
            }
        }

        // Reset Seed, Fix, Cnt, Btn in secure data after successful or unsuccessful generation
        memset(subghz->secure_data->seed, 0, sizeof(subghz->secure_data->seed));
        memset(subghz->secure_data->cnt, 0, sizeof(subghz->secure_data->cnt));
        memset(subghz->secure_data->fix, 0, sizeof(subghz->secure_data->fix));
        subghz->secure_data->btn = 0x01;


        if(generated_protocol) {
            subghz_file_name_clear(subghz);

            scene_manager_set_scene_state(
                subghz->scene_manager, SubGhzSceneSetType, SubGhzCustomEventManagerSet);
            scene_manager_next_scene(subghz->scene_manager, SubGhzSceneSaveName);
            return true;
        }
    }
    return consumed;
}

void subghz_scene_set_button_on_exit(void* context) {
    SubGhz* subghz = context;

    // Clear view
    byte_input_set_result_callback(subghz->byte_input, NULL, NULL, NULL, NULL, 0);
    byte_input_set_header_text(subghz->byte_input, "");
}

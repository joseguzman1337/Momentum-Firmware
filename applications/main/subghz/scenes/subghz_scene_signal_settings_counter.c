#include "../subghz_i.h"
#include "../helpers/subghz_txrx_create_protocol_key.h"

#include <machine/endian.h>
#include <toolbox/strint.h>
#define TAG "SubGhzSceneSignalSettingsCounter"

uint32_t counter32 = 0x0;
uint16_t counter16 = 0x0;

void subghz_scene_signal_settings_counter_byte_input_callback(void* context) {
    SubGhz* subghz = context;

    view_dispatcher_send_custom_event(subghz->view_dispatcher, SubGhzCustomEventByteInputDone);
}

void subghz_scene_signal_settings_counter_on_enter(void* context) {
    SubGhz* subghz = context;

    FuriString* text = furi_string_alloc();
    FuriString* textCnt = furi_string_alloc();
    uint8_t byte_count = 0;
    uint8_t* byte_ptr = NULL;
    
    subghz_protocol_decoder_base_get_string(subghz_txrx_get_decoder(subghz->txrx), text);
    FURI_LOG_D(TAG, furi_string_get_cstr(text));

    // In protocols output we allways have HEX format for "Cnt:" output (text formating like ...Cnt:%05lX\r\n")
    // Both "Cnt:0x1111" and "Cnt:1111" always mean 0x1111 hex value, so we just use part after "0x"
    // we take 8 simbols starting from "Cnt:0x........" or "Cnt:........"
    // default value for textcnt "0000"
    furi_string_set_str(textCnt, "0000");
    int8_t cnt_place = furi_string_search_str(text, "Cnt:0x", 0);
        
    if(cnt_place > 0) {
        furi_string_set_n(textCnt, text, cnt_place + 6, 8);
    } else {
        cnt_place = furi_string_search_str(text, "Cnt:", 0);
        if(cnt_place > 0) {
            furi_string_set_n(textCnt, text, cnt_place + 4, 8);
        } 
    }
    ///// Добавить проверку  Cnt:????\r\n"



    furi_string_trim(textCnt);
    FURI_LOG_D(TAG,"Counter from file %s", furi_string_get_cstr(textCnt));
    
    //convert 8 simbols string to uint based on base 16 (hex);
    strint_to_uint32(furi_string_get_cstr(textCnt), NULL, &counter32, 16);

    // Check will be counter 2(less than 65535) or 4 (more than 65535) hex bytes long and use corresponding variable for ByteInput
    // To correct display hex value we must revert bytes for ByteInput view and display 2 or 4 hex bytes to edit
    if (counter32 > 0xFFFF) {
        byte_count = 4;
        counter32 = __bswap32(counter32);
        byte_ptr = (uint8_t*)&counter32;

    } else {
        counter16 = counter32;
        byte_count = 2;
        counter16 = __bswap16(counter16);
        byte_ptr = (uint8_t*)&counter16;
    }

    FURI_LOG_D(TAG,"Byte count %i",byte_count);
    FURI_LOG_D(TAG, "Counter Int %li", counter32);
  
    furi_assert(byte_ptr);
    furi_assert(byte_count > 0);

    // Setup view
    ByteInput* byte_input = subghz->byte_input;
    byte_input_set_header_text(byte_input, "Enter COUNTER in HEX");

    byte_input_set_result_callback(
        byte_input,
        subghz_scene_signal_settings_counter_byte_input_callback,
        NULL,
        subghz,
        byte_ptr,
        byte_count);

    furi_string_free(text);
    furi_string_free(textCnt);

    view_dispatcher_switch_to_view(subghz->view_dispatcher, SubGhzViewIdByteInput);

}

bool subghz_scene_signal_settings_counter_on_event(void* context, SceneManagerEvent event) {
    SubGhz* subghz = context;
    bool consumed = false;
    bool generated_protocol = false;

    if(event.type == SceneManagerEventTypeCustom) {
        if(event.event == SubGhzCustomEventByteInputDone) {
            // Swap bytes
            switch(subghz->gen_info->type) {
            case GenFaacSLH:
                subghz->gen_info->faac_slh.cnt = __bswap32(subghz->gen_info->faac_slh.cnt);
                break;
            case GenKeeloq:
                subghz->gen_info->keeloq.cnt = __bswap16(subghz->gen_info->keeloq.cnt);
                break;
            case GenCameAtomo:
                subghz->gen_info->came_atomo.cnt = __bswap16(subghz->gen_info->came_atomo.cnt);
                break;
            case GenKeeloqBFT:
                subghz->gen_info->keeloq_bft.cnt = __bswap16(subghz->gen_info->keeloq_bft.cnt);
                break;
            case GenAlutechAt4n:
                subghz->gen_info->alutech_at_4n.cnt =
                    __bswap16(subghz->gen_info->alutech_at_4n.cnt);
                break;
            case GenSomfyTelis:
                subghz->gen_info->somfy_telis.cnt = __bswap16(subghz->gen_info->somfy_telis.cnt);
                break;
            case GenNiceFlorS:
                subghz->gen_info->nice_flor_s.cnt = __bswap16(subghz->gen_info->nice_flor_s.cnt);
                break;
            case GenSecPlus2:
                subghz->gen_info->sec_plus_2.cnt = __bswap32(subghz->gen_info->sec_plus_2.cnt);
                break;
            case GenPhoenixV2:
                subghz->gen_info->phoenix_v2.cnt = __bswap16(subghz->gen_info->phoenix_v2.cnt);
                break;
                // Not needed for these types
            case GenData:
            case GenSecPlus1:
            default:
                furi_crash("Not implemented");
                break;
            }

            switch(subghz->gen_info->type) {
            case GenFaacSLH:
            case GenKeeloqBFT:
                scene_manager_next_scene(subghz->scene_manager, SubGhzSceneSetSeed);
                return true;
            case GenKeeloq:
                generated_protocol = subghz_txrx_gen_keeloq_protocol(
                    subghz->txrx,
                    subghz->gen_info->mod,
                    subghz->gen_info->freq,
                    subghz->gen_info->keeloq.serial,
                    subghz->gen_info->keeloq.btn,
                    subghz->gen_info->keeloq.cnt,
                    subghz->gen_info->keeloq.manuf);
                break;
            case GenCameAtomo:
                generated_protocol = subghz_txrx_gen_came_atomo_protocol(
                    subghz->txrx,
                    subghz->gen_info->mod,
                    subghz->gen_info->freq,
                    subghz->gen_info->came_atomo.serial,
                    subghz->gen_info->came_atomo.cnt);
                break;
            case GenAlutechAt4n:
                generated_protocol = subghz_txrx_gen_alutech_at_4n_protocol(
                    subghz->txrx,
                    subghz->gen_info->mod,
                    subghz->gen_info->freq,
                    subghz->gen_info->alutech_at_4n.serial,
                    subghz->gen_info->alutech_at_4n.btn,
                    subghz->gen_info->alutech_at_4n.cnt);
                break;
            case GenSomfyTelis:
                generated_protocol = subghz_txrx_gen_somfy_telis_protocol(
                    subghz->txrx,
                    subghz->gen_info->mod,
                    subghz->gen_info->freq,
                    subghz->gen_info->somfy_telis.serial,
                    subghz->gen_info->somfy_telis.btn,
                    subghz->gen_info->somfy_telis.cnt);
                break;
            case GenNiceFlorS:
                generated_protocol = subghz_txrx_gen_nice_flor_s_protocol(
                    subghz->txrx,
                    subghz->gen_info->mod,
                    subghz->gen_info->freq,
                    subghz->gen_info->nice_flor_s.serial,
                    subghz->gen_info->nice_flor_s.btn,
                    subghz->gen_info->nice_flor_s.cnt,
                    subghz->gen_info->nice_flor_s.nice_one);
                break;
            case GenSecPlus2:
                generated_protocol = subghz_txrx_gen_secplus_v2_protocol(
                    subghz->txrx,
                    subghz->gen_info->mod,
                    subghz->gen_info->freq,
                    subghz->gen_info->sec_plus_2.serial,
                    subghz->gen_info->sec_plus_2.btn,
                    subghz->gen_info->sec_plus_2.cnt);
                break;
            case GenPhoenixV2:
                generated_protocol = subghz_txrx_gen_phoenix_v2_protocol(
                    subghz->txrx,
                    subghz->gen_info->mod,
                    subghz->gen_info->freq,
                    subghz->gen_info->phoenix_v2.serial,
                    subghz->gen_info->phoenix_v2.cnt);
                break;
            // Not needed for these types
            case GenData:
            case GenSecPlus1:
            default:
                furi_crash("Not implemented");
                break;
            }

            consumed = true;

            if(!generated_protocol) {
                furi_string_set(
                    subghz->error_str, "Function requires\nan SD card with\nfresh databases.");
                scene_manager_next_scene(subghz->scene_manager, SubGhzSceneShowError);
            } else {
                subghz_file_name_clear(subghz);

                scene_manager_set_scene_state(
                    subghz->scene_manager, SubGhzSceneSetType, SubGhzCustomEventManagerSet);
                scene_manager_next_scene(subghz->scene_manager, SubGhzSceneSaveName);
            }
        }
    }
    return consumed;
}

void subghz_scene_signal_settings_counter_on_exit(void* context) {
    SubGhz* subghz = context;

    // Clear view
    byte_input_set_result_callback(subghz->byte_input, NULL, NULL, NULL, NULL, 0);
    byte_input_set_header_text(subghz->byte_input, "");
}

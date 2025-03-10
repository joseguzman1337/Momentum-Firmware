#include "type_4_tag.h"
#include "type_4_tag_render.h"

#include <nfc/protocols/type_4_tag/type_4_tag_poller.h>
#include <nfc/protocols/type_4_tag/type_4_tag_listener.h>
#include <toolbox/pretty_format.h>

#include "nfc/nfc_app_i.h"

#include "../nfc_protocol_support_common.h"
#include "../nfc_protocol_support_gui_common.h"

enum {
    SubmenuIndexWrite = SubmenuIndexCommonMax,
};

enum {
    NfcSceneMoreInfoStateASCII,
    NfcSceneMoreInfoStateRawData,
};

static void nfc_scene_info_on_enter_type_4_tag(NfcApp* instance) {
    const NfcDevice* device = instance->nfc_device;
    const Type4TagData* data = nfc_device_get_data(device, NfcProtocolType4Tag);

    FuriString* temp_str = furi_string_alloc();
    nfc_append_filename_string_when_present(instance, temp_str);
    furi_string_cat_printf(
        temp_str, "\e#%s\n", nfc_device_get_name(device, NfcDeviceNameTypeFull));
    nfc_render_type_4_tag_info(data, NfcProtocolFormatTypeFull, temp_str);

    widget_add_text_scroll_element(
        instance->widget, 0, 0, 128, 52, furi_string_get_cstr(temp_str));

    furi_string_free(temp_str);
}

static void nfc_scene_more_info_on_enter_type_4_tag(NfcApp* instance) {
    const NfcDevice* device = instance->nfc_device;
    const Type4TagData* data = nfc_device_get_data(device, NfcProtocolType4Tag);

    furi_string_reset(instance->text_box_store);
    uint32_t scene_state =
        scene_manager_get_scene_state(instance->scene_manager, NfcSceneMoreInfo);

    if(scene_state == NfcSceneMoreInfoStateASCII) {
        if(simple_array_get_count(data->ndef_data) == 0) {
            furi_string_cat_str(instance->text_box_store, "No NDEF data to show");
        } else {
            pretty_format_bytes_hex_canonical(
                instance->text_box_store,
                TYPE_4_TAG_RENDER_BYTES_PER_LINE,
                PRETTY_FORMAT_FONT_MONOSPACE,
                simple_array_cget_data(data->ndef_data),
                simple_array_get_count(data->ndef_data));
        }

        widget_add_text_scroll_element(
            instance->widget, 0, 0, 128, 48, furi_string_get_cstr(instance->text_box_store));
        widget_add_button_element(
            instance->widget,
            GuiButtonTypeRight,
            "Raw Data",
            nfc_protocol_support_common_widget_callback,
            instance);

        widget_add_button_element(
            instance->widget,
            GuiButtonTypeLeft,
            "Info",
            nfc_protocol_support_common_widget_callback,
            instance);
    } else if(scene_state == NfcSceneMoreInfoStateRawData) {
        nfc_render_type_4_tag_dump(data, instance->text_box_store);
        widget_add_text_scroll_element(
            instance->widget, 0, 0, 128, 48, furi_string_get_cstr(instance->text_box_store));

        widget_add_button_element(
            instance->widget,
            GuiButtonTypeLeft,
            "ASCII",
            nfc_protocol_support_common_widget_callback,
            instance);
    }
}

static bool nfc_scene_more_info_on_event_type_4_tag(NfcApp* instance, SceneManagerEvent event) {
    bool consumed = false;

    if((event.type == SceneManagerEventTypeCustom && event.event == GuiButtonTypeLeft) ||
       (event.type == SceneManagerEventTypeBack)) {
        scene_manager_set_scene_state(
            instance->scene_manager, NfcSceneMoreInfo, NfcSceneMoreInfoStateASCII);
        scene_manager_previous_scene(instance->scene_manager);
        consumed = true;
    } else if(event.type == SceneManagerEventTypeCustom && event.event == GuiButtonTypeRight) {
        scene_manager_set_scene_state(
            instance->scene_manager, NfcSceneMoreInfo, NfcSceneMoreInfoStateRawData);
        scene_manager_next_scene(instance->scene_manager, NfcSceneMoreInfo);
        consumed = true;
    }
    return consumed;
}

static NfcCommand nfc_scene_read_poller_callback_type_4_tag(NfcGenericEvent event, void* context) {
    furi_assert(event.protocol == NfcProtocolType4Tag);

    NfcCommand command = NfcCommandContinue;

    NfcApp* instance = context;
    const Type4TagPollerEvent* type_4_tag_event = event.event_data;

    if(type_4_tag_event->type == Type4TagPollerEventTypeReadSuccess) {
        nfc_device_set_data(
            instance->nfc_device, NfcProtocolType4Tag, nfc_poller_get_data(instance->poller));
        view_dispatcher_send_custom_event(instance->view_dispatcher, NfcCustomEventPollerSuccess);
        command = NfcCommandStop;
    } else if(type_4_tag_event->type == Type4TagPollerEventTypeReadFailed) {
        command = NfcCommandReset;
    }

    return command;
}

static void nfc_scene_read_on_enter_type_4_tag(NfcApp* instance) {
    nfc_poller_start(instance->poller, nfc_scene_read_poller_callback_type_4_tag, instance);
}

static void nfc_scene_read_and_saved_menu_on_enter_type_4_tag(NfcApp* instance) {
    Submenu* submenu = instance->submenu;

    submenu_add_item(
        submenu,
        "Write (Not Implemented)",
        SubmenuIndexWrite,
        nfc_protocol_support_common_submenu_callback,
        instance);
}

static bool
    nfc_scene_read_and_saved_menu_on_event_type_4_tag(NfcApp* instance, SceneManagerEvent event) {
    bool consumed = false;
    UNUSED(instance);

    if(event.type == SceneManagerEventTypeCustom) {
        if(event.event == SubmenuIndexWrite) {
            // TODO: Implement write
            // scene_manager_next_scene(instance->scene_manager, NfcSceneType4TagWrite);
            consumed = true;
        }
    }
    return consumed;
}

static void nfc_scene_read_success_on_enter_type_4_tag(NfcApp* instance) {
    const NfcDevice* device = instance->nfc_device;
    const Type4TagData* data = nfc_device_get_data(device, NfcProtocolType4Tag);

    FuriString* temp_str = furi_string_alloc();
    furi_string_cat_printf(
        temp_str, "\e#%s\n", nfc_device_get_name(device, NfcDeviceNameTypeFull));
    nfc_render_type_4_tag_info(data, NfcProtocolFormatTypeShort, temp_str);

    widget_add_text_scroll_element(
        instance->widget, 0, 0, 128, 52, furi_string_get_cstr(temp_str));

    furi_string_free(temp_str);
}

static NfcCommand
    nfc_scene_emulate_listener_callback_type_4_tag(NfcGenericEvent event, void* context) {
    furi_assert(context);
    furi_assert(event.protocol == NfcProtocolType4Tag);
    furi_assert(event.event_data);

    NfcApp* nfc = context;
    Type4TagListenerEvent* type_4_tag_event = event.event_data;

    if(type_4_tag_event->type == Type4TagListenerEventTypeCustomCommand) {
        if(furi_string_size(nfc->text_box_store) < NFC_LOG_SIZE_MAX) {
            furi_string_cat_printf(nfc->text_box_store, "R:");
            for(size_t i = 0; i < bit_buffer_get_size_bytes(type_4_tag_event->data->buffer); i++) {
                furi_string_cat_printf(
                    nfc->text_box_store,
                    " %02X",
                    bit_buffer_get_byte(type_4_tag_event->data->buffer, i));
            }
            furi_string_push_back(nfc->text_box_store, '\n');
            view_dispatcher_send_custom_event(nfc->view_dispatcher, NfcCustomEventListenerUpdate);
        }
    }

    return NfcCommandContinue;
}

static void nfc_scene_emulate_on_enter_type_4_tag(NfcApp* instance) {
    const Type4TagData* data = nfc_device_get_data(instance->nfc_device, NfcProtocolType4Tag);

    instance->listener = nfc_listener_alloc(instance->nfc, NfcProtocolType4Tag, data);
    nfc_listener_start(
        instance->listener, nfc_scene_emulate_listener_callback_type_4_tag, instance);
}

const NfcProtocolSupportBase nfc_protocol_support_type_4_tag = {
    .features = NfcProtocolFeatureEmulateFull | NfcProtocolFeatureMoreInfo,

    .scene_info =
        {
            .on_enter = nfc_scene_info_on_enter_type_4_tag,
            .on_event = nfc_protocol_support_common_on_event_empty,
        },
    .scene_more_info =
        {
            .on_enter = nfc_scene_more_info_on_enter_type_4_tag,
            .on_event = nfc_scene_more_info_on_event_type_4_tag,
        },
    .scene_read =
        {
            .on_enter = nfc_scene_read_on_enter_type_4_tag,
            .on_event = nfc_protocol_support_common_on_event_empty,
        },
    .scene_read_menu =
        {
            .on_enter = nfc_scene_read_and_saved_menu_on_enter_type_4_tag,
            .on_event = nfc_scene_read_and_saved_menu_on_event_type_4_tag,
        },
    .scene_read_success =
        {
            .on_enter = nfc_scene_read_success_on_enter_type_4_tag,
            .on_event = nfc_protocol_support_common_on_event_empty,
        },
    .scene_saved_menu =
        {
            .on_enter = nfc_scene_read_and_saved_menu_on_enter_type_4_tag,
            .on_event = nfc_scene_read_and_saved_menu_on_event_type_4_tag,
        },
    .scene_save_name =
        {
            .on_enter = nfc_protocol_support_common_on_enter_empty,
            .on_event = nfc_protocol_support_common_on_event_empty,
        },
    .scene_emulate =
        {
            .on_enter = nfc_scene_emulate_on_enter_type_4_tag,
            .on_event = nfc_protocol_support_common_on_event_empty,
        },
};

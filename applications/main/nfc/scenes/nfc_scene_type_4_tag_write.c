#include "../nfc_app_i.h"

#include <nfc/protocols/type_4_tag/type_4_tag_poller.h>

enum {
    NfcSceneType4TagWriteStateCardSearch,
    NfcSceneType4TagWriteStateCardFound,
};

NfcCommand nfc_scene_type_4_tag_write_worker_callback(NfcGenericEvent event, void* context) {
    furi_assert(context);
    furi_assert(event.event_data);
    furi_assert(event.protocol == NfcProtocolType4Tag);

    NfcCommand command = NfcCommandContinue;
    NfcApp* instance = context;
    Type4TagPollerEvent* t4t_event = event.event_data;

    if(t4t_event->type == Type4TagPollerEventTypeRequestMode) {
        t4t_event->data->poller_mode.mode = Type4TagPollerModeWrite;
        t4t_event->data->poller_mode.data =
            nfc_device_get_data(instance->nfc_device, NfcProtocolType4Tag);
        view_dispatcher_send_custom_event(instance->view_dispatcher, NfcCustomEventCardDetected);
    } else if(t4t_event->type == Type4TagPollerEventTypeWriteFail) {
        scene_manager_set_scene_state(
            instance->scene_manager, NfcSceneType4TagWriteFail, t4t_event->data->error);
        view_dispatcher_send_custom_event(instance->view_dispatcher, NfcCustomEventPollerFailure);
        command = NfcCommandStop;
    } else if(t4t_event->type == Type4TagPollerEventTypeWriteSuccess) {
        view_dispatcher_send_custom_event(instance->view_dispatcher, NfcCustomEventPollerSuccess);
        command = NfcCommandStop;
    }
    return command;
}

static void nfc_scene_type_4_tag_write_setup_view(NfcApp* instance) {
    Popup* popup = instance->popup;
    popup_reset(popup);
    uint32_t state = scene_manager_get_scene_state(instance->scene_manager, NfcSceneType4TagWrite);

    if(state == NfcSceneType4TagWriteStateCardSearch) {
        popup_set_header(instance->popup, "Writing", 95, 20, AlignCenter, AlignCenter);
        popup_set_text(
            instance->popup, "Apply card\nto the back", 95, 38, AlignCenter, AlignCenter);
        popup_set_icon(instance->popup, 0, 8, &I_NFC_manual_60x50);
    } else {
        popup_set_header(popup, "Writing\nDon't move...", 52, 32, AlignLeft, AlignCenter);
        popup_set_icon(popup, 12, 23, &A_Loading_24);
    }

    view_dispatcher_switch_to_view(instance->view_dispatcher, NfcViewPopup);
}

void nfc_scene_type_4_tag_write_on_enter(void* context) {
    NfcApp* instance = context;
    dolphin_deed(DolphinDeedNfcEmulate);

    scene_manager_set_scene_state(
        instance->scene_manager, NfcSceneType4TagWrite, NfcSceneType4TagWriteStateCardSearch);
    nfc_scene_type_4_tag_write_setup_view(instance);

    // Setup and start worker
    instance->poller = nfc_poller_alloc(instance->nfc, NfcProtocolType4Tag);
    nfc_poller_start(instance->poller, nfc_scene_type_4_tag_write_worker_callback, instance);

    nfc_blink_emulate_start(instance);
}

bool nfc_scene_type_4_tag_write_on_event(void* context, SceneManagerEvent event) {
    NfcApp* instance = context;
    bool consumed = false;

    if(event.type == SceneManagerEventTypeCustom) {
        if(event.event == NfcCustomEventCardDetected) {
            scene_manager_set_scene_state(
                instance->scene_manager,
                NfcSceneType4TagWrite,
                NfcSceneType4TagWriteStateCardFound);
            nfc_scene_type_4_tag_write_setup_view(instance);
            consumed = true;
        } else if(event.event == NfcCustomEventPollerSuccess) {
            scene_manager_next_scene(instance->scene_manager, NfcSceneType4TagWriteSuccess);
            consumed = true;
        } else if(event.event == NfcCustomEventPollerFailure) {
            scene_manager_next_scene(instance->scene_manager, NfcSceneType4TagWriteFail);
            consumed = true;
        }
    }

    return consumed;
}

void nfc_scene_type_4_tag_write_on_exit(void* context) {
    NfcApp* instance = context;

    nfc_poller_stop(instance->poller);
    nfc_poller_free(instance->poller);

    scene_manager_set_scene_state(
        instance->scene_manager, NfcSceneType4TagWrite, NfcSceneType4TagWriteStateCardSearch);
    // Clear view
    popup_reset(instance->popup);

    nfc_blink_stop(instance);
}

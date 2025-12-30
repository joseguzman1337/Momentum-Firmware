#include "../js_modules.h"

#include <furi.h>
#include <ctype.h>
#include <ibutton/ibutton_key.h>
#include <ibutton/ibutton_worker.h>
#include <ibutton/ibutton_protocols.h>

#define TAG "js_ibutton"

#define JS_IBUTTON_EVENT_DONE (1U << 0)

typedef enum {
    JsIbuttonStateIdle,
    JsIbuttonStateEmulating,
} JsIbuttonState;

typedef struct {
    iButtonProtocols* protocols;
    iButtonWorker* worker;
    iButtonKey* key;
    FuriEventFlag* event;
    JsIbuttonState state;
    iButtonWorkerWriteResult write_result;
} JsIbuttonCtx;

static void js_ibutton_read_callback(void* context) {
    furi_assert(context);
    FuriEventFlag* event = context;
    furi_event_flag_set(event, JS_IBUTTON_EVENT_DONE);
}

static void js_ibutton_write_callback(void* context, iButtonWorkerWriteResult result) {
    furi_assert(context);
    JsIbuttonCtx* ibutton = context;
    ibutton->write_result = result;
    furi_event_flag_set(ibutton->event, JS_IBUTTON_EVENT_DONE);
}

static bool js_ibutton_copy_bytes(
    struct mjs* mjs,
    mjs_val_t value,
    uint8_t** out,
    size_t* out_len,
    bool* out_allocated,
    const char** out_error) {
    *out = NULL;
    *out_len = 0;
    *out_allocated = false;
    *out_error = NULL;

    if(mjs_is_array(value)) {
        size_t len = mjs_array_length(mjs, value);
        if(len == 0) {
            *out_error = "Data array must not be empty";
            return false;
        }
        uint8_t* buf = malloc(len);
        for(size_t i = 0; i < len; i++) {
            mjs_val_t val = mjs_array_get(mjs, value, i);
            if(!mjs_is_number(val)) {
                free(buf);
                *out_error = "Data array must contain only numbers";
                return false;
            }
            uint32_t byte_val = mjs_get_int32(mjs, val);
            if(byte_val > 0xFF) {
                free(buf);
                *out_error = "Data array values must be 0-255";
                return false;
            }
            buf[i] = (uint8_t)byte_val;
        }
        *out = buf;
        *out_len = len;
        *out_allocated = true;
        return true;
    }

    if(mjs_is_typed_array(value)) {
        mjs_val_t array_buf = value;
        if(mjs_is_data_view(value)) {
            array_buf = mjs_dataview_get_buf(mjs, value);
        }
        size_t len = 0;
        uint8_t* buf = (uint8_t*)mjs_array_buf_get_ptr(mjs, array_buf, &len);
        if(len == 0) {
            *out_error = "Data array must not be empty";
            return false;
        }
        *out = buf;
        *out_len = len;
        *out_allocated = false;
        return true;
    }

    *out_error = "Data must be an array, arraybuf or dataview";
    return false;
}

static bool js_ibutton_prepare_key(
    struct mjs* mjs,
    JsIbuttonCtx* ibutton,
    mjs_val_t protocol_arg,
    mjs_val_t data_arg,
    iButtonProtocolId* out_id) {
    if(!mjs_is_string(protocol_arg)) {
        JS_ERROR_AND_RETURN_VAL(mjs, MJS_BAD_ARGS_ERROR, false, "Protocol must be a string");
    }

    size_t protocol_len = 0;
    const char* protocol_name = mjs_get_string(mjs, &protocol_arg, &protocol_len);
    if((protocol_len == 0) || (protocol_name == NULL)) {
        JS_ERROR_AND_RETURN_VAL(mjs, MJS_BAD_ARGS_ERROR, false, "Protocol must be a string");
    }

    char* protocol_copy = malloc(protocol_len + 1);
    memcpy(protocol_copy, protocol_name, protocol_len);
    protocol_copy[protocol_len] = '\0';
    protocol_copy[0] = (char)toupper((unsigned char)protocol_copy[0]);

    iButtonProtocolId protocol_id =
        ibutton_protocols_get_id_by_name(ibutton->protocols, protocol_copy);
    free(protocol_copy);

    if(protocol_id == iButtonProtocolIdInvalid) {
        JS_ERROR_AND_RETURN_VAL(mjs, MJS_BAD_ARGS_ERROR, false, "Unknown iButton protocol");
    }

    ibutton_key_reset(ibutton->key);
    ibutton_key_set_protocol_id(ibutton->key, protocol_id);

    iButtonEditableData editable = {};
    ibutton_protocols_get_editable_data(ibutton->protocols, ibutton->key, &editable);

    uint8_t* data = NULL;
    size_t data_len = 0;
    bool allocated = false;
    const char* error = NULL;
    if(!js_ibutton_copy_bytes(mjs, data_arg, &data, &data_len, &allocated, &error)) {
        JS_ERROR_AND_RETURN_VAL(mjs, MJS_BAD_ARGS_ERROR, false, "%s", error);
    }

    if(data_len != editable.size) {
        if(allocated) free(data);
        JS_ERROR_AND_RETURN_VAL(
            mjs,
            MJS_BAD_ARGS_ERROR,
            false,
            "Data must be %zu bytes long",
            editable.size);
    }

    memcpy(editable.ptr, data, editable.size);
    if(allocated) free(data);

    if(out_id) *out_id = protocol_id;
    return true;
}

static void js_ibutton_read(struct mjs* mjs) {
    JsIbuttonCtx* ibutton = JS_GET_CONTEXT(mjs);
    furi_assert(ibutton);

    if(ibutton->state != JsIbuttonStateIdle) {
        JS_ERROR_AND_RETURN(mjs, MJS_INTERNAL_ERROR, "iButton is busy");
    }

    uint32_t timeout_ms = FuriWaitForever;
    if(mjs_nargs(mjs) > 0) {
        mjs_val_t timeout_arg = mjs_arg(mjs, 0);
        if(!mjs_is_number(timeout_arg)) {
            JS_ERROR_AND_RETURN(mjs, MJS_BAD_ARGS_ERROR, "Timeout must be a number");
        }
        int32_t timeout_val = mjs_get_int32(mjs, timeout_arg);
        if(timeout_val > 0) timeout_ms = (uint32_t)timeout_val;
    }

    furi_event_flag_clear(ibutton->event, JS_IBUTTON_EVENT_DONE);
    ibutton_worker_start_thread(ibutton->worker);
    ibutton_worker_read_set_callback(ibutton->worker, js_ibutton_read_callback, ibutton->event);
    ibutton_worker_read_start(ibutton->worker, ibutton->key);

    uint32_t flags =
        furi_event_flag_wait(ibutton->event, JS_IBUTTON_EVENT_DONE, FuriFlagWaitAny, timeout_ms);

    ibutton_worker_stop(ibutton->worker);
    ibutton_worker_stop_thread(ibutton->worker);

    if(!(flags & JS_IBUTTON_EVENT_DONE)) {
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    const char* protocol_name =
        ibutton_protocols_get_name(ibutton->protocols, ibutton_key_get_protocol_id(ibutton->key));

    iButtonEditableData editable = {};
    ibutton_protocols_get_editable_data(ibutton->protocols, ibutton->key, &editable);

    uint8_t* data_copy = malloc(editable.size);
    memcpy(data_copy, editable.ptr, editable.size);

    FuriString* uid = furi_string_alloc();
    ibutton_protocols_render_uid(ibutton->protocols, ibutton->key, uid);

    mjs_val_t result = mjs_mk_object(mjs);
    JS_ASSIGN_MULTI(mjs, result) {
        JS_FIELD("protocol", mjs_mk_string(mjs, protocol_name, ~0, true));
        JS_FIELD("data", mjs_mk_array_buf(mjs, (char*)data_copy, editable.size));
        JS_FIELD("uid", mjs_mk_string(mjs, furi_string_get_cstr(uid), ~0, true));
    }

    furi_string_free(uid);
    free(data_copy);

    mjs_return(mjs, result);
}

static bool js_ibutton_write_internal(struct mjs* mjs, bool write_copy) {
    JsIbuttonCtx* ibutton = JS_GET_CONTEXT(mjs);
    furi_assert(ibutton);

    if(ibutton->state != JsIbuttonStateIdle) {
        JS_ERROR_AND_RETURN_VAL(mjs, MJS_INTERNAL_ERROR, false, "iButton is busy");
    }

    if(mjs_nargs(mjs) < 2 || mjs_nargs(mjs) > 3) {
        JS_ERROR_AND_RETURN_VAL(mjs, MJS_BAD_ARGS_ERROR, false, "Wrong argument count");
    }

    iButtonProtocolId protocol_id = iButtonProtocolIdInvalid;
    if(!js_ibutton_prepare_key(
           mjs, ibutton, mjs_arg(mjs, 0), mjs_arg(mjs, 1), &protocol_id)) {
        return false;
    }

    uint32_t features = ibutton_protocols_get_features(ibutton->protocols, protocol_id);
    if(write_copy && !(features & iButtonProtocolFeatureWriteCopy)) {
        JS_ERROR_AND_RETURN_VAL(mjs, MJS_BAD_ARGS_ERROR, false, "Protocol cannot write copy");
    }
    if(!write_copy && !(features & iButtonProtocolFeatureWriteId)) {
        JS_ERROR_AND_RETURN_VAL(mjs, MJS_BAD_ARGS_ERROR, false, "Protocol cannot write id");
    }

    uint32_t timeout_ms = FuriWaitForever;
    if(mjs_nargs(mjs) == 3) {
        mjs_val_t timeout_arg = mjs_arg(mjs, 2);
        if(!mjs_is_number(timeout_arg)) {
            JS_ERROR_AND_RETURN_VAL(mjs, MJS_BAD_ARGS_ERROR, false, "Timeout must be a number");
        }
        int32_t timeout_val = mjs_get_int32(mjs, timeout_arg);
        if(timeout_val > 0) timeout_ms = (uint32_t)timeout_val;
    }

    furi_event_flag_clear(ibutton->event, JS_IBUTTON_EVENT_DONE);
    ibutton_worker_start_thread(ibutton->worker);
    ibutton_worker_write_set_callback(ibutton->worker, js_ibutton_write_callback, ibutton);
    if(write_copy) {
        ibutton_worker_write_copy_start(ibutton->worker, ibutton->key);
    } else {
        ibutton_worker_write_id_start(ibutton->worker, ibutton->key);
    }

    uint32_t flags =
        furi_event_flag_wait(ibutton->event, JS_IBUTTON_EVENT_DONE, FuriFlagWaitAny, timeout_ms);

    ibutton_worker_stop(ibutton->worker);
    ibutton_worker_stop_thread(ibutton->worker);

    if(!(flags & JS_IBUTTON_EVENT_DONE)) {
        return false;
    }

    return (ibutton->write_result == iButtonWorkerWriteOK) ||
           (ibutton->write_result == iButtonWorkerWriteSameKey);
}

static void js_ibutton_write_id(struct mjs* mjs) {
    bool result = js_ibutton_write_internal(mjs, false);
    mjs_return(mjs, mjs_mk_boolean(mjs, result));
}

static void js_ibutton_write_copy(struct mjs* mjs) {
    bool result = js_ibutton_write_internal(mjs, true);
    mjs_return(mjs, mjs_mk_boolean(mjs, result));
}

static void js_ibutton_emulate_start(struct mjs* mjs) {
    JsIbuttonCtx* ibutton = JS_GET_CONTEXT(mjs);
    furi_assert(ibutton);

    if(ibutton->state != JsIbuttonStateIdle) {
        JS_ERROR_AND_RETURN(mjs, MJS_INTERNAL_ERROR, "iButton is busy");
    }

    if(mjs_nargs(mjs) != 2) {
        JS_ERROR_AND_RETURN(mjs, MJS_BAD_ARGS_ERROR, "Wrong argument count");
    }

    if(!js_ibutton_prepare_key(
           mjs, ibutton, mjs_arg(mjs, 0), mjs_arg(mjs, 1), NULL)) {
        return;
    }

    ibutton_worker_start_thread(ibutton->worker);
    ibutton_worker_emulate_start(ibutton->worker, ibutton->key);
    ibutton->state = JsIbuttonStateEmulating;

    mjs_return(mjs, MJS_UNDEFINED);
}

static void js_ibutton_emulate_stop(struct mjs* mjs) {
    JsIbuttonCtx* ibutton = JS_GET_CONTEXT(mjs);
    furi_assert(ibutton);

    if(ibutton->state == JsIbuttonStateEmulating) {
        ibutton_worker_stop(ibutton->worker);
        ibutton_worker_stop_thread(ibutton->worker);
        ibutton->state = JsIbuttonStateIdle;
    }

    mjs_return(mjs, MJS_UNDEFINED);
}

static void* js_ibutton_create(struct mjs* mjs, mjs_val_t* object, JsModules* modules) {
    UNUSED(modules);

    JsIbuttonCtx* ibutton = malloc(sizeof(JsIbuttonCtx));
    ibutton->protocols = ibutton_protocols_alloc();
    ibutton->worker = ibutton_worker_alloc(ibutton->protocols);
    ibutton->key = ibutton_key_alloc(ibutton_protocols_get_max_data_size(ibutton->protocols));
    ibutton->event = furi_event_flag_alloc();
    ibutton->state = JsIbuttonStateIdle;
    ibutton->write_result = iButtonWorkerWriteNoDetect;

    mjs_val_t ibutton_obj = mjs_mk_object(mjs);
    mjs_set(mjs, ibutton_obj, INST_PROP_NAME, ~0, mjs_mk_foreign(mjs, ibutton));

    JS_ASSIGN_MULTI(mjs, ibutton_obj) {
        JS_FIELD("read", MJS_MK_FN(js_ibutton_read));
        JS_FIELD("writeId", MJS_MK_FN(js_ibutton_write_id));
        JS_FIELD("writeCopy", MJS_MK_FN(js_ibutton_write_copy));
        JS_FIELD("emulateStart", MJS_MK_FN(js_ibutton_emulate_start));
        JS_FIELD("emulateStop", MJS_MK_FN(js_ibutton_emulate_stop));
    }

    *object = ibutton_obj;
    return ibutton;
}

static void js_ibutton_destroy(void* inst) {
    JsIbuttonCtx* ibutton = inst;
    if(ibutton->state == JsIbuttonStateEmulating) {
        ibutton_worker_stop(ibutton->worker);
        ibutton_worker_stop_thread(ibutton->worker);
    }
    ibutton_key_free(ibutton->key);
    ibutton_worker_free(ibutton->worker);
    ibutton_protocols_free(ibutton->protocols);
    furi_event_flag_free(ibutton->event);
    free(ibutton);
}

static const JsModuleDescriptor js_ibutton_desc = {
    "ibutton",
    js_ibutton_create,
    js_ibutton_destroy,
    NULL,
};

static const FlipperAppPluginDescriptor plugin_descriptor = {
    .appid = PLUGIN_APP_ID,
    .ep_api_version = PLUGIN_API_VERSION,
    .entry_point = &js_ibutton_desc,
};

const FlipperAppPluginDescriptor* js_ibutton_ep(void) {
    return &plugin_descriptor;
}

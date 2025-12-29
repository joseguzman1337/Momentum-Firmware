#include <core/common_defines.h>
#include "../js_modules.h"
#include <furi_hal_rtc.h>

static void js_rtc_get_datetime(struct mjs* mjs) {
    DateTime datetime = {0};
    furi_hal_rtc_get_datetime(&datetime);

    mjs_val_t datetime_obj = mjs_mk_object(mjs);
    mjs_set(mjs, datetime_obj, "year", ~0, mjs_mk_number(mjs, datetime.year));
    mjs_set(mjs, datetime_obj, "month", ~0, mjs_mk_number(mjs, datetime.month));
    mjs_set(mjs, datetime_obj, "day", ~0, mjs_mk_number(mjs, datetime.day));
    mjs_set(mjs, datetime_obj, "hour", ~0, mjs_mk_number(mjs, datetime.hour));
    mjs_set(mjs, datetime_obj, "minute", ~0, mjs_mk_number(mjs, datetime.minute));
    mjs_set(mjs, datetime_obj, "second", ~0, mjs_mk_number(mjs, datetime.second));
    mjs_set(mjs, datetime_obj, "weekday", ~0, mjs_mk_number(mjs, datetime.weekday));
    mjs_return(mjs, datetime_obj);
}

static void js_rtc_get_timestamp(struct mjs* mjs) {
    uint32_t timestamp = furi_hal_rtc_get_timestamp();
    mjs_return(mjs, mjs_mk_number(mjs, timestamp));
}

static void* js_rtc_create(struct mjs* mjs, mjs_val_t* object, JsModules* modules) {
    UNUSED(modules);

    mjs_val_t rtc_obj = mjs_mk_object(mjs);
    mjs_set(mjs, rtc_obj, "getDateTime", ~0, MJS_MK_FN(js_rtc_get_datetime));
    mjs_set(mjs, rtc_obj, "getTimestamp", ~0, MJS_MK_FN(js_rtc_get_timestamp));
    *object = rtc_obj;

    return (void*)1;
}

static const JsModuleDescriptor js_rtc_desc = {
    "rtc",
    js_rtc_create,
    NULL,
    NULL,
};

static const FlipperAppPluginDescriptor plugin_descriptor = {
    .appid = PLUGIN_APP_ID,
    .ep_api_version = PLUGIN_API_VERSION,
    .entry_point = &js_rtc_desc,
};

const FlipperAppPluginDescriptor* js_rtc_ep(void) {
    return &plugin_descriptor;
}

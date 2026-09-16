#include <flipper_application/api_hashtable/api_hashtable.h>
#include <flipper_application/api_hashtable/compilesort.hpp>

#include "js_event_loop_api_table_i.h"

static_assert(!has_hash_collisions(js_event_loop_api_table), "Detected API method hash collision!");
static constexpr auto js_event_loop_packed_api_table = pack_hashtable(js_event_loop_api_table);

extern "C" constexpr HashtableApiInterface js_event_loop_hashtable_api_interface{
    {
        .api_version_major = 0,
        .api_version_minor = 0,
        .resolver_callback = &elf_resolve_from_hashtable,
    },
    js_event_loop_packed_api_table.hash_low.data(),
    js_event_loop_packed_api_table.hash_high.data(),
    js_event_loop_packed_api_table.addresses.data(),
    js_event_loop_api_table.size(),
    js_event_loop_packed_api_table.low_width,
};

#include <flipper_application/api_hashtable/api_hashtable.h>
#include <flipper_application/api_hashtable/compilesort.hpp>

#include "unit_test_api_table_i.h"

static_assert(!has_hash_collisions(unit_tests_api_table), "Detected API method hash collision!");
static constexpr auto unit_tests_packed_api_table = pack_hashtable(unit_tests_api_table);

constexpr HashtableApiInterface unit_tests_hashtable_api_interface{
    {
        .api_version_major = 0,
        .api_version_minor = 0,
        .resolver_callback = &elf_resolve_from_hashtable,
    },
    unit_tests_packed_api_table.hash_low.data(),
    unit_tests_packed_api_table.hash_high.data(),
    unit_tests_packed_api_table.addresses.data(),
    unit_tests_api_table.size(),
    unit_tests_packed_api_table.low_width,
};

extern "C" const ElfApiInterface* const unit_tests_api_interface =
    &unit_tests_hashtable_api_interface;

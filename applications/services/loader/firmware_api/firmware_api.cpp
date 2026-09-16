#include "firmware_api.h"

#include <flipper_application/api_hashtable/api_hashtable.h>
#include <flipper_application/api_hashtable/compilesort.hpp>

/* Generated table */
#include <firmware_api_table.h>

#include <furi_hal_info.h>

constexpr HashtableApiInterface elf_api_interface{
    {
        .api_version_major = (elf_api_version >> 16),
        .api_version_minor = (elf_api_version & 0xFFFF),
        .resolver_callback = &elf_resolve_from_hashtable,
    },
    elf_api_hash_low,
    elf_api_hash_high,
    elf_api_addresses,
    elf_api_count,
    elf_api_low_width,
};
const ElfApiInterface* const firmware_api_interface = &elf_api_interface;

extern "C" void furi_hal_info_get_api_version(uint16_t* major, uint16_t* minor) {
    *major = firmware_api_interface->api_version_major;
    *minor = firmware_api_interface->api_version_minor;
}

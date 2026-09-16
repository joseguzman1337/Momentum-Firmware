#include "api_hashtable.h"

#include <furi.h>
#include <algorithm>

#define TAG "ApiHashtable"

bool elf_resolve_from_hashtable(
    const ElfApiInterface* interface,
    uint32_t hash,
    Elf32_Addr* address) {

    furi_check(interface);
    furi_check(address);

    const HashtableApiInterface* hashtable_interface =
        static_cast<const HashtableApiInterface*>(interface);

    uint32_t high_position = 0;
    for(uint16_t index = 0; index < hashtable_interface->count; ++index) {
        while(!(hashtable_interface->hash_high[high_position >> 3] &
                (1U << (high_position & 7)))) {
            ++high_position;
        }
        const uint32_t low_bit = (uint32_t)index * hashtable_interface->low_width;
        const uint8_t* packed = hashtable_interface->hash_low + (low_bit >> 3);
        uint32_t low = packed[0] | ((uint32_t)packed[1] << 8) | ((uint32_t)packed[2] << 16);
        const uint8_t shift = low_bit & 7;
        if(shift) low |= (uint32_t)packed[3] << 24;
        const uint32_t low_mask = hashtable_interface->low_width == 32 ?
                                      UINT32_MAX :
                                      ((UINT32_C(1) << hashtable_interface->low_width) - 1);
        low = (low >> shift) & low_mask;
        const uint32_t decoded = hashtable_interface->low_width == 32 ?
                                     low :
                                     ((high_position - index) << hashtable_interface->low_width) |
                                         low;
        if(decoded >= hash) {
            if(decoded == hash) {
                *address = hashtable_interface->addresses[index];
                return true;
            }
            break;
        }
        ++high_position;
    }
    FURI_LOG_T(TAG, "Can't find symbol with hash %lx!", hash);
    return false;
}

uint32_t elf_symbolname_hash(const char* s) {
    furi_check(s);
    return elf_gnu_hash(s);
}

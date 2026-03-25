#pragma once

#include <stdint.h>

namespace rtl8814au {

struct DeviceId {
    uint16_t vendor;
    uint16_t product;
};

static constexpr DeviceId kRealtekVendor {
    0x0BDA, 0x0000 // product filled per device
};

} // namespace rtl8814au

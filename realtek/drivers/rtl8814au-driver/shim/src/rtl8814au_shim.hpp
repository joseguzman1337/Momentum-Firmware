#pragma once

#include <string>
#include <vector>

struct RTL8814AUDeviceInfo {
    std::string vendorName;
    std::string productName;
    uint16_t vendorId;
    uint16_t productId;
};

std::vector<RTL8814AUDeviceInfo> find_rtl8814au_devices();
int bring_up_link(const RTL8814AUDeviceInfo &dev);

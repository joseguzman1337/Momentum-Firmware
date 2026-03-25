#include "rtl8814au_shim.hpp"
#include <IOKit/usb/IOUSBLib.h>
#include <CoreFoundation/CoreFoundation.h>
#include <iostream>

std::vector<RTL8814AUDeviceInfo> find_rtl8814au_devices()
{
    std::vector<RTL8814AUDeviceInfo> result;

    std::cout << "[shim] Device enumeration not implemented yet.\n";
    return result;
}

int bring_up_link(const RTL8814AUDeviceInfo &dev)
{
    std::cout << "[shim] bring_up_link() not implemented for device: "
              << dev.vendorName << " " << dev.productName << "\n";
    return -1;
}

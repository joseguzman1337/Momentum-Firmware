#include "rtl8814au_shim.hpp"
#include <iostream>

int main()
{
    auto devices = find_rtl8814au_devices();
    if (devices.empty()) {
        std::cout << "No RTL8814AU devices found.\n";
        return 1;
    }

    std::cout << "Found " << devices.size() << " RTL8814AU candidate(s):\n";
    for (const auto &dev : devices) {
        std::cout << "  Vendor=" << dev.vendorName
                  << " Product=" << dev.productName
                  << " VID=0x" << std::hex << dev.vendorId
                  << " PID=0x" << std::hex << dev.productId << std::dec
                  << "\n";
    }

    return bring_up_link(devices.front());
}

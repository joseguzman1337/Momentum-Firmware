#pragma once

#include <DriverKit/OSObject.h>
#include <DriverKit/IOService.h>

class RTL8814AU_USBDevice : public OSObject
{
    OSDeclareDefaultStructors(RTL8814AU_USBDevice)

public:
    bool initWithProvider(IOService *provider);

    kern_return_t start();
    void stop();
};

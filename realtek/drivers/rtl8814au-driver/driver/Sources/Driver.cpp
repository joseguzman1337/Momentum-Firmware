#include "Driver.hpp"
#include "USBDevice.hpp"

#define super IOService
OSDefineMetaClassAndStructors(RTL8814AU_Driver, IOService)

bool RTL8814AU_Driver::init()
{
    if (!super::init()) {
        return false;
    }
    return true;
}

void RTL8814AU_Driver::free()
{
    super::free();
}

kern_return_t RTL8814AU_Driver::Start(IOService *provider)
{
    kern_return_t ret = super::Start(provider);
    if (ret != kIOReturnSuccess) {
        return ret;
    }

    // TODO: create RTL8814AU_USBDevice, initialize hardware

    return kIOReturnSuccess;
}

kern_return_t RTL8814AU_Driver::Stop(IOService *provider)
{
    // TODO: stop hardware, cleanup
    return super::Stop(provider);
}

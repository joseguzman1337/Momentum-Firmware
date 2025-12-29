#include "USBDevice.hpp"

OSDefineMetaClassAndStructors(RTL8814AU_USBDevice, OSObject)

bool RTL8814AU_USBDevice::initWithProvider(IOService *provider)
{
    if (!OSObject::init()) {
        return false;
    }
    // TODO: query USB descriptors, allocate endpoints
    (void)provider;
    return true;
}

kern_return_t RTL8814AU_USBDevice::start()
{
    // TODO: initialize chip, load firmware
    return kIOReturnSuccess;
}

void RTL8814AU_USBDevice::stop()
{
    // TODO: stop traffic, power down
}

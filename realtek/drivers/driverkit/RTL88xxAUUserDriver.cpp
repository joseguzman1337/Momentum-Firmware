#include "RTL88xxAUUserDriver.hpp"

OSDefineMetaClassAndStructors(RTL88xxAUUserDriver, IOUserNetworkController);

kern_return_t
RTL88xxAUUserDriver::Start(IOService *provider)
{
    kern_return_t ret = super::Start(provider);
    if (ret != kIOReturnSuccess) {
        os_log(OS_LOG_DEFAULT, "[RTL88xxAUUserDriver] Start failed: 0x%x", ret);
        return ret;
    }

    os_log(OS_LOG_DEFAULT, "[RTL88xxAUUserDriver] DriverKit network controller started");

    // TODO: Implement USB/PCIe binding and bring up a logical network interface.

    return kIOReturnSuccess;
}

kern_return_t
RTL88xxAUUserDriver::Stop(IOService *provider)
{
    os_log(OS_LOG_DEFAULT, "[RTL88xxAUUserDriver] Stopping DriverKit network controller");

    // TODO: Tear down any active queues, timers, and hardware bindings.

    return super::Stop(provider);
}

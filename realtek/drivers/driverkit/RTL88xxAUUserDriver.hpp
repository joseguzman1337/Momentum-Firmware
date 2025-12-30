#ifndef RTL88XXAU_USER_DRIVER_HPP
#define RTL88XXAU_USER_DRIVER_HPP

#include <DriverKit/IOUserNetworkController.h>
#include <DriverKit/OSLog.h>

// Minimal DriverKit network controller skeleton for RTL88xxAU/RTL8814AU.
// This does NOT implement real hardware I/O; it is a starting point for a
// production DriverKit-based replacement for the legacy kext.

class RTL88xxAUUserDriver : public IOUserNetworkController
{
    OSDeclareDefaultStructors(RTL88xxAUUserDriver);

public:
    virtual kern_return_t
    Start(IOService *provider) APPLE_KEXT_OVERRIDE;

    virtual kern_return_t
    Stop(IOService *provider) APPLE_KEXT_OVERRIDE;
};

#endif // RTL88XXAU_USER_DRIVER_HPP

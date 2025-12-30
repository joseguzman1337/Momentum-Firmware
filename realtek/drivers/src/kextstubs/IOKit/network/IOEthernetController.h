#ifndef STUB_IOKIT_NETWORK_IOETHERNETCONTROLLER_H
#define STUB_IOKIT_NETWORK_IOETHERNETCONTROLLER_H

#include "../IOService.h"
#include "../IOWorkLoop.h"

class IONetworkInterface;

class IOEthernetController : public IOService {
public:
    virtual bool createWorkLoop() { return true; }
    virtual IOWorkLoop *getWorkLoop() const { return nullptr; }
    virtual IOReturn enable(IONetworkInterface *) { return kIOReturnSuccess; }
    virtual IOReturn disable(IONetworkInterface *) { return kIOReturnSuccess; }
    virtual IOReturn outputStart(IONetworkInterface *, IOOptionBits) { return kIOReturnSuccess; }
};

#endif // STUB_IOKIT_NETWORK_IOETHERNETCONTROLLER_H

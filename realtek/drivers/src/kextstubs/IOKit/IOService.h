#ifndef STUB_IOKIT_IOSERVICE_H
#define STUB_IOKIT_IOSERVICE_H

#include "libkern/c++/OSObject.h"
#include <stdint.h>

typedef uint8_t  UInt8;
typedef uint16_t UInt16;
typedef uint32_t UInt32;
typedef uint32_t IOOptionBits;

class IOService : public OSObject {
public:
    virtual bool init(OSDictionary *properties = nullptr) { (void)properties; return true; }
    virtual void free() {}
    virtual bool start(IOService *provider) { (void)provider; return true; }
    virtual void stop(IOService *provider) { (void)provider; }
    virtual IOReturn message(UInt32, IOService *, void *) { return kIOReturnSuccess; }
};

#endif // STUB_IOKIT_IOSERVICE_H

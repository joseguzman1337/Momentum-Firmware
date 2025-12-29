#ifndef STUB_IOKIT_USB_IOUSBINTERFACE_H
#define STUB_IOKIT_USB_IOUSBINTERFACE_H

#include "../IOService.h"
#include "IOUSBDevice.h"

class IOUSBInterface : public IOService {
public:
    IOUSBDevice *GetDevice() { return nullptr; }
    IOReturn SetConfiguration(IOService *, UInt8) { return kIOReturnSuccess; }
};

#endif // STUB_IOKIT_USB_IOUSBINTERFACE_H

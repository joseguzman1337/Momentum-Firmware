#ifndef STUB_IOKIT_USB_IOUSBDEVICE_H
#define STUB_IOKIT_USB_IOUSBDEVICE_H

#include "../IOService.h"

class IOUSBDevice : public IOService {
public:
    UInt16 GetVendorID() const { return 0; }
    UInt16 GetProductID() const { return 0; }
};

#endif // STUB_IOKIT_USB_IOUSBDEVICE_H

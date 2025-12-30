#pragma once

#include <DriverKit/IOService.h>

class RTL8814AU_Driver : public IOService
{
    OSDeclareDefaultStructors(RTL8814AU_Driver)

public:
    virtual bool init() override;
    virtual void free() override;

    virtual kern_return_t Start(IOService *provider) override;
    virtual kern_return_t Stop(IOService *provider) override;
};

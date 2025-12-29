#ifndef STUB_IOUSERNETWORKCONTROLLER_H
#define STUB_IOUSERNETWORKCONTROLLER_H

// Local stub for environments without full DriverKit networking headers.
// Provides just enough declarations for RTL88xxAUUserDriver.cpp to compile.

typedef int kern_return_t;
static const kern_return_t kIOReturnSuccess = 0;

class IOService {};

class IOUserNetworkController : public IOService {
public:
    virtual kern_return_t Start(IOService *provider) { (void)provider; return kIOReturnSuccess; }
    virtual kern_return_t Stop(IOService *provider)  { (void)provider; return kIOReturnSuccess; }
};

#define APPLE_KEXT_OVERRIDE override

#define OSDeclareDefaultStructors(className) \
public: \
    className() = default; \
    virtual ~className() = default;

#define OSDefineMetaClassAndStructors(className, superClass)

// Provide a simple alias so code can use 'super::Start/Stop' like in real DriverKit classes.
#ifndef super
#define super IOUserNetworkController
#endif

#endif // STUB_IOUSERNETWORKCONTROLLER_H

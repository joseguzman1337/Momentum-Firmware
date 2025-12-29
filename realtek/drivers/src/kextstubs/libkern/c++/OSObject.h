#ifndef STUB_LIBKERN_OSOBJECT_H
#define STUB_LIBKERN_OSOBJECT_H

#include <stdint.h>
#include <cstddef>

#ifndef NULL
#define NULL nullptr
#endif

// Minimal stand-in for IOReturn and basic libkern status codes

typedef int32_t IOReturn;
static const IOReturn kIOReturnSuccess   = 0;
static const IOReturn kIOReturnNotReady  = 0x2c1; // arbitrary non-zero placeholder

class OSObject {
public:
    virtual void retain() {}
    virtual void release() {}

protected:
    virtual ~OSObject() = default;
};

// Mirror typical libkern macros with simple implementations
#define OSDeclareDefaultStructors(className) \
public: \
    className() = default; \
    virtual ~className() = default;

// Provide a typedef so code can use 'super::method()' where
// OSDefineMetaClassAndStructors(className, superClass) is invoked.
#define OSDefineMetaClassAndStructors(className, superClass) \
    typedef superClass super;

#define OSDynamicCast(type, obj) (static_cast<type *>(obj))

#endif // STUB_LIBKERN_OSOBJECT_H

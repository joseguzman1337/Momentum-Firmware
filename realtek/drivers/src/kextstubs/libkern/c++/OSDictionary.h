#ifndef STUB_LIBKERN_OSDICTIONARY_H
#define STUB_LIBKERN_OSDICTIONARY_H

#include "OSObject.h"

// Extremely small stub just to satisfy references from RTL88xxAU.

class OSDictionary : public OSObject {
public:
    static OSDictionary *withCapacity(unsigned int) { return new OSDictionary; }
};

#endif // STUB_LIBKERN_OSDICTIONARY_H

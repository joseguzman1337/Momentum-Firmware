#ifndef STUB_IOKIT_IOWORKLOOP_H
#define STUB_IOKIT_IOWORKLOOP_H

#include "IOService.h"

class IOWorkLoop : public OSObject {
public:
    static IOWorkLoop *workLoop() { return new IOWorkLoop; }
};

#endif // STUB_IOKIT_IOWORKLOOP_H

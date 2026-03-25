#include <libkern/libkern.h>
#include <mach/mach_types.h>

extern "C" {
kern_return_t realtek_start(kmod_info_t* ki, void* d);
kern_return_t realtek_stop(kmod_info_t* ki, void* d);
}

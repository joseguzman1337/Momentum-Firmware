#include "realtek.hpp"

kern_return_t realtek_start(kmod_info_t* ki, void* d) {
    printf("realtek: Loaded successfully\n");
    return KERN_SUCCESS;
}

kern_return_t realtek_stop(kmod_info_t* ki, void* d) {
    printf("realtek: Unloaded successfully\n");
    return KERN_SUCCESS;
}

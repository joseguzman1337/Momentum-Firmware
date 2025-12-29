#include "realtek2.hpp"

kern_return_t realtek2_start(kmod_info_t* ki, void* d) {
    printf("realtek2: Loaded successfully\n");
    return KERN_SUCCESS;
}

kern_return_t realtek2_stop(kmod_info_t* ki, void* d) {
    printf("realtek2: Unloaded successfully\n");
    return KERN_SUCCESS;
}

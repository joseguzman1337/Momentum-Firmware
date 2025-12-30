#ifndef __CC_H__
#define __CC_H__

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>

#ifndef BYTE_ORDER
// #define BYTE_ORDER ERROR // Standard lwip checks for little endian by default/cmake?
#endif
// Cortex-M4 is Little Endian
#ifdef BYTE_ORDER
#undef BYTE_ORDER
#endif
#define BYTE_ORDER LITTLE_ENDIAN

typedef uint8_t u8_t;
typedef int8_t s8_t;
typedef uint16_t u16_t;
typedef int16_t s16_t;
typedef uint32_t u32_t;
typedef int32_t s32_t;

typedef uintptr_t mem_ptr_t;

#define LWIP_ERR_T int

// Printf formatters
#define U16_F "u"
#define S16_F "d"
#define X16_F "x"
#define U32_F "ru"
#define S32_F "rd"
#define X32_F "rx"
#define SZT_F "uz"

// Compiler hints for packing structures
#define PACK_STRUCT_FIELD(x) x
#define PACK_STRUCT_STRUCT   __attribute__((packed))
#define PACK_STRUCT_BEGIN
#define PACK_STRUCT_END

// Platform specific diagnostic output
#define LWIP_PLATFORM_DIAG(x) \
    do {                      \
        printf x;             \
    } while(0)
#define LWIP_PLATFORM_ASSERT(x)                                                      \
    do {                                                                             \
        printf("Assertion \"%s\" failed at line %d in %s\n", x, __LINE__, __FILE__); \
        abort();                                                                     \
    } while(0)

// Random number generator
// Use __has_include to avoid redeclaration if header is available
#if defined(__has_include) && __has_include(<furi_hal_random.h>)
#include <furi_hal_random.h>
#else
extern uint32_t furi_hal_random_get(void);
#endif
#define LWIP_RAND() furi_hal_random_get()

#endif /* __CC_H__ */

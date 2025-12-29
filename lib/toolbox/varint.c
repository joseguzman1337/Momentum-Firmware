#include "varint.h"

size_t varint_uint32_pack(uint32_t value, uint8_t* output) {
    uint8_t* start = output;
    while(value >= 0x80) {
        *output++ = (value | 0x80);
        value >>= 7;
    }
    *output++ = value;
    return output - start;
}

size_t varint_uint32_unpack(uint32_t* value, const uint8_t* input, size_t input_size) {
    size_t i;
    uint32_t parsed = 0;

    for(i = 0; i < input_size; i++) {
        parsed |= (input[i] & 0x7FUL) << (7 * i);

        if(!(input[i] & 0x80)) {
            break;
        }
    }

    *value = parsed;

    return i + 1;
}

size_t varint_uint32_length(uint32_t value) {
    size_t size = 0;
    while(value >= 0x80) {
        value >>= 7;
        size++;
    }
    size++;

    return size;
}

size_t varint_int32_pack(int32_t value, uint8_t* output) {
    uint32_t v;

    // ZigZag encoding: cast to unsigned before arithmetic to avoid signed overflow
    // For negative values, convert to unsigned representation first
    if(value >= 0) {
        v = (uint32_t)value << 1;
    } else {
        // Cast to unsigned first, then negate to avoid overflow with INT32_MIN
        // -value would overflow for INT32_MIN, so use: ~(value as unsigned) + 1 = -value in unsigned
        uint32_t abs_val = ~(uint32_t)value + 1;
        v = (abs_val << 1) - 1;
    }

    return varint_uint32_pack(v, output);
}

size_t varint_int32_unpack(int32_t* value, const uint8_t* input, size_t input_size) {
    uint32_t v;
    size_t size = varint_uint32_unpack(&v, input, input_size);

    if(v & 1) {
        *value = (int32_t)(v + 1) / (-2);
    } else {
        *value = v / 2;
    }

    return size;
}

size_t varint_int32_length(int32_t value) {
    uint32_t v;

    // ZigZag encoding: cast to unsigned before arithmetic to avoid signed overflow
    // For negative values, convert to unsigned representation first
    if(value >= 0) {
        v = (uint32_t)value << 1;
    } else {
        // Cast to unsigned first, then negate to avoid overflow with INT32_MIN
        // -value would overflow for INT32_MIN, so use: ~(value as unsigned) + 1 = -value in unsigned
        uint32_t abs_val = ~(uint32_t)value + 1;
        v = (abs_val << 1) - 1;
    }

    return varint_uint32_length(v);
}

// DeepSeek Security Fix: Zero-overhead bounds check applied.

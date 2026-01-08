/** Bit Buffer
 *
 * Various bits and bytes manipulation tools.
 *
 * @file bit_buffer.h
 */
#pragma once

#ifndef _BIT_BUFFER_H
#define _BIT_BUFFER_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct BitBuffer BitBuffer;

/** Allocate a BitBuffer instance.
 *
 * @param[in]  capacity_bytes  maximum buffer capacity, in bytes
 *
 * @return     pointer to the allocated BitBuffer instance
 */
BitBuffer* bit_buffer_alloc(size_t capacity_bytes);

/** Delete a BitBuffer instance.
 *
 * @param[in,out] buf   pointer to a BitBuffer instance
 */
void bit_buffer_free(BitBuffer* buf);

/** Clear all data from a BitBuffer instance.
 *
 * @param[in,out] buf   pointer to a BitBuffer instance
 */
void bit_buffer_reset(BitBuffer* buf);

// Copy and write

/** Copy another BitBuffer instance's contents to this one, replacing all of the
 * original data.
 *
 * @warning       The destination capacity must be no less than the source data
 *                size.
 *
 * @param[in,out] buf    pointer to a BitBuffer instance to copy into
 * @param[in]     other  pointer to a BitBuffer instance to copy from
 */
void bit_buffer_copy(BitBuffer* buf, const BitBuffer* other);

/** Copy all BitBuffer instance's contents to this one, starting from
 * start_index, replacing all of the original data.
 *
 * @warning       The destination capacity must be no less than the source data
 *                size counting from start_index.
 *
 * @param[in,out] buf          pointer to a BitBuffer instance to copy into
 * @param[in]     other        pointer to a BitBuffer instance to copy from
 * @param[in]     start_index  index to begin copying source data from
 */
void bit_buffer_copy_right(BitBuffer* buf, const BitBuffer* other, size_t start_index);

/** Copy all BitBuffer instance's contents to this one, ending with end_index,
 * replacing all of the original data.
 *
 * @warning       The destination capacity must be no less than the source data
 *                size counting to end_index.
 *
 * @param[in,out] buf        pointer to a BitBuffer instance to copy into
 * @param[in]     other      pointer to a BitBuffer instance to copy from
 * @param[in]     end_index  index to end copying source data at
 */
void bit_buffer_copy_left(BitBuffer* buf, const BitBuffer* other, size_t end_index);

/** Copy a byte array to a BitBuffer instance, replacing all of the original
 * data.
 *
 * @warning       The destination capacity must be no less than the source data
 *                size.
 *
 * @param[in,out] buf         pointer to a BitBuffer instance to copy into
 * @param[in]     data        pointer to the byte array to be copied
 * @param[in]     size_bytes  size of the data to be copied, in bytes
 */
void bit_buffer_copy_bytes(BitBuffer* buf, const uint8_t* data, size_t size_bytes);

/** Copy a byte array to a BitBuffer instance, replacing all of the original
 * data.
 *
 * @warning       The destination capacity must be no less than the source data
 *                size.
 *
 * @param[in,out] buf        pointer to a BitBuffer instance to copy into
 * @param[in]     data       pointer to the byte array to be copied
 * @param[in]     size_bits  size of the data to be copied, in bits
 */
void bit_buffer_copy_bits(BitBuffer* buf, const uint8_t* data, size_t size_bits);

/** Copy a byte with parity array to a BitBuffer instance, replacing all of the
 * original data.
 *
 * @warning       The destination capacity must be no less than the source data
 *                size.
 *
 * @param[in,out] buf        pointer to a BitBuffer instance to copy into
 * @param[in]     data       pointer to the byte array to be copied
 * @param[in]     size_bits  size of the data to be copied, in bits
 * @note          Parity bits are placed starting with the most significant bit
 *                of each byte and moving up.
 * @note          Example: DDDDDDDD PDDDDDDD DPDDDDDD DDP...
 */
void bit_buffer_copy_bytes_with_parity(BitBuffer* buf, const uint8_t* data, size_t size_bits);

/** Copy data from BitBuffer to a byte array.
 *
 * @param[in]  buf         pointer to a BitBuffer instance
 * @param[out] dest        pointer to the destination byte array
 * @param[in]  size_bytes  size of the data to be copied, in bytes
 */
void bit_buffer_write_bytes(const BitBuffer* buf, void* dest, size_t size_bytes);

/** Copy data from BitBuffer to a byte array, extracting parity bits into a separate buffer.
 *
 * @param[in]  buf         pointer to a BitBuffer instance
 * @param[out] dest        pointer to the destination byte array
 * @param[in]  size_bits   size of the data to be copied, in bits
 * @param[out] parity_buf  pointer to the destination parity buffer
 */
void bit_buffer_write_bytes_with_parity(
    const BitBuffer* buf,
    void* dest,
    size_t size_bits,
    size_t* parity_buf);

/** Copy data from BitBuffer to a byte array, starting from middle.
 *
 * @param[in]  buf         pointer to a BitBuffer instance
 * @param[out] dest        pointer to the destination byte array
 * @param[in]  size_bits   size of the data to be copied, in bits
 * @param[in]  start_index bit index to start copying from
 */
void bit_buffer_write_bytes_mid(
    const BitBuffer* buf,
    void* dest,
    size_t size_bits,
    size_t start_index);

/** Check if the BitBuffer instance contains at least one partial byte.
 *
 * @param[in]  buf   pointer to a BitBuffer instance
 *
 * @return     true if at least one partial byte is present, false otherwise
 */
bool bit_buffer_has_partial_byte(const BitBuffer* buf);

/** Check if the BitBuffer instance starts with a specific byte.
 *
 * @param[in]  buf   pointer to a BitBuffer instance
 * @param[in]  byte  byte to check for
 *
 * @return     true if the BitBuffer instance starts with the specific byte, false otherwise
 */
bool bit_buffer_starts_with_byte(const BitBuffer* buf, uint8_t byte);

// Getter and setters

/** Get the capacity of a BitBuffer instance, in bytes.
 *
 * @param[in]  buf   pointer to a BitBuffer instance
 *
 * @return     the capacity, in bytes
 */
size_t bit_buffer_get_capacity_bytes(const BitBuffer* buf);

/** Get the size of a BitBuffer instance, in bits.
 *
 * @param[in]  buf   pointer to a BitBuffer instance
 *
 * @return     the size, in bits
 */
size_t bit_buffer_get_size(const BitBuffer* buf);

/** Get the size of a BitBuffer instance, in bytes (rounded up).
 *
 * @param[in]  buf   pointer to a BitBuffer instance
 *
 * @return     the size, in bytes
 */
size_t bit_buffer_get_size_bytes(const BitBuffer* buf);

/** Get a byte from a BitBuffer instance at a specific bit index.
 *
 * @param[in]  buf    pointer to a BitBuffer instance
 * @param[in]  index  bit index to get the byte from
 *
 * @return     the byte value
 */
uint8_t bit_buffer_get_byte(const BitBuffer* buf, size_t index);

/** Get a byte from a BitBuffer instance at a specific bit index.
 *
 * @param[in]  buf         pointer to a BitBuffer instance
 * @param[in]  index_bits  bit index to get the byte from
 *
 * @return     the byte value
 */
uint8_t bit_buffer_get_byte_from_bit(const BitBuffer* buf, size_t index_bits);

/** Get a pointer to the internal data buffer of a BitBuffer instance.
 *
 * @param[in]  buf   pointer to a BitBuffer instance
 *
 * @return     pointer to the internal data buffer
 */
const uint8_t* bit_buffer_get_data(const BitBuffer* buf);

/** Get a pointer to the internal parity buffer of a BitBuffer instance.
 *
 * @param[in]  buf   pointer to a BitBuffer instance
 *
 * @return     pointer to the internal parity buffer
 */
const uint8_t* bit_buffer_get_parity(const BitBuffer* buf);

/** Set a byte in a BitBuffer instance at a specific bit index.
 *
 * @param[in,out] buf    pointer to a BitBuffer instance
 * @param[in]     index  bit index to set the byte at
 * @param[in]     byte   byte value to set
 */
void bit_buffer_set_byte(BitBuffer* buf, size_t index, uint8_t byte);

/** Set a byte with a parity bit in a BitBuffer instance at a specific bit index.
 *
 * @param[in,out] buff    pointer to a BitBuffer instance
 * @param[in]     index   bit index to set the byte at
 * @param[in]     byte    byte value to set
 * @param[in]     parity  parity bit value to set
 */
void bit_buffer_set_byte_with_parity(BitBuffer* buff, size_t index, uint8_t byte, bool parity);

/** Set the size of a BitBuffer instance, in bits.
 *
 * @param[in,out] buf       pointer to a BitBuffer instance
 * @param[in]     new_size  new size, in bits
 */
void bit_buffer_set_size(BitBuffer* buf, size_t new_size);

/** Set the size of a BitBuffer instance, in bytes.
 *
 * @param[in,out] buf             pointer to a BitBuffer instance
 * @param[in]     new_size_bytes  new size, in bytes
 */
void bit_buffer_set_size_bytes(BitBuffer* buf, size_t new_size_bytes);

// Append

/** Append another BitBuffer instance's contents to this one.
 *
 * @warning       The destination capacity must be no less than the sum of the
 *                original and appended data sizes.
 *
 * @param[in,out] buf    pointer to a BitBuffer instance to append into
 * @param[in]     other  pointer to a BitBuffer instance to append from
 */
void bit_buffer_append(BitBuffer* buf, const BitBuffer* other);

/** Append a BitBuffer instance's contents to this one, starting from start_index.
 *
 * @warning       The destination capacity must be no less than the sum of the
 *                original and appended data sizes.
 *
 * @param[in,out] buf          pointer to a BitBuffer instance to append into
 * @param[in]     other        pointer to a BitBuffer instance to append from
 * @param[in]     start_index  bit index to begin appending source data from
 */
void bit_buffer_append_right(BitBuffer* buf, const BitBuffer* other, size_t start_index);

/** Append a byte to a BitBuffer instance.
 *
 * @warning       The destination capacity must be no less than the sum of the
 *                original data size and 8 bits.
 *
 * @param[in,out] buf   pointer to a BitBuffer instance to append into
 * @param[in]     byte  byte value to append
 */
void bit_buffer_append_byte(BitBuffer* buf, uint8_t byte);

/** Append multiple bytes to a BitBuffer instance.
 *
 * @warning       The destination capacity must be no less than the sum of the
 *                original and appended data sizes.
 *
 * @param[in,out] buf         pointer to a BitBuffer instance to append into
 * @param[in]     data        pointer to the byte array to be appended
 * @param[in]     size_bytes  size of the data to be appended, in bytes
 */
void bit_buffer_append_bytes(BitBuffer* buf, const uint8_t* data, size_t size_bytes);

/** Append a single bit to a BitBuffer instance.
 *
 * @warning       The destination capacity must be no less than the sum of the
 *                original data size and 1 bit.
 *
 * @param[in,out] buf  pointer to a BitBuffer instance to append into
 * @param[in]     bit  bit value to append
 */
void bit_buffer_append_bit(BitBuffer* buf, bool bit);

#ifdef __cplusplus
}
#endif

#endif // _BIT_BUFFER_H
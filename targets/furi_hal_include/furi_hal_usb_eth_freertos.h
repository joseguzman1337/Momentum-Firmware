#pragma once

/*
 * USB Ethernet's private lwIP library uses these FreeRTOS kernel entry points
 * directly. Keeping this narrow bridge in the SDK lets the FAP relocate them
 * without linking lwIP or the Ethernet implementation into the base firmware.
 */
#include <stdint.h>

typedef int32_t BaseType_t;
typedef uint32_t UBaseType_t;
typedef uint32_t TickType_t;
typedef struct QueueDefinition* QueueHandle_t;
typedef struct tskTaskControlBlock* TaskHandle_t;
typedef void (*TaskFunction_t)(void*);

#ifdef __cplusplus
extern "C" {
#endif

void vPortEnterCritical(void);
void vPortExitCritical(void);
void vQueueDelete(QueueHandle_t queue);
void vTaskDelete(TaskHandle_t task);
void vTaskSuspend(TaskHandle_t task);
QueueHandle_t xQueueCreateMutex(const uint8_t queue_type);
BaseType_t xQueueTakeMutexRecursive(QueueHandle_t mutex, TickType_t ticks_to_wait);
QueueHandle_t xQueueGenericCreate(
    const UBaseType_t queue_length,
    const UBaseType_t item_size,
    const uint8_t queue_type);
BaseType_t xTaskCreate(
    TaskFunction_t task,
    const char* const name,
    const uint16_t stack_depth,
    void* const context,
    UBaseType_t priority,
    TaskHandle_t* const created_task);
BaseType_t xQueueGiveMutexRecursive(QueueHandle_t mutex);
TickType_t xTaskGetTickCount(void);
BaseType_t
    xQueueReceive(QueueHandle_t queue, void* const buffer, TickType_t ticks_to_wait);
BaseType_t xQueueSemaphoreTake(QueueHandle_t queue, TickType_t ticks_to_wait);
BaseType_t xQueueGenericSend(
    QueueHandle_t queue,
    const void* const item,
    TickType_t ticks_to_wait,
    const BaseType_t copy_position);

#ifdef __cplusplus
}
#endif

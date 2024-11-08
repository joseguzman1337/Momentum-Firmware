#include "nfc_logger.h"

#include <furi.h>
#include <furi_hal_resources.h>
#include <furi_hal_rtc.h>
#include <storage/storage.h>

#define TAG "NfcLogger"

#define NFC_LOG_FOLDER                   "nfc"
#define NFC_LOG_TEMP_FILE_NAME           "log_temp.bin"
#define NFC_LOG_FILE_PATH                EXT_PATH(NFC_LOG_FOLDER "/")
#define NFC_LOG_FILE_PATH_BASE(filename) (NFC_LOG_FILE_PATH filename)
#define NFC_LOG_TEMP_FILE_PATH           NFC_LOG_FILE_PATH_BASE(NFC_LOG_TEMP_FILE_NAME)
//EXT_PATH(NFC_LOG_FOLDER "/" NFC_LOG_TEMP_FILE_NAME)

typedef enum {
    NfcTransactionTypeEmpty,
    NfcTransactionTypeRequest,
    NfcTransactionTypeResponse,
    NfcTransactionTypeRequestResponse,
} NfcTransactionType;

typedef struct {
    uint32_t time;
    uint32_t flags;
    size_t data_size;
    uint8_t* data;
} NfcPacket;

typedef struct {
    uint32_t id;
    NfcTransactionType type;
    //uint32_t time; ///TODO: optional
    NfcPacket* request;
    NfcPacket* response;
} FURI_PACKED NfcTransaction;

typedef struct {
    NfcProtocol protocol;
    NfcMode mode;
    size_t transactions_count;
} FURI_PACKED NfcTrace;

typedef enum {
    NfcLoggerStateIdle,
    NfcLoggerStateProcessing,
    NfcLoggerStateStopped,
    NfcLoggerStateError
} NfcLoggerState;

struct NfcLogger {
    NfcTrace* trace;
    NfcTransaction* transaction;
    NfcLoggerState state;

    FuriString* filename;
    Storage* storage;
    FuriThread* logger_thread;
    FuriMessageQueue* transaction_queue;
    bool exit;
};

static void nfc_logger_transaction_free(NfcTransaction* instance);

static void nfc_logger_save_packet(File* file, NfcPacket* packet) {
    if(packet) {
        storage_file_write(file, &packet->time, sizeof(uint32_t) * 2 + sizeof(size_t));
        //storage_file_write(file, &packet->time, sizeof(uint32_t));
        //storage_file_write(file, &packet->data_size, sizeof(size_t));
        storage_file_write(file, packet->data, packet->data_size);
    }
}

static int32_t nfc_logger_thread_callback(void* context) {
    FURI_LOG_D(TAG, "Thread start");
    NfcLogger* instance = context;

    const GpioPin* pin = furi_hal_resources_pin_by_number(2)->pin;
    furi_hal_gpio_init_simple(pin, GpioModeOutputPushPull);
    bool toggle = false;

    File* f = storage_file_alloc(instance->storage);
    if(!storage_file_open(f, NFC_LOG_TEMP_FILE_PATH, FSAM_READ_WRITE, FSOM_CREATE_ALWAYS)) {
        instance->state = NfcLoggerStateError;
        nfc_logger_stop(instance);
    }

    NfcTrace* trace = instance->trace;
    storage_file_write(f, trace, sizeof(NfcTrace));

    while(!instance->exit) {
        NfcTransaction* ptr = NULL;
        if(furi_message_queue_get(instance->transaction_queue, &ptr, 50) == FuriStatusErrorTimeout)
            continue;

        FURI_LOG_D(TAG, "Save_tr: %ld", ptr->id);
        storage_file_write(f, &(ptr->id), sizeof(uint32_t) + sizeof(NfcTransactionType));
        nfc_logger_save_packet(f, ptr->request);
        nfc_logger_save_packet(f, ptr->response);
        //storage_file_write(f, &(ptr->time), sizeof(uint32_t));

        nfc_logger_transaction_free(ptr);
        furi_hal_gpio_write(pin, toggle);
        toggle = !toggle;
    }

    storage_file_seek(f, 0, true);
    storage_file_write(f, trace, sizeof(NfcTrace));

    storage_file_close(f);
    storage_file_free(f);
    FURI_LOG_D(TAG, "Thread finish");
    return 0;
}

NfcLogger* nfc_logger_alloc(void) {
    NfcLogger* instance = malloc(sizeof(NfcLogger));

    instance->storage = furi_record_open(RECORD_STORAGE);
    instance->filename = furi_string_alloc();
    return instance;
}

static inline void nfc_logger_free_thread_and_queue(NfcLogger* instance) {
    if(instance->logger_thread) furi_thread_free(instance->logger_thread);
    if(instance->transaction_queue) furi_message_queue_free(instance->transaction_queue);
}

void nfc_logger_free(NfcLogger* instance) {
    furi_assert(instance);

    furi_record_close(RECORD_STORAGE);
    furi_string_free(instance->filename);
    nfc_logger_free_thread_and_queue(instance);

    free(instance);
}

void nfc_logger_config(NfcLogger* instance, bool enabled) {
    if(enabled) {
        FuriThread* thread =
            furi_thread_alloc_ex(TAG, 1024U, nfc_logger_thread_callback, instance);
        furi_thread_set_priority(thread, FuriThreadPriorityLow);
        instance->logger_thread = thread;

        instance->transaction_queue = furi_message_queue_alloc(4, sizeof(NfcTransaction*));
        instance->state = NfcLoggerStateIdle;
    } else {
        nfc_logger_free_thread_and_queue(instance);
        instance->state = NfcLoggerStateDisabled;
    }
}

static NfcTrace* nfc_logger_trace_alloc(NfcProtocol protocol, NfcMode mode) {
    NfcTrace* trace = malloc(sizeof(NfcTrace));
    trace->mode = mode;
    trace->protocol = protocol;
    return trace;
}

static void nfc_logger_trace_free(NfcTrace* trace) {
    furi_assert(trace);
    free(trace);
}

void nfc_logger_start(NfcLogger* instance, NfcProtocol protocol, NfcMode mode) {
    furi_assert(instance);
    furi_assert(protocol < NfcProtocolNum);
    furi_assert(mode < NfcModeNum);

    instance->exit = false;
    instance->trace = nfc_logger_trace_alloc(protocol, mode);

    DateTime dt;
    furi_hal_rtc_get_datetime(&dt);
    furi_string_printf(
        instance->filename,
        "LOG-%.4d%.2d%.2d-%.2d%.2d%.2d",
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second);

    instance->state = NfcLoggerStateIdle;

    furi_thread_start(instance->logger_thread);
}

void nfc_logger_stop(NfcLogger* instance) {
    furi_assert(instance);

    if(instance->state != NfcLoggerStateError) {
        nfc_logger_transaction_end(instance);
    }

    instance->exit = true;
    furi_thread_join(instance->logger_thread);

    if(instance->state != NfcLoggerStateError) {
        FuriString* str = furi_string_alloc_set_str(NFC_LOG_FILE_PATH);
        furi_string_cat(str, instance->filename);
        furi_string_cat_str(str, ".bin");
        storage_common_copy(instance->storage, NFC_LOG_TEMP_FILE_PATH, furi_string_get_cstr(str));
        furi_string_free(str);

        ///TODO: Re-save temp.bin log file to file_name and save in flipper_format
        nfc_logger_trace_free(instance->trace);
        furi_string_reset(instance->filename);
        instance->state = NfcLoggerStateStopped;
    }
}
//----------------------------------------------------------------------------------------------------------
//NfcTransaction handlers
static NfcTransaction* nfc_logger_transaction_alloc(uint32_t id) {
    NfcTransaction* t = malloc(sizeof(NfcTransaction));
    t->type = NfcTransactionTypeEmpty;
    t->id = id;
    return t;
}

static void nfc_logger_transaction_free(NfcTransaction* instance) {
    furi_assert(instance);

    FURI_LOG_D(TAG, "Free_tr: %ld", instance->id);

    if(instance->request) {
        if(instance->request->data) free(instance->request->data);
        free(instance->request);
    }

    if(instance->response) {
        if(instance->response->data) free(instance->response->data);
        free(instance->response);
    }

    free(instance);
}

void nfc_logger_transaction_begin(NfcLogger* instance) {
    furi_assert(instance);
    furi_assert(instance->transaction == NULL);

    if(instance->transaction) {
        nfc_logger_transaction_end(instance);
    }

    uint32_t id = instance->trace->transactions_count;
    FURI_LOG_D(TAG, "Begin_tr: %ld", id);

    instance->state = NfcLoggerStateProcessing;
    instance->transaction = nfc_logger_transaction_alloc(id);
    instance->trace->transactions_count++;
}

void nfc_logger_transaction_end(NfcLogger* instance) {
    furi_assert(instance);
    do {
        if(instance->state != NfcLoggerStateProcessing) break;
        if(!instance->transaction) break;

        FURI_LOG_D(TAG, "End_tr: %ld", instance->transaction->id);

        if(furi_message_queue_put(instance->transaction_queue, &instance->transaction, 10) !=
           FuriStatusOk) {
            instance->state = NfcLoggerStateError;
            FURI_LOG_E(TAG, "Transaction lost, logger will be stopped!");
            nfc_logger_stop(instance);
        }
        instance->transaction = NULL;
    } while(false);
}

static NfcPacket* nfc_logger_get_packet(NfcTransaction* transaction, bool response) {
    furi_assert(transaction);

    NfcPacket* p;
    if(response) {
        if(!transaction->response) transaction->response = malloc(sizeof(NfcPacket));
        transaction->type = transaction->type == NfcTransactionTypeRequest ?
                                NfcTransactionTypeRequestResponse :
                                NfcTransactionTypeResponse;
        p = transaction->response;
    } else {
        if(!transaction->request) transaction->request = malloc(sizeof(NfcPacket));
        transaction->type = NfcTransactionTypeRequest;
        p = transaction->request;
    }
    return p;
}

void nfc_logger_transaction_append(
    NfcLogger* instance,
    const uint8_t* data,
    const size_t data_size,
    bool response) {
    furi_assert(instance);
    furi_assert(data);
    furi_assert(data_size > 0);

    NfcPacket* p = nfc_logger_get_packet(instance->transaction, response);
    FURI_LOG_D(
        TAG,
        "Append_tr: %ld size: %d type: %02X",
        instance->transaction->id,
        data_size,
        instance->transaction->type);

    p->time = furi_get_tick();
    p->data_size = data_size;
    p->data = malloc(data_size);
    memcpy(p->data, data, data_size);
}

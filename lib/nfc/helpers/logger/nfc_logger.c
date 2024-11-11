#include "nfc_logger_i.h"

#define TAG "NfcLogger"

#define NFC_LOG_FOLDER                   "nfc"
#define NFC_LOG_TEMP_FILE_NAME           "log_temp.bin"
#define NFC_LOG_FILE_PATH                EXT_PATH(NFC_LOG_FOLDER "/")
#define NFC_LOG_FILE_PATH_BASE(filename) (NFC_LOG_FILE_PATH filename)
#define NFC_LOG_TEMP_FILE_PATH           NFC_LOG_FILE_PATH_BASE(NFC_LOG_TEMP_FILE_NAME)
//EXT_PATH(NFC_LOG_FOLDER "/" NFC_LOG_TEMP_FILE_NAME)

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

        nfc_transaction_save_to_file(f, ptr);

        nfc_transaction_free(ptr);
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

bool nfc_logger_enabled(NfcLogger* instance) {
    furi_assert(instance);
    return instance->state != NfcLoggerStateDisabled;
}

void nfc_logger_set_history_size(NfcLogger* instance, uint8_t size) {
    furi_assert(instance);
    furi_assert(size > 0);
    instance->history_size_max = size;
}

void nfc_logger_start(NfcLogger* instance, NfcProtocol protocol, NfcMode mode) {
    furi_assert(instance);
    furi_assert(protocol < NfcProtocolNum);
    furi_assert(mode < NfcModeNum);

    if(instance->state == NfcLoggerStateDisabled) return;

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

    furi_thread_start(instance->logger_thread);
}

void nfc_logger_stop(NfcLogger* instance) {
    furi_assert(instance);

    if(instance->state == NfcLoggerStateDisabled) return;

    if(instance->state != NfcLoggerStateError) {
        nfc_logger_transaction_end(instance);
    }

    instance->exit = true;
    furi_thread_join(instance->logger_thread);
    //    nfc_logger_free_thread_and_queue(instance);

    if(instance->state != NfcLoggerStateError) {
        FuriString* str = furi_string_alloc_set_str(NFC_LOG_FILE_PATH);
        furi_string_cat(str, instance->filename);
        furi_string_cat_str(str, ".bin");
        storage_common_copy(instance->storage, NFC_LOG_TEMP_FILE_PATH, furi_string_get_cstr(str));
        ///TODO: Maybe rename with storage_common_rename(instance->storage) would be better?
        furi_string_free(str);

        ///TODO: Re-save temp.bin log file to file_name and save in flipper_format
        nfc_logger_trace_free(instance->trace);
        furi_string_reset(instance->filename);
        instance->state = NfcLoggerStateStopped;
    }
}

//------------------------------------------------------------------------------------------------------------------------
//NfcTransaction some handlers

void nfc_logger_transaction_begin(NfcLogger* instance) {
    furi_assert(instance);
    furi_assert(instance->transaction == NULL);

    if(instance->state == NfcLoggerStateDisabled) return;

    if(instance->transaction) {
        nfc_logger_transaction_end(instance);
    }

    uint32_t id = instance->trace->transactions_count;
    FURI_LOG_D(TAG, "Begin_tr: %ld", id);

    instance->state = NfcLoggerStateProcessing;
    instance->transaction = nfc_transaction_alloc(id, instance->history_size_max);
}

void nfc_logger_transaction_end(NfcLogger* instance) {
    furi_assert(instance);
    do {
        if(instance->state == NfcLoggerStateDisabled) break;
        if(instance->state != NfcLoggerStateProcessing) break;
        if(!instance->transaction) break;
        if(nfc_transaction_get_type(instance->transaction) == NfcTransactionTypeEmpty) {
            nfc_transaction_free(instance->transaction);
            break;
        }

        //FURI_LOG_D(TAG, "End_tr: %ld", instance->transaction->id);

        if(furi_message_queue_put(instance->transaction_queue, &instance->transaction, 10) !=
           FuriStatusOk) {
            instance->state = NfcLoggerStateError;
            FURI_LOG_E(TAG, "Transaction lost, logger will be stopped!");
            nfc_logger_stop(instance);
        }
        instance->trace->transactions_count++;
        instance->transaction = NULL;
    } while(false);
}

void nfc_logger_append_data(
    NfcLogger* instance,
    const uint8_t* data,
    const size_t data_size,
    bool response) {
    if(instance->state == NfcLoggerStateDisabled) return;

    nfc_transaction_append(instance->transaction, data, data_size, response);
}

void nfc_logger_append_history(NfcLogger* instance, NfcLoggerHistory* history) {
    furi_assert(instance);
    furi_assert(history);

    if(instance->state == NfcLoggerStateDisabled) return;

    uint8_t history_cnt = nfc_transaction_get_history_count(instance->transaction);
    ///TODO:replace assert with check
    furi_assert(history_cnt < instance->history_size_max);

    nfc_transaction_append_history(instance->transaction, history);
}

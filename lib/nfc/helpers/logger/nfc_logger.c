#include "nfc_logger_context.h"
#include "history/nfc_history_size.h"
#include "formatter/nfc_formatter.h"
#include <nfc_device.h>
#include <furi_hal_cortex.h>

#define TAG "NfcLogger"

#define NFC_LOG_FOLDER                   "nfc/log"
#define NFC_LOG_TEMP_FILE_NAME           "log_temp.bin"
#define NFC_LOG_FOLDER_PATH              EXT_PATH(NFC_LOG_FOLDER)
#define NFC_LOG_FILE_PATH                NFC_LOG_FOLDER_PATH "/"
#define NFC_LOG_FILE_PATH_BASE(filename) (NFC_LOG_FILE_PATH filename)
#define NFC_LOG_TEMP_FILE_PATH           NFC_LOG_FILE_PATH_BASE(NFC_LOG_TEMP_FILE_NAME)
//EXT_PATH(NFC_LOG_FOLDER "/" NFC_LOG_TEMP_FILE_NAME)

#define NFC_LOG_MESSAGE_QUEUE_TIMEOUT_MS (50)
#define NFC_LOG_MESSAGE_QUEUE_TIMEOUT_US (NFC_LOG_MESSAGE_QUEUE_TIMEOUT_MS * 1000U)

#define NFC_LOG_DWT_CYCCNT_CYCLES_PER_MESSAGE_QUEUE_TIMEOUT(inst_per_us) \
    (NFC_LOG_MESSAGE_QUEUE_TIMEOUT_US * inst_per_us)
#define NFC_LOG_DWT_CYCCNT_SECONDS_MAX(inst_per_us) (UINT32_MAX / inst_per_us)

static uint32_t nfc_logger_get_time(NfcLogger* instance) {
    uint32_t time = 0;
    uint32_t inst_per_us = furi_hal_cortex_instructions_per_microsecond();

    if(furi_mutex_acquire(instance->dwt_mutex, 10) == FuriStatusOk) {
        uint32_t dwt_prev = instance->dwt_cnt_prev;

        uint32_t dwt = DWT->CYCCNT;
        time = (dwt < dwt_prev) ? ((UINT32_MAX - dwt_prev) + dwt) / inst_per_us :
                                  (dwt - dwt_prev) / inst_per_us;

        time += instance->dwt_second_per_ovf * instance->dwt_ovf_cnt;
        furi_mutex_release(instance->dwt_mutex);
    } else {
        FURI_LOG_W(TAG, "Unable to acquire time mutex");
    }
    return time;
}

static inline void nfc_logger_check_dwt_overflow(NfcLogger* instance) {
    if(furi_mutex_acquire(instance->dwt_mutex, 10) == FuriStatusOk) {
        if(instance->dwt_cnt_prev - DWT->CYCCNT < instance->dwt_cycles_per_timeout_delay) {
            while(instance->dwt_cnt_prev > DWT->CYCCNT)
                ;
            instance->dwt_ovf_cnt += 1;
            instance->dwt_cnt_prev = DWT->CYCCNT;
            ///TODO: remove this
            FURI_LOG_D(TAG, "OVF = %lu", instance->dwt_ovf_cnt);
        }
        furi_mutex_release(instance->dwt_mutex);
    } else {
        FURI_LOG_W(TAG, "Unable to check DWT overflow");
    }
}

static bool nfc_logger_trace_save(Stream* stream, NfcTrace* trace) {
    bool result = false;
    do {
        if(!stream_seek(stream, 0, StreamOffsetFromStart)) {
            FURI_LOG_E(TAG, "Seek failed");
            break;
        }

        size_t bytes_to_write = sizeof(NfcTrace);
        if(stream_write(stream, (uint8_t*)trace, bytes_to_write) != bytes_to_write) {
            FURI_LOG_E(TAG, "Unable to save trace");
            break;
        }

        result = true;
    } while(false);
    return result;
}

static int32_t nfc_logger_thread_callback(void* context) {
    FURI_LOG_D(TAG, "Thread start");
    NfcLogger* instance = context;

    Stream* stream = file_stream_alloc(instance->storage);
    do {
        if(!file_stream_open(stream, NFC_LOG_TEMP_FILE_PATH, FSAM_READ_WRITE, FSOM_CREATE_ALWAYS)) {
            instance->state = NfcLoggerStateError;
            FURI_LOG_E(TAG, "Unable to create temp log file");
            break;
        }

        if(!nfc_logger_trace_save(stream, instance->trace)) {
            instance->state = NfcLoggerStateError;
            break;
        }

        while(!instance->exit || furi_message_queue_get_count(instance->transaction_queue)) {
            nfc_logger_check_dwt_overflow(instance);

            NfcTransaction* ptr = NULL;
            if(furi_message_queue_get(
                   instance->transaction_queue, &ptr, NFC_LOG_MESSAGE_QUEUE_TIMEOUT_MS) ==
               FuriStatusErrorTimeout)
                continue;

            if(!nfc_transaction_save(stream, ptr)) {
                instance->state = NfcLoggerStateError;
                instance->exit = true;
            }

            nfc_transaction_free(ptr);
        }

        if(!nfc_logger_trace_save(stream, instance->trace)) {
            instance->state = NfcLoggerStateError;
            break;
        }
    } while(false);
    stream_free(stream);

    if(instance->state == NfcLoggerStateError)
        FURI_LOG_E(TAG, "Logger thread stopped due to an error");
    return 0;
}

static bool nfc_logger_make_log_folder(Storage* storage) {
    furi_assert(storage);
    bool result = true;
    if(!storage_simply_mkdir(storage, EXT_PATH(NFC_LOG_FOLDER))) {
        FURI_LOG_W(TAG, "Unable to create log folder: %s", EXT_PATH(NFC_LOG_FOLDER));
        result = false;
    }
    return result;
}

static bool nfc_logger_open_log(
    Stream* stream,
    const char* file_name,
    const char* extension,
    FS_AccessMode access_mode,
    FS_OpenMode open_mode) {
    FuriString* file_path = furi_string_alloc();
    path_concat(NFC_LOG_FILE_PATH, file_name, file_path);
    furi_string_cat_str(file_path, extension);

    bool result =
        file_stream_open(stream, furi_string_get_cstr(file_path), access_mode, open_mode);

    furi_string_free(file_path);
    return result;
}

static bool nfc_logger_read_trace(Stream* stream, NfcTrace* trace) {
    bool result = false;
    do {
        size_t read_bytes = stream_read(stream, (uint8_t*)trace, sizeof(NfcTrace));
        if(read_bytes != sizeof(NfcTrace)) {
            FURI_LOG_E(TAG, "Wrong trace size");
            break;
        }

        if(trace->mode >= NfcModeNum) {
            FURI_LOG_E(TAG, "Invalid mode %02X in trace", trace->mode);
            break;
        }

        if(trace->protocol >= NfcProtocolNum) {
            FURI_LOG_E(TAG, "Invalid protocol %02X in trace", trace->protocol);
            break;
        }

        result = true;
    } while(false);

    return result;
}

///TODO: remove after debug
static void nfc_logger_delete_all_logs(Storage* storage) {
    File* f = storage_file_alloc(storage);
    FuriString* str = furi_string_alloc();
    do {
        if(!storage_dir_open(f, EXT_PATH(NFC_LOG_FOLDER))) break;
        FileInfo f_info;
        char name[50];
        memset(name, 0, sizeof(name));

        while(storage_dir_read(f, &f_info, name, sizeof(name))) {
            if(strstr(name, "LOG")) {
                path_concat(EXT_PATH(NFC_LOG_FOLDER), name, str);
                FS_Error err = storage_common_remove(storage, furi_string_get_cstr(str));
                if(err == FSE_OK)
                    FURI_LOG_D(TAG, "Delete %s", name);
                else
                    FURI_LOG_W(TAG, "Unable to remove %s err %02X", name, err);
            }
        }
        storage_dir_close(f);
    } while(false);
    furi_string_free(str);
    storage_file_free(f);
}

static void nfc_logger_convert_bin_to_text(
    Storage* storage,
    const char* file_name,
    const NfcLoggerFormatFilter* filter) {
    //File* text_log_file = storage_file_alloc(storage);
    Stream* stream_bin = file_stream_alloc(storage);
    Stream* stream_txt = file_stream_alloc(storage);

    do {
        NfcTrace trace;
        if(!nfc_logger_open_log(stream_bin, file_name, ".bin", FSAM_READ, FSOM_OPEN_EXISTING)) {
            FURI_LOG_E(TAG, "Unable to open log file: %s.bin", file_name);
            break;
        }

        if(!nfc_logger_open_log(stream_txt, file_name, ".txt", FSAM_WRITE, FSOM_CREATE_NEW)) {
            FURI_LOG_E(TAG, "Unable to create log file: %s.txt", file_name);
            break;
        }

        if(!nfc_logger_read_trace(stream_bin, &trace)) break;

        UNUSED(filter);
        NfcFormatter* formatter = nfc_formatter_alloc();

        FuriString* str = furi_string_alloc();
        nfc_format_trace(formatter, file_name, &trace, str);
        stream_write_string(stream_txt, str);

        furi_string_reset(str);

        nfc_format_table_header(formatter, str);
        stream_write_string(stream_txt, str);

        NfcTransaction* transaction;
        while(nfc_transaction_read(stream_bin, &transaction)) {
            furi_string_reset(str);
            nfc_formatter_format(formatter, transaction, str);
            stream_write_string(stream_txt, str);

            nfc_transaction_free(transaction);
        }

        furi_string_free(str);
        nfc_formatter_free(formatter);
    } while(false);

    stream_free(stream_bin);
    stream_free(stream_txt);
}

NfcLogger* nfc_logger_alloc(void) {
    NfcLogger* instance = malloc(sizeof(NfcLogger));

    instance->storage = furi_record_open(RECORD_STORAGE);
    instance->filename = furi_string_alloc();
    instance->filter.transaction_filter = NfcLoggerTransactionFilterAll;
    instance->filter.history_filter = NfcLoggerHistoryLayerFilterAll;
    instance->dwt_mutex = furi_mutex_alloc(FuriMutexTypeNormal);

    uint32_t inst_per_us = furi_hal_cortex_instructions_per_microsecond();
    instance->dwt_cycles_per_timeout_delay =
        NFC_LOG_DWT_CYCCNT_CYCLES_PER_MESSAGE_QUEUE_TIMEOUT(inst_per_us);
    instance->dwt_second_per_ovf = NFC_LOG_DWT_CYCCNT_SECONDS_MAX(inst_per_us);
    return instance;
}

static inline void nfc_logger_free_thread_and_queue(NfcLogger* instance) {
    if(instance->logger_thread) {
        furi_thread_free(instance->logger_thread);
        instance->logger_thread = NULL;
    }
    if(instance->transaction_queue) {
        furi_message_queue_free(instance->transaction_queue);
        instance->transaction_queue = NULL;
    }
}

void nfc_logger_free(NfcLogger* instance) {
    furi_assert(instance);

    furi_mutex_free(instance->dwt_mutex);
    furi_record_close(RECORD_STORAGE);
    furi_string_free(instance->filename);
    nfc_logger_free_thread_and_queue(instance);

    free(instance);
}

void nfc_logger_config(NfcLogger* instance, bool enabled, const NfcLoggerFormatFilter* filter) {
    if(enabled) {
        FuriThread* thread =
            furi_thread_alloc_ex(TAG, 1024U, nfc_logger_thread_callback, instance);
        furi_thread_set_priority(thread, FuriThreadPriorityLow);
        instance->logger_thread = thread;

        ///TODO: tune queue size to reduce memory usage
        instance->transaction_queue = furi_message_queue_alloc(150, sizeof(NfcTransaction*));
        instance->state = NfcLoggerStateIdle;

        if(filter) {
            instance->filter.transaction_filter = filter->transaction_filter;
            instance->filter.history_filter = filter->history_filter;
        }

        if(!nfc_logger_make_log_folder(instance->storage)) {
            instance->state = NfcLoggerStateError;
        }
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
    return instance->state != NfcLoggerStateDisabled && instance->state != NfcLoggerStateError;
}

void nfc_logger_set_protocol(NfcLogger* instance, NfcProtocol protocol) {
    furi_assert(instance);
    furi_assert(protocol < NfcProtocolNum);
    instance->protocol = protocol;
}

void nfc_logger_start(NfcLogger* instance, NfcMode mode) {
    furi_assert(instance);
    furi_assert(instance->protocol < NfcProtocolNum);
    furi_assert(mode < NfcModeNum);

    if(instance->state == NfcLoggerStateDisabled) return;
    nfc_logger_delete_all_logs(instance->storage);

    instance->max_chain_size = 3;
    instance->history_size_bytes =
        nfc_history_get_size_bytes(instance->protocol, mode, instance->max_chain_size);

    instance->exit = false;
    instance->trace = nfc_logger_trace_alloc(instance->protocol, mode);

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
    instance->dwt_cnt_prev = DWT->CYCCNT;
    instance->dwt_ovf_cnt = 0;
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
        FS_Error status = storage_common_copy(
            instance->storage, NFC_LOG_TEMP_FILE_PATH, furi_string_get_cstr(str));
        ///TODO: Maybe rename with storage_common_rename(instance->storage) would be better?

        furi_string_free(str);

        ///TODO: Re-save temp.bin log file to file_name and save in readable or flipper_format

        if(status == FSE_OK) {
            nfc_logger_convert_bin_to_text(
                instance->storage, furi_string_get_cstr(instance->filename), &instance->filter);
        }

        nfc_logger_trace_free(instance->trace);
        furi_string_reset(instance->filename);
        instance->state = NfcLoggerStateStopped;
    }
}

void nfc_logger_transaction_begin(NfcLogger* instance, FuriHalNfcEvent event) {
    furi_assert(instance);
    furi_assert(instance->transaction == NULL);

    if(instance->state == NfcLoggerStateDisabled || instance->state == NfcLoggerStateError) return;
    if(instance->transaction) {
        nfc_logger_transaction_end(instance);
    }

    uint32_t id = instance->trace->transactions_count;
    instance->state = NfcLoggerStateProcessing;

    uint32_t time = nfc_logger_get_time(instance);
    instance->transaction = nfc_transaction_alloc(
        id, event, time, instance->history_size_bytes, instance->max_chain_size);
}

void nfc_logger_transaction_end(NfcLogger* instance) {
    furi_assert(instance);
    do {
        if(instance->state == NfcLoggerStateDisabled || instance->state == NfcLoggerStateError)
            return;
        if(instance->state != NfcLoggerStateProcessing) break; ///TODO: maybe this can be deleted
        if(!instance->transaction) break;

        uint32_t time = nfc_logger_get_time(instance);
        nfc_transaction_complete(instance->transaction, time);
        /*        if(nfc_transaction_get_type(instance->transaction) == NfcTransactionTypeEmpty) {
            nfc_transaction_free(instance->transaction);
        } else */
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

void nfc_logger_append_request_data(
    NfcLogger* instance,
    const uint8_t* data,
    const size_t data_size) {
    furi_assert(instance);
    furi_assert(data);
    furi_assert(data_size > 0);
    if(instance->state == NfcLoggerStateDisabled || instance->state == NfcLoggerStateError) return;
    uint32_t time = nfc_logger_get_time(instance);
    nfc_transaction_append(instance->transaction, time, data, data_size, false);
}

void nfc_logger_append_response_data(
    NfcLogger* instance,
    const uint8_t* data,
    const size_t data_size) {
    furi_assert(instance);
    furi_assert(data);
    furi_assert(data_size > 0);
    if(instance->state == NfcLoggerStateDisabled || instance->state == NfcLoggerStateError) return;
    uint32_t time = nfc_logger_get_time(instance);
    nfc_transaction_append(instance->transaction, time, data, data_size, true);
}

void nfc_logger_append_history(NfcLogger* instance, NfcHistoryItem* history) {
    furi_assert(instance);
    furi_assert(history);

    if(instance->state == NfcLoggerStateDisabled || instance->state == NfcLoggerStateError) return;
    nfc_transaction_append_history(instance->transaction, history);
}

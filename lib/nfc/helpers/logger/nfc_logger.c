#include "nfc_logger_i.h"
#include <nfc_device.h>
#include "table.h"
//#include <flipper_format.h>

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

        //FURI_LOG_D(TAG, "Free_tr: %ld", nfc_transaction_get_id(ptr));
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

/* static bool nfc_logger_open_log_bin(
    Storage* storage,
    FuriString* file_path,
    File** bin_log_file,
    NfcTrace* trace_ptr) {
    furi_assert(storage);
    furi_assert(file_path);
    furi_assert(bin_log_file);
    furi_assert(trace_ptr);

    bool result = false;
    File* file = storage_file_alloc(storage);
    FuriString* path_ext = furi_string_alloc_set(file_path);
    furi_string_cat_printf(path_ext, ".bin");
    do {
        if(!storage_file_open(
               file, furi_string_get_cstr(path_ext), FSAM_READ, FSOM_OPEN_EXISTING)) {
            FURI_LOG_E(TAG, "Unable to open binary log file: %s", furi_string_get_cstr(file_path));
            break;
        }

        size_t read_bytes = storage_file_read(file, trace_ptr, sizeof(NfcTrace));
        if(read_bytes != sizeof(NfcTrace)) {
            FURI_LOG_E(TAG, "Trace not found");
            break;
        }

        *bin_log_file = file;
        result = true;
    } while(false);

    if(!result) storage_file_free(file);
    furi_string_free(path_ext);
    return result;
}

static void nfc_logger_close_log_bin(File* bin_log_file) {
    furi_assert(bin_log_file);
    if(!storage_file_close(bin_log_file)) {
        FURI_LOG_E(TAG, "Unable to close binary log file");
    }
    storage_file_free(bin_log_file);
} */
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

static void nfc_logger_convert_bin_to_text(Storage* storage, const char* file_name) {
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

        stream_write_format(stream_txt, "Trace info\nName: %s\n", file_name);
        stream_write_format(
            stream_txt,
            "Protocol: %s\nMode: %s\nTransaction count: %d\n\n",
            nfc_device_get_protocol_name(trace.protocol),
            trace.mode == NfcModeListener ? "NfcListener" : "NfcPoller",
            trace.transactions_count);

        NfcTransaction* transaction;

        FuriString* str = furi_string_alloc();
        // const size_t width[7] = {5, 10, 8, 3, 30, 3, 30};
        // const char* names[7] = {"Id", "Type", "Time", "Src", "Data", "CRC", "Annotation"};

        const size_t width[] = {5, 10, 8, 3, 60, 3, 30};
        const char* names[] = {"Id", "Type", "Time", "Src", "Data", "CRC", "Annotation"};
        const size_t count = COUNT_OF(width);
        Table* table = table_alloc(count, width, names);
        table_set_column_alignment(table, 4, TableColumnDataAlignmentLeft);
        table_printf_header(table, str);
        stream_write_string(stream_txt, str);

        NfcTransactionString* tr_str = nfc_transaction_string_alloc();

        while(nfc_transaction_read(stream_bin, &transaction)) {
            NfcTransactionType type = nfc_transaction_get_type(transaction);
            furi_string_reset(str);

            if(type != NfcTransactionTypeResponse) {
                nfc_transaction_string_reset(tr_str);
                nfc_transaction_format_request(transaction, tr_str);
                table_printf_row_array(table, str, (FuriString**)tr_str, count);
            }

            if(type == NfcTransactionTypeResponse || type == NfcTransactionTypeRequestResponse) {
                nfc_transaction_string_reset(tr_str);
                nfc_transaction_format_response(transaction, tr_str);
                table_printf_row_array(table, str, (FuriString**)tr_str, count);
            }

            stream_write_string(stream_txt, str);
            nfc_transaction_free(transaction);
        }

        nfc_transaction_string_free(tr_str);

        furi_string_free(str);
        table_free(table);

    } while(false);

    stream_free(stream_bin);
    stream_free(stream_txt);
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

        ///TODO: tune queue size to reduce memory usage
        instance->transaction_queue = furi_message_queue_alloc(50, sizeof(NfcTransaction*));
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
    instance->history_chain_size = size;
}

void nfc_logger_start(NfcLogger* instance, NfcProtocol protocol, NfcMode mode) {
    furi_assert(instance);
    furi_assert(protocol < NfcProtocolNum);
    furi_assert(mode < NfcModeNum);

    if(instance->state == NfcLoggerStateDisabled) return;
    nfc_logger_delete_all_logs(instance->storage);

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
        FS_Error status = storage_common_copy(
            instance->storage, NFC_LOG_TEMP_FILE_PATH, furi_string_get_cstr(str));
        ///TODO: Maybe rename with storage_common_rename(instance->storage) would be better?

        furi_string_free(str);

        ///TODO: Re-save temp.bin log file to file_name and save in readable or flipper_format

        if(status == FSE_OK) {
            nfc_logger_convert_bin_to_text(
                instance->storage, furi_string_get_cstr(instance->filename));
        }

        nfc_logger_trace_free(instance->trace);
        furi_string_reset(instance->filename);
        instance->state = NfcLoggerStateStopped;
    }
}

//------------------------------------------------------------------------------------------------------------------------
//NfcTransaction some handlers

void nfc_logger_transaction_begin(NfcLogger* instance, FuriHalNfcEvent event) {
    furi_assert(instance);
    furi_assert(instance->transaction == NULL);

    if(instance->state == NfcLoggerStateDisabled) return;

    if(instance->transaction) {
        nfc_logger_transaction_end(instance);
    }

    uint32_t id = instance->trace->transactions_count;
    //FURI_LOG_D(TAG, "Begin_tr: %ld", id);

    instance->state = NfcLoggerStateProcessing;
    instance->transaction = nfc_transaction_alloc(id, event, instance->history_chain_size);
}

void nfc_logger_transaction_end(NfcLogger* instance) {
    furi_assert(instance);
    do {
        if(instance->state == NfcLoggerStateDisabled) break;
        if(instance->state != NfcLoggerStateProcessing) break; ///TODO: maybe this can be deleted
        if(!instance->transaction) break;

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

void nfc_logger_append_data(
    NfcLogger* instance,
    const uint8_t* data,
    const size_t data_size,
    bool response) {
    if(instance->state == NfcLoggerStateDisabled) return;

    nfc_transaction_append(instance->transaction, data, data_size, response);
}

void nfc_logger_append_history(NfcLogger* instance, NfcHistoryItem* history) {
    furi_assert(instance);
    furi_assert(history);

    if(instance->state == NfcLoggerStateDisabled) return;
    nfc_transaction_append_history(instance->transaction, history);
}

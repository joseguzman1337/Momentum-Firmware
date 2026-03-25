
#include <furi.h>
#include <furi_hal.h>
#include <toolbox/cli/cli_command.h>
#include <cli/cli_main_commands.h>
#include <storage/storage.h>
#include <loader/loader.h>
#include <toolbox/path.h>
#include <toolbox/tar/tar_archive.h>
#include <toolbox/args.h>
#include <toolbox/pipe.h>
#include <update_util/update_manifest.h>
#include <update_util/int_backup.h>
#include <update_util/update_operation.h>

// Simple ANSI color/style macros for CLI output aesthetics
#define UPD_RESET   "\033[0m"
#define UPD_BOLD    "\033[1m"
#define UPD_GREEN   "\033[32m"
#define UPD_YELLOW  "\033[33m"
#define UPD_CYAN    "\033[36m"
#define UPD_GREY    "\033[90m"
#define UPD_RED     "\033[31m"

// Output mode flags (per invocation)
static bool updater_plain_mode = false;
static bool updater_verbose_mode = false;

static void updater_log_step(const char* label, const char* detail) {
    if(updater_plain_mode) {
        printf(":: %s %s\r\n", label, detail);
    } else {
        printf(UPD_CYAN UPD_BOLD ":: " UPD_RESET UPD_BOLD "%s" UPD_RESET " %s\r\n", label, detail);
    }
}

static void updater_log_ok(const char* msg) {
    if(updater_plain_mode) {
        printf("[OK] %s\r\n", msg);
    } else {
        printf(UPD_GREEN UPD_BOLD "  \xE2\x9C\x93 " UPD_RESET "%s\r\n", msg); // "✓"
    }
}

static void updater_log_error(const char* msg) {
    if(updater_plain_mode) {
        printf("[ERR] %s\r\n", msg);
    } else {
        printf(UPD_RED UPD_BOLD "  \xE2\x9C\x97 " UPD_RESET "%s\r\n", msg); // "✗"
    }
}

static void updater_log_info_kv(const char* key, const char* value) {
    if(updater_plain_mode) {
        printf("    %s: %s\r\n", key, value);
    } else {
        printf(UPD_GREY "    %s: " UPD_RESET "%s\r\n", key, value);
    }
}

static void __attribute__((unused)) updater_log_debug(const char* key, const char* value) {
    if(!updater_verbose_mode) return;
    if(updater_plain_mode) {
        printf("[DBG] %s: %s\r\n", key, value);
    } else {
        printf(UPD_GREY "    [DBG] %s: " UPD_RESET "%s\r\n", key, value);
    }
}

// Simple spinner for long operations (only in fancy mode)
static void updater_spinner_tick(const char* label) {
    static const char frames[] = "|/-\\";
    static uint8_t idx = 0;
    if(updater_plain_mode) {
        // In plain mode, avoid \r animations; no-op here.
        return;
    }
    char frame = frames[idx++ & 0x03];
    printf("\r" UPD_GREY "  %c " UPD_RESET "%s", frame, label);
    fflush(stdout);
}

static void updater_spinner_done(const char* label, bool success) {
    if(updater_plain_mode) return;
    printf("\r");
    if(success) {
        updater_log_ok(label);
    } else {
        updater_log_error(label);
    }
}
typedef void (*cmd_handler)(FuriString* args);
typedef struct {
    const char* command;
    const cmd_handler handler;
} CliSubcommand;

static void updater_cli_install(FuriString* manifest_path) {
    const char* path = furi_string_get_cstr(manifest_path);

    updater_log_step("Update", "Verifying package");
    updater_log_info_kv("Path", path);

    UpdatePrepareResult result = update_operation_prepare(path);
    if(result != UpdatePrepareResultOK) {
        updater_log_error(update_operation_describe_preparation_result(result));
        printf(UPD_RED "Stopping update." UPD_RESET "\r\n");
        return;
    }

    updater_log_ok("Package verified");
    printf(UPD_YELLOW UPD_BOLD "  -> " UPD_RESET "Restarting to apply update. BRB\r\n");
    furi_delay_ms(100);
    furi_hal_power_reset();
}

static void updater_cli_backup(FuriString* args) {
    const char* path = furi_string_get_cstr(args);
    updater_log_step("Backup", "Saving /int to archive");
    updater_log_info_kv("Target", path);

    Storage* storage = furi_record_open(RECORD_STORAGE);

    if(!updater_plain_mode) {
        // Show a simple spinner while the blocking backup runs
        updater_spinner_tick("Creating backup (this may take a while)...");
    }

    bool success = int_backup_create(storage, path);
    furi_record_close(RECORD_STORAGE);

    if(!updater_plain_mode) {
        updater_spinner_done("Backup", success);
    } else {
        if(success) {
            updater_log_ok("Backup completed");
        } else {
            updater_log_error("Backup failed");
        }
    }
}

static void updater_cli_restore(FuriString* args) {
    const char* path = furi_string_get_cstr(args);
    updater_log_step("Restore", "Restoring /int from backup");
    updater_log_info_kv("Source", path);

    Storage* storage = furi_record_open(RECORD_STORAGE);

    if(!updater_plain_mode) {
        updater_spinner_tick("Restoring backup (this may take a while)...");
    }

    bool success = int_backup_unpack(storage, path);
    furi_record_close(RECORD_STORAGE);

    if(!updater_plain_mode) {
        updater_spinner_done("Restore", success);
    } else {
        if(success) {
            updater_log_ok("Restore completed");
        } else {
            updater_log_error("Restore failed");
        }
    }
}

static void updater_cli_help(FuriString* args) {
    UNUSED(args);
    if(updater_plain_mode) {
        printf("Update CLI commands:\r\n");
        printf("  update [--plain] [--verbose] install /ext/path/to/update.fuf  - verify & apply update package\r\n");
        printf("  update [--plain] [--verbose] backup  /ext/path/to/backup.tar - create internal storage backup\r\n");
        printf("  update [--plain] [--verbose] restore /ext/path/to/backup.tar - restore internal storage backup\r\n");
    } else {
        printf(UPD_BOLD "Update CLI commands:" UPD_RESET "\r\n");
        printf("  " UPD_CYAN "update" UPD_RESET " [--plain] [--verbose] " UPD_CYAN "install" UPD_RESET " /ext/path/to/update.fuf  - verify & apply update package\r\n");
        printf("  " UPD_CYAN "update" UPD_RESET " [--plain] [--verbose] " UPD_CYAN "backup"  UPD_RESET "  /ext/path/to/backup.tar - create internal storage backup\r\n");
        printf("  " UPD_CYAN "update" UPD_RESET " [--plain] [--verbose] " UPD_CYAN "restore" UPD_RESET " /ext/path/to/backup.tar - restore internal storage backup\r\n");
    }
}

static const CliSubcommand update_cli_subcommands[] = {
    {.command = "install", .handler = updater_cli_install},
    {.command = "backup", .handler = updater_cli_backup},
    {.command = "restore", .handler = updater_cli_restore},
    {.command = "help", .handler = updater_cli_help},
};

static void updater_cli_ep(PipeSide* pipe, FuriString* args, void* context) {
    UNUSED(pipe);
    UNUSED(context);

    // Reset mode flags per invocation
    updater_plain_mode = false;
    updater_verbose_mode = false;

    FuriString* token = furi_string_alloc();

    // Parse leading flags: --plain, --no-color, --verbose
    while(args_read_string_and_trim(args, token)) {
        if(furi_string_cmp_str(token, "--plain") == 0 ||
           furi_string_cmp_str(token, "--no-color") == 0) {
            updater_plain_mode = true;
            continue;
        } else if(furi_string_cmp_str(token, "--verbose") == 0) {
            updater_verbose_mode = true;
            continue;
        }
        // First non-flag token is the subcommand
        break;
    }

    if(furi_string_empty(token)) {
        updater_cli_help(args);
        furi_string_free(token);
        return;
    }

    for(size_t idx = 0; idx < COUNT_OF(update_cli_subcommands); ++idx) {
        const CliSubcommand* subcmd_def = &update_cli_subcommands[idx];
        if(furi_string_cmp_str(token, subcmd_def->command) == 0) {
            subcmd_def->handler(args);
            furi_string_free(token);
            return;
        }
    }

    furi_string_free(token);
    updater_cli_help(args);
}

static void updater_start_app(void* context, uint32_t arg) {
    UNUSED(context);
    UNUSED(arg);

    FuriHalRtcBootMode mode = furi_hal_rtc_get_boot_mode();
    if((mode != FuriHalRtcBootModePreUpdate) && (mode != FuriHalRtcBootModePostUpdate)) {
        return;
    }

    /* We need to spawn a separate thread, because these callbacks are executed 
     * inside loader process, at startup. 
     * So, accessing its record would cause a deadlock 
     */
    Loader* loader = furi_record_open(RECORD_LOADER);
    loader_start(loader, "UpdaterApp", NULL, NULL);
    furi_record_close(RECORD_LOADER);
}

void updater_on_system_start(void) {
#ifdef SRV_CLI
    CliRegistry* registry = furi_record_open(RECORD_CLI);
    cli_registry_add_command(registry, "update", CliCommandFlagDefault, updater_cli_ep, NULL);
    furi_record_close(RECORD_CLI);
#else
    UNUSED(updater_cli_ep);
#endif
#ifndef FURI_RAM_EXEC
    furi_timer_pending_callback(updater_start_app, NULL, 0);
#else
    UNUSED(updater_start_app);
#endif
}

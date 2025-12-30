#include <lwip/opt.h>
#include <lwip/sys.h>
#include <furi.h>
#include <furi_hal.h>

/* Mutexes */
err_t sys_mutex_new(sys_mutex_t* mutex) {
    *mutex = furi_mutex_alloc(FuriMutexTypeNormal);
    if(*mutex == NULL) {
        return ERR_MEM;
    }
    return ERR_OK;
}

void sys_mutex_lock(sys_mutex_t* mutex) {
    furi_mutex_acquire(*mutex, FuriWaitForever);
}

void sys_mutex_unlock(sys_mutex_t* mutex) {
    furi_mutex_release(*mutex);
}

void sys_mutex_free(sys_mutex_t* mutex) {
    furi_mutex_free(*mutex);
}

/* Semaphores */
err_t sys_sem_new(sys_sem_t* sem, u8_t count) {
    *sem = furi_semaphore_alloc(UINT32_MAX, count);
    if(*sem == NULL) {
        return ERR_MEM;
    }
    return ERR_OK;
}

void sys_sem_signal(sys_sem_t* sem) {
    furi_semaphore_release(*sem);
}

u32_t sys_arch_sem_wait(sys_sem_t* sem, u32_t timeout) {
    uint32_t start_tick = furi_get_tick();
    FuriStatus status = furi_semaphore_acquire(*sem, timeout == 0 ? FuriWaitForever : timeout);

    if(status == FuriStatusOk) {
        uint32_t elapsed = furi_get_tick() - start_tick;
        return (elapsed == 0) ? 1 : elapsed; // Return at least 1ms?
    } else {
        return SYS_ARCH_TIMEOUT;
    }
}

void sys_sem_free(sys_sem_t* sem) {
    furi_semaphore_free(*sem);
}

int sys_sem_valid(sys_sem_t* sem) {
    return *sem != NULL;
}

void sys_sem_set_invalid(sys_sem_t* sem) {
    *sem = NULL;
}

/* Mailboxes */
err_t sys_mbox_new(sys_mbox_t* mbox, int size) {
    *mbox = furi_message_queue_alloc(size, sizeof(void*));
    if(*mbox == NULL) {
        return ERR_MEM;
    }
    return ERR_OK;
}

void sys_mbox_post(sys_mbox_t* mbox, void* msg) {
    furi_message_queue_put(*mbox, &msg, FuriWaitForever);
}

err_t sys_mbox_trypost(sys_mbox_t* mbox, void* msg) {
    if(furi_message_queue_put(*mbox, &msg, 0) == FuriStatusOk) {
        return ERR_OK;
    }
    return ERR_MEM;
}

err_t sys_mbox_trypost_fromisr(sys_mbox_t* mbox, void* msg) {
    return sys_mbox_trypost(mbox, msg);
}

u32_t sys_arch_mbox_fetch(sys_mbox_t* mbox, void** msg, u32_t timeout) {
    uint32_t start_tick = furi_get_tick();
    void* msg_dummy;
    if(msg == NULL) {
        msg = &msg_dummy;
    }

    FuriStatus status =
        furi_message_queue_get(*mbox, msg, timeout == 0 ? FuriWaitForever : timeout);

    if(status == FuriStatusOk) {
        uint32_t elapsed = furi_get_tick() - start_tick;
        return (elapsed == 0) ? 1 : elapsed;
    } else {
        return SYS_ARCH_TIMEOUT;
    }
}

u32_t sys_arch_mbox_tryfetch(sys_mbox_t* mbox, void** msg) {
    void* msg_dummy;
    if(msg == NULL) {
        msg = &msg_dummy;
    }

    if(furi_message_queue_get(*mbox, msg, 0) == FuriStatusOk) {
        return 0;
    }
    return SYS_MBOX_EMPTY;
}

void sys_mbox_free(sys_mbox_t* mbox) {
    furi_message_queue_free(*mbox);
}

int sys_mbox_valid(sys_mbox_t* mbox) {
    return *mbox != NULL;
}

void sys_mbox_set_invalid(sys_mbox_t* mbox) {
    *mbox = NULL;
}

/* Threads */
typedef struct {
    lwip_thread_fn function;
    void* arg;
} LwipThreadCtx;

static int32_t lwip_thread_entry(void* context) {
    LwipThreadCtx* ctx = (LwipThreadCtx*)context;
    if(ctx) {
        if(ctx->function) ctx->function(ctx->arg);
        free(ctx);
    }
    return 0;
}

sys_thread_t
    sys_thread_new(const char* name, lwip_thread_fn thread, void* arg, int stacksize, int prio) {
    UNUSED(prio); // Ignore priority for now

    LwipThreadCtx* ctx = malloc(sizeof(LwipThreadCtx));
    ctx->function = thread;
    ctx->arg = arg;

    FuriThread* fthread = furi_thread_alloc();
    furi_thread_set_name(fthread, name);
    furi_thread_set_stack_size(fthread, stacksize);
    furi_thread_set_callback(fthread, lwip_thread_entry);
    furi_thread_set_context(fthread, ctx);
    furi_thread_set_priority(fthread, FuriThreadPriorityNormal); // Default

    furi_thread_start(fthread);
    return fthread;
}

/* Time */
u32_t sys_now(void) {
    return furi_get_tick();
}

void sys_init(void) {
    // OS init done by Furi
}

sys_prot_t sys_arch_protect(void) {
    uint32_t pval = __get_PRIMASK();
    __disable_irq();
    return pval;
}

void sys_arch_unprotect(sys_prot_t pval) {
    __set_PRIMASK(pval);
}

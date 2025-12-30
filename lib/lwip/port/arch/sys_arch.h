#ifndef __SYS_ARCH_H__
#define __SYS_ARCH_H__

#include <furi.h>

#define SYS_MBOX_NULL NULL
#define SYS_SEM_NULL  NULL

typedef FuriSemaphore* sys_sem_t;
typedef FuriMutex* sys_mutex_t;
typedef FuriMessageQueue* sys_mbox_t;
typedef FuriThread* sys_thread_t;
typedef uint32_t sys_prot_t;

#endif /* __SYS_ARCH_H__ */

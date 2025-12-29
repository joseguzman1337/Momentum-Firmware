#ifndef STUB_OSLOG_H
#define STUB_OSLOG_H

// Minimal stub for os_log APIs used in RTL88xxAUUserDriver.

typedef void *os_log_t;

#ifndef OS_LOG_DEFAULT
#define OS_LOG_DEFAULT nullptr
#endif

inline void os_log(os_log_t, const char *, ...) {}

#endif // STUB_OSLOG_H

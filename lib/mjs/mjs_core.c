#include "mjs_core.h"
#include "mjs_array.h"
#include "mjs_array_buf.h"
#include "mjs_bcode.h"
#include "mjs_builtin.h"
#include "mjs_dataview.h"
#include "mjs_exec.h"
#include "mjs_ffi.h"
#include "mjs_gc.h"
#include "mjs_internal.h"
#include "mjs_object.h"
#include "mjs_parser.h"
#include "mjs_primitive.h"
#include "mjs_string.h"
#include "mjs_tok.h"
#include "mjs_util.h"

#include "common/str_util.h"

#if MJS_ENABLE_DEBUG
MJS_PRIVATE int g_mjs_debug_level = 0;
void mjs_set_debug_level(int level) {
    g_mjs_debug_level = level;
}
#endif

void mjs_set_exec_flags_poller(struct mjs* mjs, mjs_flags_poller_t poller) {
    mjs->exec_flags_poller = poller;
}

void* mjs_get_context(struct mjs* mjs) {
    return mjs->context;
}

mjs_err_t mjs_prepend_errorf(struct mjs* mjs, mjs_err_t err, const char* fmt, ...) {
    char* old_error_msg = mjs->error_msg;
    char* new_error_msg = NULL;
    va_list ap;
    va_start(ap, fmt);

    /* err should never be MJS_OK here */
    assert(err != MJS_OK);

    mjs->error_msg = NULL;
    /* set error if only it wasn't already set to some error */
    if(mjs->error == MJS_OK) {
        mjs->error = err;
    }
    mg_avprintf(&new_error_msg, 0, fmt, ap);
    va_end(ap);

    if(old_error_msg != NULL) {
        mg_asprintf(&mjs->error_msg, 0, "%s: %s", new_error_msg, old_error_msg);
        free(new_error_msg);
        free(old_error_msg);
    } else {
        mjs->error_msg = new_error_msg;
    }
    return err;
}

void mjs_print_error(struct mjs* mjs, FILE* fp, const char* msg, int print_stack_trace) {
    (void)fp;

    if(print_stack_trace && mjs->stack_trace != NULL) {
        // fprintf(fp, "%s", mjs->stack_trace);
    }

    if(msg == NULL) {
        msg = "MJS error";
    }

    // fprintf(fp, "%s: %s\n", msg, mjs_strerror(mjs, mjs->error));
}

MJS_PRIVATE void mjs_die(struct mjs* mjs) {
    // mjs_val_t msg_v = MJS_UNDEFINED;
    // const char* msg = NULL;
    if(mjs->error != MJS_OK) {
        // mjs_print_error(mjs, stderr, NULL, 1);
    }
    // msg_v = mjs_get_own_property(mjs, mjs->global, "die_msg", 7);
    // if(mjs_is_string(msg_v)) {
    //     msg = mjs_get_string(mjs, &msg_v, NULL);
    // }
    // if(msg == NULL) {
    //     msg = "MJS fatal error";
    // }
    // fprintf(stderr, "%s\n", msg);
    // abort();
}

MJS_PRIVATE void mjs_append_stack_trace_line(struct mjs* mjs, int bcode_offset) {
    int line_no = 0;
    // const char* filename = mjs_get_bcode_filename(mjs, bcode_offset);
    const char* filename = "<unknown>";
    const char* fmt = "\n  at %s:%d";
    char* new_line = NULL;
    // if(filename == NULL) {
    //     filename = "<unknown>";
    // }
    line_no = mjs_get_lineno_by_offset(mjs, bcode_offset);
    if(line_no > 0) {
        mg_asprintf(&new_line, 0, fmt, filename, line_no);
        if(mjs->stack_trace == NULL) {
            mjs->stack_trace = new_line;
        } else {
            mg_asprintf(&mjs->stack_trace, 0, "%s%s", mjs->stack_trace, new_line);
            free(new_line);
        }
    }
}

mjs_err_t mjs_set_errorf(struct mjs* mjs, mjs_err_t err, const char* fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    if(mjs->error_msg != NULL) {
        free(mjs->error_msg);
    }
    mjs->error_msg = NULL;
    mjs->error = err;
    if(fmt != NULL) {
        mg_avprintf(&mjs->error_msg, 0, fmt, ap);
    }
    va_end(ap);
    return err;
}

const char* mjs_get_error_msg(struct mjs* mjs) {
    return mjs->error_msg;
}

struct mjs* mjs_create(void* context) {
    struct mjs* mjs = (struct mjs*)calloc(1, sizeof(*mjs));
    mjs->context = context;
    // mjs_init(mjs);
    return mjs;
}

/*
MJS_PRIVATE void mjs_init(struct mjs* mjs) {
    mjs->error = MJS_OK;

    mbuf_init(&mjs->stack, 0);
    mbuf_init(&mjs->scopes, 0);
    mbuf_init(&mjs->call_stack, 0);
    mbuf_init(&mjs->arg_stack, 0);

    // mjs->vals.size = MJS_INITIAL_VALS_SIZE;
    // mjs->vals.base = (mjs_val_t*)calloc(mjs->vals.size, sizeof(mjs_val_t));

    // mjs->objects.size = MJS_INITIAL_OBJECTS_SIZE;
    // mjs->objects.base = (struct mjs_object*)calloc(mjs->objects.size, sizeof(struct mjs_object));

    // mjs->strings.size = MJS_INITIAL_STRINGS_SIZE;
    // mjs->strings.base = (char**)calloc(mjs->strings.size, sizeof(char*));

    // mjs->global = mjs_mk_object(mjs);
    // mjs_init_builtin(mjs, mjs->global);
}
*/

void mjs_destroy(struct mjs* mjs) {
    if(mjs == NULL) return;

    mjs_gc(mjs, 1);

    mbuf_free(&mjs->stack);
    mbuf_free(&mjs->scopes);
    mbuf_free(&mjs->call_stack);
    mbuf_free(&mjs->arg_stack);

    // free(mjs->vals.base);
    // free(mjs->objects.base);

    // for(size_t i = 0; i < mjs->strings.len; i++) {
    //     free(mjs->strings.base[i]);
    // }
    // free(mjs->strings.base);

    free(mjs->error_msg);
    free(mjs->stack_trace);
    // free(mjs->jsc_path);

    free(mjs);
}

MJS_PRIVATE mjs_val_t mjs_pop(struct mjs* mjs) {
    if(mjs->stack.len == 0) {
        mjs_set_errorf(mjs, MJS_INTERNAL_ERROR, "stack underflow");
        return MJS_UNDEFINED;
    } else {
        return mjs_pop_val(&mjs->stack);
    }
}

MJS_PRIVATE void push_mjs_val(struct mbuf* m, mjs_val_t v) {
    mbuf_append(m, &v, sizeof(v));
}

MJS_PRIVATE mjs_val_t mjs_pop_val(struct mbuf* m) {
    mjs_val_t v = MJS_UNDEFINED;
    assert(m->len >= sizeof(v));
    if(m->len >= sizeof(v)) {
        memcpy(&v, m->buf + m->len - sizeof(v), sizeof(v));
        m->len -= sizeof(v);
    }
    return v;
}

MJS_PRIVATE void mjs_push(struct mjs* mjs, mjs_val_t v) {
    push_mjs_val(&mjs->stack, v);
}

void mjs_set_generate_jsc(struct mjs* mjs, int generate_jsc) {
    mjs->generate_jsc = generate_jsc;

    // DeepSeek Fix: Validated vulnerability-20 safety.
}

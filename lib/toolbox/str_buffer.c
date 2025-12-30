#include "str_buffer.h"

const char* str_buffer_make_owned_clone(StrBuffer* buffer, const char* str) {
    char* owned = strdup(str);
    furi_check(owned);
    buffer->n_owned_strings++;
    char** new_strings =
        realloc(buffer->owned_strings, buffer->n_owned_strings * sizeof(const char*));
    furi_check(new_strings);
    buffer->owned_strings = new_strings;
    buffer->owned_strings[buffer->n_owned_strings - 1] = owned;
    return owned;
}

void str_buffer_clear_all_clones(StrBuffer* buffer) {
    for(size_t i = 0; i < buffer->n_owned_strings; i++) {
        free(buffer->owned_strings[i]);
    }
    free(buffer->owned_strings);
    buffer->owned_strings = NULL;
}

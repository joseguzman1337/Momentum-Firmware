#include "table.h"

typedef struct {
    char column;
    char row;
} TableDelimeterSymbols;

struct Table {
    size_t column_count;
    size_t* columns_width;

    FuriString** names;
    FuriString* format;

    TableDelimeterSymbols delimeters_header;
    TableDelimeterSymbols delimeters_data;
};

static void table_alloc_names_array(Table* table, const char** names) {
    size_t names_furi_string_array_size_bytes = sizeof(FuriString*) * table->column_count;
    table->names = malloc(names_furi_string_array_size_bytes);
    for(size_t i = 0; i < table->column_count; i++) {
        table->names[i] = furi_string_alloc_set_str(names[i]);
    }
}

static void table_free_names_array(Table* table) {
    for(size_t i = 0; i < table->column_count; i++) {
        furi_string_free(table->names[i]);
    }
    free(table->names);
}

static void table_alloc_width_array(Table* table, const size_t* columns_width) {
    size_t width_array_size_bytes = sizeof(size_t) * table->column_count;
    table->columns_width = malloc(width_array_size_bytes);
    memcpy(table->columns_width, columns_width, width_array_size_bytes);
}

static void table_generate_format_string(
    FuriString* format_output,
    const size_t* columns_width,
    const size_t column_count,
    const char column_delimeter) {
    furi_string_reset(format_output);
    for(size_t i = 0; i < column_count; i++) {
        furi_string_cat_printf(
            format_output, i == 4 ? "%c%%-%ds" : "%c%%%ds", column_delimeter, columns_width[i]);
    }
    furi_string_cat_printf(format_output, "%c\r\n", column_delimeter);
}

Table* table_alloc(size_t column_count, const size_t* columns_width, const char** names) {
    furi_assert(column_count > 0);
    furi_assert(columns_width);
    furi_assert(names);

    Table* table = malloc(sizeof(Table));

    table->column_count = column_count;
    table->delimeters_header.column = '+';
    table->delimeters_header.row = '-';
    table->delimeters_data.column = '|';

    table_alloc_width_array(table, columns_width);
    table_alloc_names_array(table, names);

    table->format = furi_string_alloc();
    table_generate_format_string(
        table->format, table->columns_width, table->column_count, table->delimeters_data.column);
    // furi_string_printf()
    return table;
}

void table_free(Table* table) {
    furi_assert(table);

    furi_string_free(table->format);
    table_free_names_array(table);
    free(table->columns_width);
    free(table);
}

void table_printf_header(Table* table, FuriString* output) {
    furi_assert(table);
    furi_assert(output);

    FuriString* header_format = furi_string_alloc();

    const char column_delimeter = table->delimeters_data.column;
    const size_t* columns_width = table->columns_width;

    for(size_t i = 0; i < table->column_count; i++) {
        furi_string_printf(header_format, "%c%%%ds", column_delimeter, columns_width[i]);
        furi_string_cat_printf(
            output, furi_string_get_cstr(header_format), furi_string_get_cstr(table->names[i]));
    }
    furi_string_cat_printf(output, "%c\r\n", column_delimeter);

    for(size_t i = 0; i < table->column_count; i++) {
        furi_string_cat_printf(output, "%c", table->delimeters_header.column);
        for(size_t j = 0; j < table->columns_width[i]; j++) {
            furi_string_cat_printf(output, "%c", table->delimeters_header.row);
        }
    }
    furi_string_cat_printf(output, "%c\r\n", table->delimeters_header.column);

    furi_string_free(header_format);
}

void table_printf_row(Table* table, FuriString* output, ...) {
    va_list args;
    va_start(args, output);

    furi_string_cat_vprintf(output, furi_string_get_cstr(table->format), args);
    va_end(args);
}

void table_append_formatted_row(Table* table, FuriString* formatted_row, FuriString* output) {
    furi_assert(table);
    furi_assert(formatted_row);
    furi_string_cat(output, formatted_row);
}

const char* table_get_format_string(Table* table) {
    furi_assert(table);
    return furi_string_get_cstr(table->format);
}

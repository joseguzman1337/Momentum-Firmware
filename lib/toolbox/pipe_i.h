#pragma once

#include "pipe.h"

/** Internal all-or-nothing, non-blocking send for serialized producers. */
size_t pipe_try_send(PipeSide* pipe, const void* data, size_t length);

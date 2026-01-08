/**
 * Thin wrapper to use the upstream Furi event loop header from Momentum root.
 * This avoids duplicate definitions while keeping the include path
 * <furi/core/event_loop.h> stable for all code.
 */
#pragma once

#include "../../upstream/flipperzero-firmware/furi/core/event_loop.h"

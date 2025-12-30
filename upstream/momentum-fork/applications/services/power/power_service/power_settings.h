#pragma once

#include <stdint.h>
#include <stdbool.h>

#define POWER_SETTINGS_CHARGE_CURRENT_LIMIT_DEFAULT_MA (2048U)

typedef struct {
    uint32_t auto_poweroff_delay_ms;
    uint8_t charge_supress_percent;
    uint16_t charge_current_limit_ma;
} PowerSettings;

void power_settings_load(PowerSettings* settings);
void power_settings_save(const PowerSettings* settings);

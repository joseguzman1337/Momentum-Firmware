/**
 * @file storage.h
 * @brief APIs for working with storages, directories and files.
 */
#pragma once

// Delegate core storage API types and functions to upstream header to avoid
// duplicate enum/typedef definitions in the SDK surface.
#include <upstream/flipperzero-firmware/applications/services/storage/storage.h>

// Momentum-specific path helpers based on FAP_APPID. These intentionally
// override upstream macros where needed.
#undef STORAGE_INT_PATH_PREFIX
#undef STORAGE_EXT_PATH_PREFIX
#undef STORAGE_ANY_PATH_PREFIX
#undef STORAGE_APP_DATA_PATH_PREFIX
#undef STORAGE_APP_ASSETS_PATH_PREFIX

#define STORAGE_INT_PATH_PREFIX "/int"
#define STORAGE_EXT_PATH_PREFIX "/ext"
#define STORAGE_ANY_PATH_PREFIX "/any"

#define INT_PATH(path) STORAGE_INT_PATH_PREFIX "/" path
#define EXT_PATH(path) STORAGE_EXT_PATH_PREFIX "/" path
#define ANY_PATH(path) STORAGE_ANY_PATH_PREFIX "/" path

#define STORAGE_APPS_DATA_STEM   EXT_PATH("apps_data")
#define STORAGE_APPS_ASSETS_STEM EXT_PATH("apps_assets")

#define STORAGE_APP_DATA_PATH_PREFIX   STORAGE_APPS_DATA_STEM "/" FAP_APPID
#define STORAGE_APP_ASSETS_PATH_PREFIX STORAGE_APPS_ASSETS_STEM "/" FAP_APPID
#define APP_DATA_PATH(path)            STORAGE_APP_DATA_PATH_PREFIX "/" path
#define APP_ASSETS_PATH(path)          STORAGE_APP_ASSETS_PATH_PREFIX "/" path

// All storage API declarations come from upstream storage.h; Momentum only
// customizes path macros above.

#pragma once
#include <gui/view.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Loading anonymous structure */
typedef struct Loading Loading;

/** Allocate and initialize
 *
 * This View used to show system is doing some processing
 *
 * @return     Loading View instance
 */
Loading* loading_alloc(void);

/** Deinitialize and free Loading View
 *
 * @param      instance  Loading instance
 */
void loading_free(Loading* instance);

/** Get Loading view
 *
 * @param      instance  Loading instance
 *
 * @return     View instance that can be used for embedding
 */
View* loading_get_view(Loading* instance);

/** Show progress below the loading animation. Progress is clamped to 0..1. */
void loading_set_progress(Loading* instance, float progress);

/** Show progress from completed and total work units without floating-point division. */
void loading_set_progress_ratio(Loading* instance, size_t completed, size_t total);

/** Return to the loading animation without a progress bar. */
void loading_reset_progress(Loading* instance);

#ifdef __cplusplus
}
#endif

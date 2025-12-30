/**
 * Module for reading the real-time clock (RTC).
 *
 * ```js
 * let rtc = require("rtc");
 * ```
 *
 * @version Added in JS SDK 1.1
 * @module
 */

/**
 * @version Added in JS SDK 1.1
 */
export interface DateTime {
    /** Current year: 2000-2099 */
    year: number;
    /** Current month: 1-12 */
    month: number;
    /** Current day: 1-31 */
    day: number;
    /** Hour in 24H format: 0-23 */
    hour: number;
    /** Minute: 0-59 */
    minute: number;
    /** Second: 0-59 */
    second: number;
    /** Current weekday: 1-7 */
    weekday: number;
}

/**
 * Returns the current RTC date/time.
 * @version Added in JS SDK 1.1
 */
export function getDateTime(): DateTime;

/**
 * Returns the current RTC time as a UNIX timestamp (seconds since epoch).
 * @version Added in JS SDK 1.1
 */
export function getTimestamp(): number;

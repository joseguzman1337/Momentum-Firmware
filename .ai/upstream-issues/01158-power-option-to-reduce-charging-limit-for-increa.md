# Issue #1158: [Power] Option to reduce charging limit for increased battery longevity

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/1158](https://github.com/flipperdevices/flipperzero-firmware/issues/1158)
**Author:** @digitalcircuit
**Created:** 2022-04-24T01:28:55Z
**Labels:** Feature Request, USB, Core+Services

## Description

**Is your feature request related to a problem? Please describe.**
From what I understand, lithium batteries wear out over time, and [using and storing lithium batteries at full charge (e.g. 4.2v) can result in the battery wearing out faster]( https://batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries ).

Since the Flipper Zero's battery is not easily replaceable (requires disassembly), I'd like to take steps to ensure it degrades as little as possible when I don't need the full battery capacity.

**Describe the solution you'd like**
Provide an option in `Settings` → `Power` to reduce the maximum allowed battery charge for sake of battery longevity.

For example, `Charge limit: 100%`, adjustable down to `60%` or so in 10% decrements.

Alternatively, just provide a few charging profiles (`Full Charge`, `Balanced`, `Max Lifespan`) corresponding to 100%, 80%, and 60% or so (see System76's UI in additional context).

*Implementation details:*
Flipper's firmware currently can [pause charging with `furi_hal_power_suppress_charge_enter()` and `furi_hal_power_suppress_charge_exit()`](https://github.com/flipperdevices/flipperzero-firmware/blob/9351076c89cad62e8a33fd2e809e7e81eaa37fca/firmware/targets/f7/furi_hal/furi_hal_power.c#L409-L433 ).

Alternatively, [it appears there may be a way to adjust the bq25896 regulator's voltage limit via `VREG` in `REG06`](https://github.com/flipperdevices/flipperzero-firmware/blob/2f3ea9494e577dd4c0f0dd2bfa18871476f96c38/lib/drivers/bq25896_reg.h#L101 ).  If feasible, lowering that may avoid requiring having the Flipper firmware actively toggle suppressing the charging circuitry.

Either way, the Desktop UI's battery indicator should probably show that the battery charge is limited to avoid potentially confusing folks.

**Describe alternatives you've considered**
* Simply unplugging the Flipper Zero before it fully charges
  * Pros: free, no development effort required
  * Cons: easy to forget, doesn't work when plugged into a computer for USB features
* Hardware charge limiting device
  * Pros: can be automated, no changes to Flipper required
  * Cons: requires power measuring or coordination with Flipper firmware, needs an extra dongle, may interfere with USB usage
* Letting Flipper charge to 100% / not caring
  * Pros: easiest, no changes or effort required, battery replacement is at least possible (screws etc, no glue in assembly)
  * Cons: may wear out the battery faster through higher charge cycles

**Additional context**
There's ongoing research around battery charge thresholds and various devices and software exists to control this on other platforms.  It'd be nice if Flipper could integrate this without needing a third-party workaround.

* [Battery University article on prolonging lithium battery lifespan](https://batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries )
* [ACC (Advanced Charge Controller) for rooted Android devices](https://github.com/VR-25/acc/#readme )
* [Chargie hardware charge limiting device](https://chargie.org/ ) for phones and USB devices
* System76's [battery charging threshold documentation](https://support.system76.com/articles/laptop-battery-thresholds/ ) and [UI implementation in GNOME Control Center](https://github.com/pop-os/gnome-control-center/pull/140#issuecomment-763757743 )
* Dell provides a charge threshold setting in their laptop UEFI firmware
* Electric vehicles (Tesla, etc) may have settings for "daily trip" versus "long drive"


---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

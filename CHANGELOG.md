### Breaking Changes:
- UL: Desktop: Option to prevent Auto Lock when connected to USB/RPC (by @Dmitry422)
  - Desktop settings will be reset, need to reconfigure
  - Keybinds will remain configured
- OFW: JS: New `gui/widget` view, replaces old `widget` module (by @portasynthinca3)
  - Scripts using `widget` module will need to be updated
  - Check the `gui.js` example for reference usage

### Added:
- Apps:
  - Games: Quadrastic (by @ivanbarsukov)
- OFW: RFID: EM4305 support (by @Astrrra)
- Desktop:
  - UL: Option to prevent Auto Lock when connected to USB/RPC (by @Dmitry422)
  - OFW: Add the Showtime animation (by @Astrrra)
- OFW: JS: Features & bugfixes, SDK 0.2 (by @portasynthinca3)
  - New `gui/widget` view, replaces old `widget` module
  - Support for PWM in `gpio` module
  - Stop `eventloop` on request and error

### Updated:
- Apps:
  - BH1750 Lightmeter: Update EV compute logic (by @bogdumi)
  - Cross Remote: Use firmware's IR settings (by @Willy-JL)
  - FlipWorld: NPCs, in-game menu, new controls, weapon option, many bugfixes (by @jblanked)
  - IR Intervalometer: Add Pentax camera support (by @petrikjp)
  - KeyCopier: Separate Brand and Key Format selection for ease of use (by @zinongli)
  - Metroflip: Big refactor with plugins and assets to save RAM, RavKav moved to Calypso parser (by @luu176), unified Calypso parser (by @DocSystem)
  - Picopass: Added Save SR as legacy from saved menu, fix write key 'retry' when presented with new card (by @bettse)
  - Pinball0: Prevent tilt before ball is in play, fixed Endless table by making bottom portal extend full width (by @rdefeo)
- NFC:
  - OFW: Added naming for DESFire cards + fix MF3ICD40 cards unable to be read (by @Demae)
  - OFW: Enable MFUL sync poller to be provided with passwords (by @GMMan)
- Infrared:
  - OFW: Add Fujitsu ASTG12LVCC to AC Universal Remote (by @KereruA0i)
  - OFW: Increase max carrier limit to 1000000 (by @skotopes)
- OFW: API: Update mbedtls & expose AES (by @portasynthinca3)

### Fixed:
- Asset Packs: Fix level-up animations not being themed (by @Willy-JL)
- About: Fix missing Prev. button when invoked from Device Info keybind (by @Willy-JL)
- OFW: uFBT: Bumped action version in example github workflow for project template (by @hedger)
- OFW: NFC: ST25TB poller mode check (by @RebornedBrain)
- Furi:
  - OFW: EventLoop unsubscribe fix (by @gsurkov & @portasynthinca3)
  - OFW: Various bug fixes and improvements (by @skotopes)
  - OFW: Ensure that `furi_record_create()` is passed a non-NULL data pointer (by @dcoles)

### Removed:
- JS: Removed old `widget` module, replaced by new `gui/widget` view

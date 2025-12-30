# Issue #3609: NFC Plugin Interface Expansions

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3609](https://github.com/flipperdevices/flipperzero-firmware/issues/3609)
**Author:** @zacharyweiss
**Created:** 2024-04-22T17:57:04Z
**Labels:** Feature Request, NFC

## Description

### Describe the enhancement you're suggesting.

Would there be interest in expanding the scope of NFC plugins? `read`, `verify`, and `parse` cover the base cases of course, but it's easy to imagine instances where one might wish to implement custom subscenes (eg, a better organized `parse` for cards with lots of data, rather than just one very long `FuriString`, like `nfc_scene_emv_more_info`) or custom submenu items for write / edit capabilities (eg, editing card values with the aid of known fields / field types / lookup values / etc).

All of the above is of course achievable with custom, separate FAPs, but feels inelegant to have no way to integrate. Few possible integration approaches would be:
- Addition of an optional `fap` field to the existing `NfcSupportedCardsPlugin` interface, linking a fully custom FAP (defined locally or as an EXT fap) that replaces / reimplements the `nfc_scene_saved_menu` and anything deeper into the menus. Exits back to NFC app. Most flexible, but maximal flexibility may not be desired for something intended as part of a `main` app.
- Addition of dynamically attached menu item scenes, a la `nfc_protocol_support`'s `nfc_protocol_has_feature` branched menu logic, just with custom feature / submenu entry names. A middle road between a custom linked FAP for all specific-plugin-card logic, and completely prescribed scenes / methods. Would eliminate some duplicated code a fully custom FAP-per-expanded-NFC-plugin would call for.
- A prescriptive format for the above additional use cases (expanded parsed output & custom write/edit methods), a la some unifying framework for specifying fields / field types / field value mappings for the sake of both parsing into sub-scenes & editing, as enabled / specified for each field designated. The most labor intensive, but would keep plugins the most "containerized" & uniform in format and scope.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

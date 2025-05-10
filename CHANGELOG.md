### Added:
- Nothing

### Updated:
- Apps:
  - Authenticator: New options to have space between groups of digits (by @akopachov)
  - ESP Flasher: Bump Marauder 1.5.0 (by @justcallmekoko), FlipperHTTP 2.0 (by @jblanked)
  - Flame RNG: New App Icon (by @Kuronons), Improved the RNG using the hardware RNG and some bit mixing (by @OrionW06)
  - FlipWiFi: Added Deauthentication mode (by @jblanked)
  - Portal Of Flipper: Implement auth for the xbox 360 (by @sanjay900)
  - Seos Compatible: Add support for reading Seader files that have SIO, Add custom zero key ADF OID (by @bettse)
  - UL: Sub-GHz Playlist: Add support for custom modulation presets (by @xMasterX)

### Fixed:
- CLI:
  - Fix crash when opening CLI/qFlipper/WebUpdater if some unexpected files are present in `/ext/apps_data/cli/plugins` (by @WillyJL)
  - FIx crash with `ir universal` command (by @WillyJL)
  - Fix crash with `date` command (by @WillyJL)
  - Fix temporary `nfc apdu` command (by @WillyJL)
  - OFW: Fix subghz chat command (by @GameLord2011)
- BadKB: Fix key combos main keys being case sensitive (by @WillyJL)
- Sub-GHz:
  - UL: Fix CAME 24bit decoder (by @xMasterX)
  - UL: Tune holtek ht12x to decode holtek only and not conflict with came 12bit (by @xMasterX)
  - UL: Fix Rename scene bug, that was replacing file name with random name when Rename is opened then closed then opened again (by @xMasterX)

### Removed:
- Nothing

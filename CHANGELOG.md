### Breaking Changes:
- Sub-GHz: Removed Weather Station, POCSAG and TPMS protocols from main app, now found in external apps (by @WillyJL)
  - Momentum previously supported these external app's protocols in the main Sub-GHz app
  - However, with more protocols added over time to the main app, they are now too many
  - The Flipper CPU cannot keep up with all the data received with this number of protocols
  - This caused some signals to not be received when they should, and in some cases could freeze the device
  - Since Weather Station, POCSAG and TPMS are available as external apps, they're now removed from the main Sub-GHz app
  - You can now find this functionality in `Apps > Sub-GHz`, where there are dedicated apps for these 3 functions

### Added:
- Apps:
  - Sub-GHz: Sub-GHz Playlist Creator (by @coolerUA)
  - Sub-GHz: Weather Station (by @Skorpionm)
  - Sub-GHz: POCSAG Pager (by @xMasterX)
  - Sub-GHz: TPMS Reader (by @wosk)
- NFC: Ventra ULEV1 parser (by @hazardousvoltage)
- Infrared: "Decode only" mode to ignore RAW signals, make buttons in learn scene more intuitive (by @WillyJL)
- UL: Sub-GHz: Add keeloq ironlogic aka il100 smart clone cloners support (by @xMasterX & Vitaly)
- UL: iButton: Add TM01x Dallas write support (by @Leptopt1los)
- UL: Display: Backlight option "Always ON" (by @Dmitry422)

### Updated:
- Apps:
  - Authenticator: New options to have space between groups of digits (by @akopachov)
  - Blackhat: Fix Run Script command (by @o7-machinehum), fix NULL ptr scrolling menu suboptions, more wlan selectors and stop options (by @WillyJL)
  - Camera Suite: Handle 128x128 image, fix image rotation bug (by @rnadyrshin)
  - Combo Cracker: Many usability improvements (by @CharlesTheGreat77)
  - ESP Flasher: Bump Marauder 1.7.0 (by @justcallmekoko), FlipperHTTP 2.0 (by @jblanked)
  - Flame RNG: New App Icon (by @Kuronons), Improved the RNG using the hardware RNG and some bit mixing (by @OrionW06)
  - FlipDownloader: Add Picoware (by @jblanked)
  - FlipWiFi: Added Deauthentication mode (by @jblanked)
  - Passy: Capitalize document number (by @bettse)
  - Picopass: Bugfixes and refactoring (by @bettse)
  - Portal Of Flipper: Implement auth for the xbox 360 (by @sanjay900)
  - Quac: Fix link imports not working, fix RAW Sub-GHz files (by @xMasterX & @WillyJL), add Sub-GHz duration setting (by @rdefeo)
  - Metroflip: Added 80+ card AIDs, more AIDs for DESFire, Calypso card saving, fixed DESFire parsing, Navigo crash, Clipper timestamp (by @luu176)
  - Seos Compatible: Add support for reading Seader files that have SIO, Add custom zero key ADF OID (by @bettse)
  - WiFi Marauder: Support for new commands from ESP32Marauder 1.6.x (by @justcallmekoko)
  - VGM Tool: Fixed RGB firmware UART regression (by @WillyJL)
  - UL: Sub-GHz Playlist: Add support for custom modulation presets, remake with txrx library and support for dynamic signals, cleanup code (by @xMasterX)
- RFID: Add DEZ10 representation to EM410X (by @realcatgirly)
- Furi: Re-enabled file paths in furi_check crash messages (by @WillyJL)
- OFW: Infrared: Add text scroll to remote buttons (by @956MB)
- Sub-GHz:
  - UL: Rename and extend Alarms ignore option with Hollarm & GangQi (by @xMasterX)
  - UL: Add 462.750 MHz to default subghz freqs list (by @xMasterX)
  - UL: V2 Phoenix show counter value (by @xMasterX)

### Fixed:
- CLI:
  - Fix crash when opening CLI/qFlipper/WebUpdater if some unexpected files are present in `/ext/apps_data/cli/plugins` (by @WillyJL)
  - Fix crash with `ir universal` command (by @WillyJL)
  - Fix crash with `date` command (by @WillyJL)
  - Fix temporary `nfc apdu` command (by @WillyJL)
  - OFW: Fix subghz chat command (by @GameLord2011)
- NFC:
  - Fix card info not being parsed when using Extra Actions > Read Specific Card Type (by @WillyJL)
  - UL: Fix clipper date timestamp (by @luu176)
- BadKB: Fix key combos main keys being case sensitive (by @WillyJL)
- Sub-GHz:
  - Fix frequency analyzer deadlock when holding Ok (by @WillyJL)
  - UL: Fix CAME 24bit decoder (by @xMasterX)
  - UL: Tune holtek ht12x to decode holtek only and not conflict with came 12bit (by @xMasterX)
  - UL: Fix Rename scene bug, that was replacing file name with random name when Rename is opened then closed then opened again (by @xMasterX)

### Removed:
- Sub-GHz: Removed Weather Station, POCSAG and TPMS protocols from main app, now found in external apps (by @WillyJL)
  - See breaking changes notice above

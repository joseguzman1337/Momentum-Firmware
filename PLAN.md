## Momentum Firmware Flash Plan

1. **Restore RFC headers & helpers** – align `lib/nfc/protocols/nfcv.h` and `slix.*` helpers with the definitions expected by `nfcv.c` (FuriHAL structures, ReturnCode, signal helpers, RFAL functions) and ensure the source includes correct public headers instead of reimplementing types.
2. **Align signal/timing support** – revisit the signal allocation logic (avoid custom digital signal structs), ensure `digital_signal` utilities are used correctly, and reintroduce RFAL/ ST25R3916 helper availability (like `rfal_platform_spi_*`, `st25r3916ExecuteCommand`, `st25r3916WriteRegister`) through proper includes or wrappers.
3. **Fix build context** – remove temporary stub files if redundant, confirm `sync_momentum_to_upstream.py` does not override upstream system files unexpectedly, then rerun `./fbt flash_usb_full` and capture `/tmp/flipper_flash.log` output for any remaining errors.
4. **Document next steps** – when the build completes or a blocker is reached, update this plan/file with the new status and outstanding follow-ups so the next session picks up cleanly.

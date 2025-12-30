# Custom Fonts (Asset Packs)

This guide explains how to add custom fonts to a Momentum Asset Pack.

## Supported font slots

Asset packs can override up to five UI fonts. Use these exact filenames in your pack:

- `Primary.u8f`
- `Secondary.u8f`
- `Keyboard.u8f`
- `BigNumbers.u8f`
- `BatteryPercent.u8f`

Only the files you provide are overridden; missing ones fall back to the defaults.

## Create a u8g2 font

Momentum uses u8g2 font data. You can:

- Start from an existing u8g2 font `.c` file (like the ones in `assets/packs/WatchDogs/Fonts`).
- Generate a u8g2 font using `bdfconv` from the u8g2 project.

The `.c` file must include a `const uint8_t` font array with `U8G2_FONT_SECTION(...)`.

## Pack the font

Place your `.c` or `.u8f` files in the `Fonts` folder of your asset pack, then run the packer:

```text
MyPack/
  Fonts/
    Primary.c
    Secondary.c
```

```bash
python scripts/mntm-asset-packer.py pack ./MyPack
```

The packer writes compiled fonts to `./asset_packs/MyPack/Fonts/*.u8f`.

## Install and use

1. Copy the packed folder to your SD card: `SD/asset_packs/MyPack`.
2. On the device, go to Momentum Settings -> Interface -> Graphics -> Asset Pack and select your pack.

## Notes

- Large fonts increase RAM usage; Momentum may show a size warning when you select a pack with big Fonts or Icons.
- If you only want to override one font, include just that file (for example `Primary.u8f`).

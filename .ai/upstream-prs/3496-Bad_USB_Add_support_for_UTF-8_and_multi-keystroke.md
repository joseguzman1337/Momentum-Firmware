# PR #3496: Bad USB: Add support for UTF-8 and multi-keystroke characters

## Metadata
- **Author:** @vanguacamolie (Guacamolie)
- **Created:** 2024-03-04
- **Status:** Open
- **Source Branch:** `bad-usb-keyboard-layout`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3496

## Labels
`USB`, `Applications`

## Description
# What's new

This PR adds support for new keyboard layouts that couldn’t be supported before. Currently, Bad USB is unable to type the following characters on most Dutch keyboards: `` ` ~ ^ ' " ``. This is because US-International (the de facto keyboard layout used in the Netherlands) requires a space to be pressed after typing any of these characters, otherwise it will attempt to merge the character with the next one.

It tries to solve this by creating a new version of the `.kl` format, one that removes the following limitations:
- Only being able to use ASCII characters
- Only being able map characters to a single key + modifiers

By solving it in this generic way, we hit two birds with one stone and also allow non-ASCII characters to be entered using the standard `STRING` command.

The only limitation that still remains is that characters have to be composed of a single Unicode codepoint. For example, while this make it possible for a keyboard layout to support é when encoded as U+00E9 LATIN SMALL LETTER E WITH ACUTE, it will not be possible to support é when encoded as U+0065 LATIN SMALL LETTER E + U+0301 COMBINING ACUTE ACCENT. The latter form seems to be much less common, however, so I don't expect this to be a big issue.

The new file format is implemented in a fully backwards compatible way, allowing users to keep using existing .kl files they may have added.

The documentation of the new file format can be found in `documentation/file_formats/BadUsbKeyboardFormat.md`. This commit also adds the keyboard layout `en-US-intl.kl`, which implements the US-International keyboard layout.

Before:

https://github.com/flipperdevices/flipperzero-firmware/assets/140027638/ab59b644-5457-4a3c-940b-bf478540822c

After:

https://github.com/flipperdevices/flipperzero-firmware/assets/140027638/c7433ceb-d39a-4b17-9cb6-a8fe7a9849e2


# Verification 

One may use the following Bad USB script to verify that every key in `en-US-intl.kl` types correctly. One needs to configure their keyboard layout to US-International for this. On Linux, this is called English (US, intl., with dead keys).

```
STRING cat > /dev/null <<"EOF"
ENTER
STRING ~  !¹ @  #  $£ %  ^  &  *  (  )  _  +÷
ENTER
STRING `  1¡ 2² 3³ 4¤ 5€ 6¼ 7½ 8¾ 9‘ 0’ -¥ =×
ENTER
ENTER
STRING     QÄ WÅ EÉ R  TÞ YÜ UÚ IÍ OÓ PÖ {  }  |¦
ENTER
STRING     qä wå eé r® tþ yü uú ií oó pö [« ]» \¬
ENTER
ENTER
STRING      AÁ S§ DÐ F  G  H  J  K  LØ :° "
ENTER
STRING      aá sß dð f  g  h  j  k  lø l¶ '
ENTER
ENTER
STRING       ZÆ X  C¢ V  B  NÑ M  <Ç >  ?
ENTER
STRING       zæ x  c© v  b  nñ mµ ,ç .  /¿
ENTER
STRING EOF
ENTER
```

One should also verify that the default keyboard layout and the v1 keyboard layouts still work. One may also try to corrupt the v2 keyboard layout (easiest way is to remove a byte from the end), and verify that it falls back to the default keyboard layout.

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix

---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*

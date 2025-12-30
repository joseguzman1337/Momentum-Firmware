# Issue #3910: `mbedtls.cfg.h` is not accessible when using local SDKs via uFBT

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3910](https://github.com/flipperdevices/flipperzero-firmware/issues/3910)
**Author:** @CookiePLMonster
**Created:** 2024-09-18T18:35:01Z
**Labels:** Bug, Build System & Scripts

## Description

### Describe the bug.

Attempting to use a self-built SDK with uFBT via `ufbt update --local=X` seems to be unable to detect `mbedtls.cfg.h`, even though it is bundled in the `.zip` update package:

```
In file included from H:/dev/flipper-zero/.ufbt/current/sdk_headers/f7_sdk/lib/mbedtls/include/mbedtls/bignum.h:14,
                 from H:\dev\flipper-zero\flipper-bakery\flipper95\flipper95.c:14:
H:/dev/flipper-zero/.ufbt/current/sdk_headers/f7_sdk/lib/mbedtls/include/mbedtls/build_info.h:79:10: error: #include expects "FILENAME" or <FILENAME>
   79 | #include MBEDTLS_CONFIG_FILE
      |          ^~~~~~~~~~~~~~~~~~~
```

Am I maybe missing a step in my local SDK builds and I need more than just `./fbt updater_package`?

### Reproduction

I'll outline the steps using my own app, but it's unlikely to be isolated to just that.

1. Have a local debug SDK build done from FBT, in my case build with `./fbt updater_package`.
2. Switch uFBT to use this local SDK - `ufbt update --local=h:\dev\flipper-zero\flipperzero-firmware\dist\f7-D\flipper-z-f7-sdk-local.zip --hw-target=f7`
3. Clone [Flipper95](https://github.com/CookiePLMonster/flipper-bakery/tree/flipper-alarm/flipper95) and set up `ufbt vscode_dist` on it.
4. Attempt to build the app with `ufbt`.
5. Observe a `sdk_headers/f7_sdk/lib/mbedtls/include/mbedtls/build_info.h:79:10: error: #include expects "FILENAME" or <FILENAME>` error.
6. Switch uFBT to the latest dev or release track via `ufbt update --channel=release/dev`.
7. Attempt to build the app again.
8. Observe the errror **does not occur**.

### Target

f7 with latest dev release

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

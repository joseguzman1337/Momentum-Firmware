# Issue #3913: Consider enabling C++23 and C23

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3913](https://github.com/flipperdevices/flipperzero-firmware/issues/3913)
**Author:** @CookiePLMonster
**Created:** 2024-09-20T10:42:53Z
**Labels:** Feature Request, Build System & Scripts

## Description

### Describe the enhancement you're suggesting.

Currently, the C and C++ standard seems to be defined as follows:
* FBT - `-std=gnu2x` for C, `-std=c++20` for C++
* uFBT - nothing? for C, `-std=c++20` for C++
* vscode config - `gnu23` for C, `c++20` for C++

Since GCC has partial support for C++23 since GCC11, please consider the following:
1. Enable `gnu23` for C in FBT and uFBT, or `gnu2x` if GCC 12 doesn't support `gnu23` yet.
2. Enable `gnu++2b` for C++ in FBT and uFBT. This gives us access to most C++23 features with GNU extensions. Or, if you don't want the GNU extensions, `c++2b` will do too.
3. Enable `gnu++23` in the vscode config, or `c++23` if you don't want the GNU extensions.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

# Issue #4262: Error while building firmware

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4262](https://github.com/flipperdevices/flipperzero-firmware/issues/4262)
**Author:** @Rel0s
**Created:** 2025-08-13T14:34:22Z
**Labels:** Triage

## Description

Hi all,

I am trying to build an updater package using fbt, and it results to the following error:

  File "C:\Users\PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\flipper\assets\coprobin.py", line 117, in __init__
    raise CoproException(f"Invalid FUS img magic {self.magic:x}")
flipper.assets.coprobin.CoproException: Invalid FUS img magic a0d6f4e
scons: *** [dist_updater_package] Error 1

********** FBT ERRORS **********
dist_updater_package: Error 1

Steps that I took: 
1. Install latest Git version.
2. Updated qflipper windows app
3. run git clone --recursive
4.  run cmd as admin and running fbt COMPACT=1 DEBUG=0 updater_package
5. The error appears

In addition there is no errors with just running fbt command in the root folder.

I have also tried the fbtenv in the scripts folder (same result).

Full output:

        DIST    dist_updater_package
2025-08-13 17:26:59,657 [INFO] Firmware binaries can be found at:
        dist\f7-C
Traceback (most recent call last):
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\sconsdist.py", line 283, in <module>
    Main()()
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\flipper\app.py", line 41, in __call__
    return_code = self.call()
                  ^^^^^^^^^^^
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\flipper\app.py", line 57, in call
    return self.args.func()
           ^^^^^^^^^^^^^^^^
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\sconsdist.py", line 145, in copy
    if bundle_result := self.bundle_update_package():
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\sconsdist.py", line 254, in bundle_update_package
    if (bundle_result := UpdateMain(no_exit=True)(bundle_args)) == 0:
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\flipper\app.py", line 41, in __call__
    return_code = self.call()
                  ^^^^^^^^^^^
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\flipper\app.py", line 57, in call
    return self.args.func()
           ^^^^^^^^^^^^^^^^
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\update.py", line 107, in generate
    radio_meta = CoproBinary(self.args.radiobin)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\flipper\assets\coprobin.py", line 136, in __init__
    self._load()
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\flipper\assets\coprobin.py", line 144, in _load
    self.img_sig_footer = CoproSigFooter(img_sig_footer_bin)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware\scripts\flipper\assets\coprobin.py", line 117, in __init__
    raise CoproException(f"Invalid FUS img magic {self.magic:x}")
flipper.assets.coprobin.CoproException: Invalid FUS img magic a0d6f4e
scons: *** [dist_updater_package] Error 1

********** FBT ERRORS **********
dist_updater_package: Error 1

(fbt) C:\Users\Home PC\Desktop\flipper_OFW\flipperzero-firmware>





---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

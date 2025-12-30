# Issue #2053: Allow loader open to start streaming logs

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2053](https://github.com/flipperdevices/flipperzero-firmware/issues/2053)
**Author:** @NZSmartie
**Created:** 2022-11-26T00:02:32Z
**Labels:** Feature Request, Build System & Scripts

## Description

### Describe the enhancement you're suggesting.

As a Flipper Application Developer, I would like to see application logs when deploying and running the fap through FBT.

What I would expect to see when running `./fbt launch_app APPSRC=applications_user\my_app`
```
        SDKCHK  firmware\targets\f7\api_symbols.csv
API version 7.5 is up to date
python "./scripts/runfap.py" "build\f7-firmware-D\.extapps\my_app.fap" --fap_dst_dir "/ext/apps/"
        APPCHK  build\f7-firmware-D\.extapps\my_app.fap
2022-11-26 12:14:16,644 [INFO] Using FLIP_GLEXVD on COM10
2022-11-26 12:14:16,694 [INFO] Installing "build\f7-firmware-D\.extapps\my_app.fap" to /ext/apps/my_app.fap
2454608 [I][fap_loader_app] FAP Loader is loading /any/apps/my_app.fap
2454613 [I][AnimationManager] Unload animation 'L1_Waves_128x50'
2454632 [I][fap_loader_app] FAP Loader is mapping
2454637 [I][elf] Total size of loaded sections: 118
2454639 [I][fap_loader_app] Loaded in 31ms
2454642 [I][fap_loader_app] FAP Loader is starting app
2454645 [I][my_app] Hello, may I have some phish?
2454648 [I][my_app] Please and Thank you~
2454656 [I][fap_loader_app] FAP app returned: 0
2454673 [I][LoaderSrv] Application stopped. Free heap: 135080
```

Instead, I only see the log output from `runfap.py` and none of the logs from the Flipper itself without needing to open a separate terminal and invoking `logs`

### Anything else?

It may be beneficial to allow specifying a log filter for known application tags to reduce the noise from other parts of the system

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

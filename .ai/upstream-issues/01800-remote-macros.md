# Issue #1800: Remote Macros

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/1800](https://github.com/flipperdevices/flipperzero-firmware/issues/1800)
**Author:** @uintdev
**Created:** 2022-09-28T17:20:53Z
**Labels:** Feature Request, Backlog, Infrared

## Description

### Description of the feature you're suggesting.

The IR remote application is a great bit of functionally that makes it possible to control multiple devices from a single Flipper.
As useful as it is, situations when using the physical navigation keys to change the button selection and then performing button combinations manually can make it time consuming to use. For example, changing TV channel to one that has multiple numbers in the channel number or trying to navigate an interface with exact key combinations (i.e. menus). If they’re common key presses, why not reduce the friction?

My idea is remote macros. The process I have in mind is as follows:
- User creates a remote/button as usual
- While in the `learn new remote` section, offer the option to create a macro (menu or present option on the bottom corner)
- Listen to all captured data as it comes through, adding delays in between (relative to how long a user waits between key presses — taking out any from before the first and after the last key press in the recording session)
- Press a key on the Flipper to lock in the capture and save the macro (if a preview is included, perhaps the amount of key presses could be shown at least)
- Macro gets assigned to a button for the remote
- When pressing a macro button, show the same sort of cancellable progress dialog as the universal remote as to show progress of the macro runtime

Ideally, users should be able to manually edit the remote file as usual but be able to adjust delays if needs be (i.e. loading times on the device being controlled may not be consistent).

As implied by the process steps I had detailed, the idea would be that this would use existing functionality as to make things more convenient for the end user and potentially development work.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

# Issue #4200: Enhance SubGhz with protocol command cycling

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4200](https://github.com/flipperdevices/flipperzero-firmware/issues/4200)
**Author:** @Nvidiacerv
**Created:** 2025-04-21T07:52:08Z
**Labels:** Feature Request, Sub-GHz

## Description

** may 5 update, i made an enhanced subghz app and got this feature to work. At this moment it is working for only the intertechno_v3 protocol but looking to expand it to support more protocols soon. I saved this enhancement in a private repository for the flipper team to look at. Contact me for access. I wanna contribute to the flipper zero firmware but unexperienced with github.

**1. Goal:** Enhance the SubGHz signal emulation functionality to allow users to transmit different commands associated with a specific device/protocol, beyond simply replaying the exact command that was originally captured and saved.
**2. Current Limitation:** Currently, if a user captures and saves, for example, the "Close" command for a Dooya blind remote, the "Send" function can only re-transmit that exact "Close" command. To send "Open" or "Stop", the user must capture and save those specific signals separately or edit the sub file manually for instance using an editor on a pc.
**3. Desired Enhancement:** When a user selects a saved SubGHz key for emulation (sending), the system should:
       • Identify Supported Commands: Determine if the protocol associated with the saved key supports multiple distinct commands (e.g., On/Off, Open/Close/Stop).
       • Present Options (If Applicable): If multiple commands are supported, present the user with a choice of available commands for that protocol before transmission. This list should use human-readable names. The user should be able to select another command for instance by using the up or down button on the flipper zero while in the emulation screen.
       • Generate Selected Command: Upon user selection of a command (which might be the original command or a different one from the list), the system must generate the correct SubGHz signal payload corresponding to the selected command when send is pressed.
       • Reuse Identification Data: Crucially, the newly generated signal must utilize the essential identification parameters (like Device ID, Remote Address, Channel, Key, Counter - depending on the protocol) from the original saved key. This ensures the command is sent as if from the original remote and targets the correct receiving device.
**4. Examples for the Dooya and Intertechno_V3 protocols. But should be workign with all known commands with multiple commands:**
       • Dooya Protocol (Blinds/Curtains):
           ◦ User saves a key captured from the "Close" button.
           ◦ User selects this key and chooses "Send".
           ◦ The system recognizes it's Dooya and presents options: "Open", "Close", "Stop".
           ◦ User selects "Open".
           ◦ The system generates the "Open" command signal, using the Device ID and other necessary data from the saved "Close" key, and transmits it.
       • Intertechno V3 Protocol (Power Outlets):
           ◦ User saves a key captured from the "On" button for a specific outlet address.
           ◦ User selects this key and chooses "Send".
           ◦ The system recognizes it's Intertechno V3 and presents options: "On", "Off".
           ◦ User selects "Off".
           ◦ The system generates the "Off" command signal, using the address/ID from the saved "On" key, and transmits it.
**5. Benefit:** This feature allows users to fully control devices supporting multiple commands using only a single saved key for that device, significantly improving usability and reducing the need to capture every possible command variation. It transforms the Flipper from a simple repeater into a more versatile remote control for supported protocols.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

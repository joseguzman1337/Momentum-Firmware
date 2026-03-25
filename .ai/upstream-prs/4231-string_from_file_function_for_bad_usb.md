# PR #4231: string from file function for bad usb

## Metadata
- **Author:** @p4p1 (Leo Smith)
- **Created:** 2025-05-14
- **Status:** Open
- **Source Branch:** `badusb_file_to_string`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4231

## Labels
`USB`, `New Feature`

## Description
# What's new
A badusb function to take the content of a file and print it.

![image](https://github.com/user-attachments/assets/0796ad80-7d57-47f8-9726-d3f9b5978973)

1. notepad to test badusb script
2. the badusb script
3. content of `/ext/abc.txt`

# Verification 
Here is a sample script to test the function:
```
STRING_FROM_FILE /ext/abc.txt
```
make sure to place a file named `abc.txt` at the root of an sdcard with text inside of it.
# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*

# Issue #4162: Connecting as USB HID keyboard cannot read state of keyboard LEDs (CapsLock/NumLock/ScrollLock)

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4162](https://github.com/flipperdevices/flipperzero-firmware/issues/4162)
**Author:** @maxplank
**Created:** 2025-03-26T18:07:07Z
**Labels:** USB, Triage

## Description

### Describe the bug.

I'm developing an application that uses Flipper to connect to a computer and represent itself as USB keyboard (something similar to BadUSB).

I'm able to establish connection using `furi_hal_usb_set_config()` and simulate key presses using `furi_hal_hid_kb_press()`.

The problem is that it seems the method `furi_hal_hid_get_led_state()` is not working and always returns 0 no matter what the keyboard LEDs are blinking and no matter Caps/Num/Scroll Lock is toggled from the keyboard or by Flipper (actually I can simulate CapsLock press from Flipper and the physical keyboard toggles CapsLock LED).

I dug deep into the firmware source code and I think I spotted where the problem comes from.
Unfortunately I see no way it to be resolved from the external .fap application and it indeed needs fix in the firmware itself.

So here is what I found:
In "targets/f7/furi_hal/furi_hal_usb_hid.c":
- `furi_hal_hid_get_led_state()` just returns led_state variable which is set in `hid_txrx_ep_callback()`
- this one is registered as endpoint in `hid_ep_config()` with this line:
	`usbd_reg_endpoint(dev, HID_EP_IN, hid_txrx_ep_callback);`

I think the problem is that it is registered as HID_EP_IN only, which means one-way input only communication (device to host). There is no OUT endpoint registered (host to device) that would allow sending the LEDs state.

For comparison there is something very similar in "targets/f7/furi_hal/furi_hal_usb_u2f.c" where there is additional line:
	`usbd_reg_endpoint(dev, HID_EP_OUT, hid_u2f_txrx_ep_callback);`
and this allows 2-way input/output communication.

I believe that adding the relevant lines for HID_EP_OUT in "furi_hal_usb_hid.c" would fix the problem and allow the USB HID device to have full input/output communication.

### Reproduction

1. Create new Flipper Zero app.
2. Connect as USB HID keyboard using:
	`furi_hal_usb_set_config(...);`
3. Simulate keypresses of CapsLock key (try several times):
      ```
      usb_keyboard_press(HID_KEY_CAPS_LOCK);
      furi_delay_ms(50);
      usb_keyboard_release(HID_KEY_CAPS_LOCK);
4. Press CapsLock on the physical keyboard. Try several times.
5. (Optional) Connect second physical keyboard and make sure CapsLock LED on both is synchronized.
6. Call `furi_hal_hid_get_led_state()` and print its result.

Expected:
`furi_hal_hid_get_led_state()` returns value corresponding to keyboards' LEDs state.

Actual result:
`furi_hal_hid_get_led_state()` always returns 0

### Target

Source code: flipperzero-firmware dev branch, latest version (till this date)
Flipper Zero device: Momentum mntm-009 [23-01-2025] (latest stable till this date)

_No response_

### Logs

```Text

```

### Anything else?

Please provide a fix for this issue!
The application I'm developing is exactly in the spirit of Flipper, but it is pointless without the ability to read keyboard LEDs, so I'm heavily relying on it. If everything goes smooth I hope to publish it, so it becomes a useful part of the Flipper toolkit.


---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

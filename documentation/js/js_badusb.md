# BadUSB module {#js_badusb}

```js
let badusb = require("badusb");
```
# Methods
## setup()
Start USB HID with optional parameters. Should be called before all other methods.
Automatically unlocks USB profile, so qFlipper connection will be interrupted.

**Parameters**

Configuration object *(optional)*:
- vid, pid (number): VID and PID values, both are mandatory
- mfrName (string): Manufacturer name (32  ASCII characters max), optional
- prodName (string): Product name (32  ASCII characters max), optional
- layoutPath (string): Path to keyboard layout file, optional

**Examples**
```js
// Start USB HID with default parameters
badusb.setup();
// Start USB HID with custom vid:pid = AAAA:BBBB, manufacturer and product strings not defined
badusb.setup({ vid: 0xAAAA, pid: 0xBBBB }); 
// Start USB HID with custom vid:pid = AAAA:BBBB, manufacturer string = "Flipper Devices", product string = "Flipper Zero"
badusb.setup({ vid: 0xAAAA, pid: 0xBBBB, mfrName: "Flipper Devices", prodName: "Flipper Zero" });
```

<br>

## setupBle()
Start Bluetooth LE HID with optional parameters. Should be called before all other methods.

**Parameters**

Configuration object *(optional)*:
- name (string): BLE device name, optional
- mac (string | Uint8Array): BLE MAC address (AA:BB:CC:DD:EE:FF), optional
- bonding (boolean): Persist pairing keys, optional (default: true)
- pairing (number | string): Pairing mode, optional (0 = YesNo, 1 = PinType, 2 = PinYesNo)
- layoutPath (string): Path to keyboard layout file, optional

**Examples**
```js
// Start BLE HID with default parameters
badusb.setupBle();
// Start BLE HID with custom name and MAC address
badusb.setupBle({ name: "BadKB JS", mac: "AA:BB:CC:DD:EE:FF" });
// Start BLE HID with custom pairing mode and layout
badusb.setupBle({ pairing: "PinYesNo", layoutPath: "/ext/badusb/assets/layouts/en-US.kl" });
```

<br>

## isConnected()
Returns connection state for the active interface (USB or BLE).

**Example**
```js
if (badusb.isConnected()) {
    // Do something
} else {
    // Show an error
}
```

<br>

## getLockState()
Returns the current state of keyboard lock LEDs (Caps Lock, Num Lock, Scroll Lock).
BLE HID does not report lock LEDs, so values may be false when using `setupBle()`.

**Return value**

An object with boolean fields:
- `caps` – Caps Lock LED state
- `num` – Num Lock LED state
- `scroll` – Scroll Lock LED state

**Examples**
```js
let locks = badusb.getLockState();
if (locks.caps) {
    // CAPSLOCK LED is on
}
if (!locks.num) {
    // Enable Num Lock before doing ALT+Numpad tricks
}
```

<br>

## press()
Press and release a key.

**Parameters**

Key or modifier name, key code.

See a [list of key names below](#js_badusb_keynames).

**Examples**
```js
badusb.press("a"); // Press "a" key
badusb.press("A"); // SHIFT + "a"
badusb.press("CTRL", "a"); // CTRL + "a"
badusb.press("CTRL", "SHIFT", "ESC"); // CTRL + SHIFT + ESC combo
badusb.press(98); // Press key with HID code (dec) 98 (Numpad 0 / Insert)
badusb.press(0x47); // Press key with HID code (hex) 0x47 (Scroll lock)
```

<br>

## hold()
Hold a key. Up to 5 keys (excluding modifiers) can be held simultaneously.

**Parameters**

Same as `press`.

**Examples**
```js
badusb.hold("a"); // Press and hold "a" key
badusb.hold("CTRL", "v"); // Press and hold CTRL + "v" combo
```

<br>

## release()
Release a previously held key.

**Parameters**

Same as `press`.

Release all keys if called without parameters.

**Examples**
```js
badusb.release(); // Release all keys
badusb.release("a"); // Release "a" key
```

<br>

## print()
Print a string.

**Parameters**

- A string to print
- *(optional)* Delay between key presses

**Examples**
```js
badusb.print("Hello, world!"); // print "Hello, world!"
badusb.print("Hello, world!", 100); // Add 100ms delay between key presses
```
<br>

## println()
Same as `print` but ended with "ENTER" press.

**Parameters**

- A string to print
- *(optional)* Delay between key presses

**Examples**
```js
badusb.println("Hello, world!");  // print "Hello, world!" and press "ENTER"
```
<br>

## altPrint()
Prints a string by Alt+Numpad method - works only on Windows!

**Parameters**

- A string to print
- *(optional)* delay between key presses

**Examples**
```js
badusb.altPrint("Hello, world!"); // print "Hello, world!"
badusb.altPrint("Hello, world!", 100); // Add 100ms delay between key presses
```
<br>

## altPrintln()
Same as `altPrint` but ended with "ENTER" press.

**Parameters**

- A string to print
- *(optional)* delay between key presses

**Examples**
```js
badusb.altPrintln("Hello, world!");  // print "Hello, world!" and press "ENTER"
```
<br>

## quit()
Releases usb, optional, but allows to interchange with usbdisk.

**Examples**
```js
badusb.quit();
usbdisk.start(...)
```
<br>

# Key names list {#js_badusb_keynames}

## Modifier keys

| Name          |
| ------------- |
| CTRL          |
| SHIFT         |
| ALT           |
| GUI           |

## Special keys

| Name               | Notes            |
| ------------------ | ---------------- |
| DOWN               | Down arrow       |
| LEFT               | Left arrow       |
| RIGHT              | Right arrow      |
| UP                 | Up arrow         |
| ENTER              |                  |
| DELETE             |                  |
| BACKSPACE          |                  |
| END                |                  |
| HOME               |                  |
| ESC                |                  |
| INSERT             |                  |
| PAGEUP             |                  |
| PAGEDOWN           |                  |
| CAPSLOCK           |                  |
| NUMLOCK            |                  |
| SCROLLLOCK         |                  |
| PRINTSCREEN        |                  |
| PAUSE              | Pause/Break key  |
| SPACE              |                  |
| TAB                |                  |
| MENU               | Context menu key |
| Fx                 | F1-F24 keys      |
| NUMx               | NUM0-NUM9 keys   |

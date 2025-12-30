# Issue #3677: A JavaScript module for handling a button press

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3677](https://github.com/flipperdevices/flipperzero-firmware/issues/3677)
**Author:** @tlhunter
**Created:** 2024-05-31T03:55:23Z
**Labels:** Feature Request, JS

## Description

### Description of the feature you're suggesting.

I would like to request an API for receiving a single button press. This could be very similar to the existing dialogue API except that it wouldn't clear the screen or display any messages. The developer would be expected to draw to the screen ahead of time.

The API could be very basic:

```js
let buttons = require("buttons");
let result = buttons.waitForButtonPress();
// result in "up", "down", "left", "right", "ok"
```

Ideally the back button could be caught as well but I understand that it is currently the only way to consistently exit a program and probably shouldn't be caught.

Ideally, assuming the code runs inside of a loop, if the user were to hold down a button continuously then it would just work as expected, triggering the button press with each iteration.

```js
let buttons = require("buttons");
while(true) {
let result = buttons.waitForButtonPress();
// result is read with each iteration even if button remains held
// of course, there is no guaranteed timing...
}
```

### Anything else?

I believe this would unlock a lot of potential games.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

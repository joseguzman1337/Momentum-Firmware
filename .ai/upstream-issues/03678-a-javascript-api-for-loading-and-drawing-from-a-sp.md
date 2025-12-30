# Issue #3678: a JavaScript API for loading and drawing from a spritesheet

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3678](https://github.com/flipperdevices/flipperzero-firmware/issues/3678)
**Author:** @tlhunter
**Created:** 2024-05-31T04:10:50Z
**Labels:** Feature Request, JS

## Description

### Description of the feature you're suggesting.

I would like to request a JavaScript API for opening a bitmap format representing graphics and for drawing them to the screen. This is a powerful and efficient pattern for drawing graphics. 

Basically each sprite in a spritesheet is perhaps 8x8 pixels while the overall sheet is perhaps 64x64 pixels. Then one programmatically chooses one of the sprites in the sheet and provides a coordinate to draw the sprite at.

The API could look like this: 
```js
let sprites = require('spritesheet');
let sheet = sprites.load('mysheet.bmp', 8, 8); // w, h
sprites.drawToScreen(sheet, 3, 8, 16);
```
This draws the fourth entry (index 3 when 0 based) in the spritesheet to pixel coordinate x=8, y=16. The drawn entry is 8x8 pixels.

I used bmp as an example but it could be gif or pcx or whatever format Flipper already uses.

### Anything else?

This would allow for interesting game development.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

# Issue #4272: При попытке подключить модуль "flipper" в js-скрипте ошибка

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4272](https://github.com/flipperdevices/flipperzero-firmware/issues/4272)
**Author:** @arduinotech
**Created:** 2025-09-09T21:51:38Z
**Labels:** None

## Description

### Describe the bug.

Пришу js-скрипт используя SDK (ts-файл).

```typescript
import * as flipper from "@flipperdevices/fz-sdk/flipper";
print(flipper.getName())
``` 

Получаю ошибку:
---- ERROR ----
"flipper" module load fail
Trace:
        at /ext/apps/Scripts/multitool_flipper_zero_js.js:7

Файл после конвертирование из ts в js:
```javascript
checkSdkCompatibility(0, 1);
let exports = {};
"use strict";

// dist/index.js
Object.defineProperty(exports, "__esModule", { value: true });
var flipper = require("@flipperdevices/fz-sdk/flipper");
print(flipper.getName());
``` 

Остальные модули импортируются и все работает корректно.
Что может быть не так?

### Reproduction

1. Импортирую модуль "flipper"
2. Запускаю скрипт через npm start
3. Получаю ошибку

### Target

_No response_

### Logs

```Text

```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

# Issue #4248: Inconsistent file path syntax in CLI

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4248](https://github.com/flipperdevices/flipperzero-firmware/issues/4248)
**Author:** @Stichoza
**Created:** 2025-07-11T14:59:11Z
**Labels:** Backlog, Bug, Core+Services

## Description

CLI commands that have spaces in filename are handled inconsistently throughout Flipper CLI.

Examples:

#### `storage read` – Normal behavior
- `storage read /ext/subghz/Some File.sub` – Does not work.
- `storage read "/ext/subghz/Some File.sub"` – Works with path in quotes.

#### `loader open` – Opposite behavior of normal
- `loader open subghz /ext/subghz/Some File.sub` – Works even without quotes.
- `loader open subghz "/ext/subghz/Some File.sub"` – Fails with quotes.

#### `subghz tx_from_file` – Not working at all
- `subghz tx_from_file /ext/subghz/Some File.sub` – No quotes – not working
- `subghz tx_from_file /ext/subghz/Some\ File.sub` – Escaped space – not working
- `subghz tx_from_file "/ext/subghz/Some File.sub"` – Double quotes – not working
- `subghz tx_from_file '/ext/subghz/Some File.sub'` – Single quotes – not working

Inconsistency between `storage read` and `loader open` is not a big deal, but I'm unable to make `subghz tx_from_file` work.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

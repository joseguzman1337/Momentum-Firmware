# Issue #1234: Two-dimensional layout for saved remotes

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/1234](https://github.com/flipperdevices/flipperzero-firmware/issues/1234)
**Author:** @lykahb
**Created:** 2022-05-15T18:43:47Z
**Labels:** Feature Request, Infrared, UI

## Description

**Is your feature request related to a problem? Please describe.**
The buttons on a saved remote are displayed as a list. It may take long time to scroll to the needed button.

**Describe the solution you'd like**
The universal library for TV has a scene with a two-dimensional layout. A saved remote would display a similar layout for the names that it recognizes, and puts the rest in a list below. For example, a saved remote has these commands: POWER, VOL+, VOL-, CH+, CH-, NETFLIX, YOUTUBE. Then we display the first commands as icons in a layout, and put the netflix and youtube in a list below, 

**Describe alternatives you've considered**
A simpler grid with two columns that have names and no icons. The items are displayed in the same order as in the .ir file, with no mapping to icon or layout position. The names are truncated to fit half width of the screen.

**Additional context**
Add any other context or screenshots about the feature request here.


---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

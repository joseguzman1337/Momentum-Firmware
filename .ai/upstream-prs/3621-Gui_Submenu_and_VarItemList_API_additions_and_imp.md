# PR #3621: Gui: Submenu and VarItemList API additions and improvements

## Metadata
- **Author:** @WillyJL (WillyJL)
- **Created:** 2024-04-30
- **Status:** Open
- **Source Branch:** `submenu-varitemlist-api`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3621

## Labels
`UI`, `New Feature`, `Core+Services`

## Description
# What's new

General improvements:
- Can have header in Variable Item List
- Can have a vertical Submenu
- Can lock items in Variable Item List and Submenu
- Variable Item List label and value text will scroll if too long
- Variable Item List value arrows shrink if value is < 4 characters
- More freedom and usefulness in Variable Item List API
- Cleaned up some parts of the code and some magic numbers are now defined
- Feature parity between submenu and variable item list, only differences now are that:
  - variable item list item ID is based on index of addition, submenu item ID is based on user-supplied 32bit value
  - variable item list can edit item values, submenu only allows picking one (by design of the widget purpose)
  - variable item list items can be edited after creation, submenu items cannot (by design of the widget purpose)

API additions (no removals, fully backwards compatible):
- `submenu_add_lockable_item()`:
  - based on #2289 which was rejected, CFWs merged it and improved it over time
  - theres a few apps that use it by now
  - example usecase: highlighting that some features are not available in current configuration / state
  - and even more useful in varitemlist version below
- `submenu_set_orientation()`:
  - can have vertical submenu (user's preference for ux)
  - same concept works great in infrared app, could be reused there to make more of the app vertical instead of having to keep switching
- `variable_item_list_get()`:
  - get and allow editing an item after creation
  - example usecase: editing one option changes state of other entries in the list, like if they are locked due to incompatible settings or if they have different labels or values
  - Sub-GHz app is already doing this (though in a very hacky way) [here](https://github.com/flipperdevices/flipperzero-firmware/blob/7414e6d4dff582efb6ad716e8268cad03be65c87/applications/main/subghz/scenes/subghz_scene_receiver_config.c#L175-L204), to change frequency text to `---` when hopping is enabled, by storing the item pointer in scene state, this is also quite error prone, with varitemlist get() it would be safer and clearer
  - for example i have a an app menu that edits an array, you select an index by scrolling on first item, second item removes that index when clicked, third item adds a new item when clicked, this needs to edit the first item to show what index is selected after remove/add
- `variable_item_list_set_header()`:
  - feature parity with `submenu` widget
  - example usecase: headers are pretty but want editable options not just a list
- `variable_item_set_item_label()`:
  - allow changing label after adding item
  - example usecase: want to show index of item, can have value shown and put (1/10) in label dynamically, like in my example above in `get()`
  - more too probably, allows more creativity
- `variable_item_set_locked()`:
  - same as above for `submenu`, based on same code but ported to varitemlist by me
  - also allows setting locked state after the fact, remembers locked message so after creation you can toggle with `set_locked(item, false/true, NULL)`
  - example usecase: some settings combinations in this screen are incompatible, like GPIO pins overlapping when configuring

Acknowlegments:
- Original submenu lockable items code by @giacomoferretti in #2289
- Vertical submenu and some code improvements by Unleashed CFW team
- Most other edits by me @Willy-JL
- Hope I'm not forgetting someone else that was involved

# Verification 

- Check apps that use variable item list and submenu to be working correctly
- No dedicated example app for additional APIs but some apps do use them, for example:

  - Magspoof is using both submenu/varitemlist lockable items and varitemlist get() to dynamically edit a config menu based on allowed combinations of GPIO pins
  - NFC Maker is using locked submenu items when choosing NTAG card type to show if payload is too big for some types
  - XRemote is using submenu vertical orientation in a similar fashion to infrared app
  - FindMy Flipper is using varitemlist header in its tag setup pages
  - BLE Spam is using varitemlist get() to edit which subarray is shown, one option chooses a type and next option chooses allowed values for that type, editing first one needs to update second one
  - An edited version of Mass Storage uses varitemlist header in disk image creation screen which allows setting image name and size
  - Some CFWs show hidden debug options as locked so the user knows they are available but they probably should not use them, keeping them secret could be detrimental to some advanced user who might need them (for example: lfrfid read raw)

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*

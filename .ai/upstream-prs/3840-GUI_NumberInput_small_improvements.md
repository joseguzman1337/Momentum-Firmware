# PR #3840: GUI: NumberInput small improvements

## Metadata
- **Author:** @WillyJL (WillyJL)
- **Created:** 2024-08-14
- **Status:** Open
- **Source Branch:** `number-input-empty-default`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3840

## Labels
`UI`

## Description
# What's new

- I really liked the idea of a number input and already had a use for it, but found a detail that did not fit my use case:
  When showing NumberInput, there is always a number there
  You can set current number to 0, but then if you want to have a minimum value, current number is changed to minimum value, so user gets default text of the minimum value and they need to erase this then input their number
  My use case would work better where you can start typing, and the save button is enabled when the number is within bounds
- This PR allows passing 0 as current number, which will mean the input is empty by default
- Also, manually pressing 0 when input is empty shows the number 0 instead of doing nothing, to avoid confusion
- Also aligned the input bar to keyboard bar, it was probably misaligned due to taking the skeleton of ByteInput, which has arrows on sides of input bar

# Verification 

- Using `example_number_input` app:
  - Set number to zero
  - Click change again, input is empty due to current number being 0
  - Click 0 when input is empty, 0 is displayed
  - Check that input bar is vertically aligned to keyboard buttons

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*

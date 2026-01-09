# PR #4141: BadUSB: Added support for constants and variables definition

## Metadata
- **Author:** @fpacenza (Francesco Pacenza)
- **Created:** 2025-03-06
- **Status:** Open
- **Source Branch:** `dev`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4141

## Labels
`USB`, `New Feature`

## Description
# What's new

- Added the possibility to define constants via the `DEFINE` command
- Added the possibility to define variables via the `VAR` command

## Syntax
### DEFINE
`DEFINE NAME VALUE`
or
`DEFINE #NAME VALUE`

where

`DEFINE` denotes the start of a constant definition
`NAME` or `#NAME` is the label or key used to locate usage within your payload
`VALUE` is the value to replace matching instances of `NAME` throughout your payload

### VAR
`VAR $NAME = VALUE`

where

`VAR` denotes the start of a variable definition
`$NAME` is the variable name used to locate usage within your payload
`VALUE` is the value to replace matching instances of `NAME` throughout your payload

# Verification 

Create an example payload like the following one and run it.

### Payload Example
`STRINGLN --------- START TEST ---------`

`DEFINE CONSTANT constant value`
`DEFINE #CONSTANT constant value using # symbol`
`VAR $variable = my variable value`

`STRINGLN this is the value of the constant: CONSTANT`
`STRINGLN this is the value of the #constant: #CONSTANT`
`STRINGLN this is the value of the variable: $variable`

`STRINGLN --------- END TEST ---------`

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*

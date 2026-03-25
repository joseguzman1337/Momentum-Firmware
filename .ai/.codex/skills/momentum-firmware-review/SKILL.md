---
name: momentum-firmware-review
description: Review Flipper Zero firmware code changes for Momentum-specific patterns, security, and compatibility when analyzing firmware modifications or pull requests.
---

# Momentum Firmware Code Review

Review firmware code changes with focus on Momentum-specific requirements:

## Security Checks
- Verify no hardcoded credentials or sensitive data
- Check for buffer overflow vulnerabilities in C/C++ code
- Validate input sanitization for user-facing functions
- Ensure proper memory management (malloc/free pairs)

## Firmware Compatibility
- Confirm changes maintain backwards compatibility with existing apps
- Verify SubGhz frequency ranges stay within legal limits (281-361, 378-481, 749-962 MHz)
- Check GPIO pin configurations don't conflict with external modules
- Validate NFC protocol implementations follow standards

## Code Quality Standards
- Ensure consistent naming conventions (snake_case for C, camelCase for JS)
- Verify proper error handling and return codes
- Check for memory leaks in dynamic allocations
- Validate thread safety in concurrent operations

## Momentum-Specific Features
- Asset Pack compatibility (Anims, Icons, Fonts structure)
- Bad-KB USB/Bluetooth parameter validation
- BLE Spam functionality safety checks
- File management operations security

## Performance Considerations
- Check for blocking operations in UI threads
- Verify efficient memory usage patterns
- Validate battery impact of new features
- Ensure real-time constraints are met

Provide specific line-by-line feedback with security severity ratings and suggested fixes.
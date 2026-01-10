# Warp AI Agent Tasks for Momentum-Firmware

## Overview
Tasks to be executed in Warp Terminal's AI Agent Mode for the Momentum-Firmware project.

## How to Use
1. Open Warp Terminal
2. Navigate to: `cd /Users/x/x/Momentum-Firmware`
3. Type `#` to activate Warp AI Agent Mode
4. If you plan to use interactive tools (psql, dev servers, vim, debuggers, etc.), review `.ai/docs/full-terminal-use.md` so the agent can safely use Full Terminal Use inside those sessions.
5. Copy and paste each task below

---

## Priority Tasks

### Task 1: Code Quality Analysis
```
# Analyze the codebase for potential memory leaks and unsafe pointer usage in C/C++ files. 
# Focus on drivers/driverkit/ and lib/ directories. Generate a report with file locations and suggestions.
```

### Task 2: Documentation Generation
```
# Generate comprehensive API documentation for all JavaScript modules in applications/system/js_app/modules/
# Include function signatures, parameters, return types, and usage examples.
```

### Task 3: Test Coverage Analysis
```
# Analyze test coverage across the project. Identify critical modules without tests.
# Prioritize: drivers/, applications/services/, and lib/nfc/ directories.
# Generate a coverage report and suggest test cases for uncovered code.
```

### Task 4: Performance Optimization
```
# Profile the SubGHz signal processing code in applications/main/subghz/
# Identify performance bottlenecks and suggest optimizations.
# Focus on frequency analyzer and signal decoding functions.
```

### Task 5: Security Hardening
```
# Review all file I/O operations in applications/services/storage/ for path traversal vulnerabilities.
# Check for proper input validation and sanitization.
# Generate a security audit report with recommendations.
```

### Task 6: Dependency Update Check
```
# Check all git submodules and npm dependencies for available updates.
# Identify security patches and breaking changes.
# Generate an update plan with compatibility notes.
```

### Task 7: Build System Optimization
```
# Analyze the build system (Makefiles, SConstruct files) for optimization opportunities.
# Suggest parallel build improvements and caching strategies.
# Estimate potential build time reduction.
```

### Task 8: NFC Protocol Implementation Review
```
# Review NFC protocol implementations in lib/nfc/protocols/ for compliance with specifications.
# Check for edge cases and error handling.
# Suggest improvements for robustness.
```

### Task 9: Power Management Analysis
```
# Analyze power consumption patterns in applications/services/power/
# Identify opportunities for battery life optimization.
# Suggest low-power mode improvements.
```

### Task 10: Code Duplication Detection
```
# Find duplicate or similar code blocks across the codebase.
# Suggest refactoring opportunities to reduce code duplication.
# Focus on applications/ and lib/ directories.
```

---

## Continuous Integration Tasks

### CI Task 1: Automated Testing Pipeline
```
# Design a comprehensive CI/CD pipeline for this project.
# Include: build validation, unit tests, integration tests, security scans, and deployment.
# Generate GitHub Actions workflow files.
```

### CI Task 2: Code Review Automation
```
# Set up automated code review checks for pull requests.
# Include: style checking, complexity analysis, security scanning, and test coverage requirements.
```

---

## Issue Resolution Tasks (Remaining Open Issues)

### Issue #49: Charge Cap Not Working
```
# Investigate why the charge cap feature is not working properly.
# Review applications/services/power/power_service/power.c and related files.
# Identify the root cause and propose a fix.
```

### Issue #48: Keybind to Specific Folder
```
# Implement a feature to allow keybinding to specific folders (e.g., NFC cards folder).
# Review the navigation and input handling code.
# Design and implement the keybind system.
```

### Issue #47: NULL Pointer Dereference
```
# Find and fix all potential NULL pointer dereferences in the codebase.
# Use static analysis tools and manual code review.
# Prioritize critical paths and frequently used functions.
```

---

## Notes
- All tasks should be executed with repository context enabled
- Results should be saved to individual markdown files in `.warp-agent-results/`
- Each task should generate actionable recommendations
- Priority should be given to security and stability improvements

## Execution Log
- [ ] Task 1: Code Quality Analysis
- [ ] Task 2: Documentation Generation  
- [ ] Task 3: Test Coverage Analysis
- [ ] Task 4: Performance Optimization
- [ ] Task 5: Security Hardening
- [ ] Task 6: Dependency Update Check
- [ ] Task 7: Build System Optimization
- [ ] Task 8: NFC Protocol Implementation Review
- [ ] Task 9: Power Management Analysis
- [ ] Task 10: Code Duplication Detection

---
name: momentum-app-creator
description: Create new Flipper Zero applications for Momentum Firmware
metadata:
  short-description: Generate complete Flipper Zero apps with proper structure
---

# Momentum App Creator

Create new Flipper Zero applications following Momentum Firmware conventions and best practices.

## Context

- Momentum Firmware uses FBT (Flipper Build Tool) for compilation
- Apps are organized in `applications/` directory with subdirectories for different categories
- Each app requires an `application.fam` manifest file
- Apps use Furi framework and GUI system

## Instructions

When creating a new Flipper Zero app:

1. **Determine app category and location:**
   - `applications/main/` - Core system apps
   - `applications/external/` - Third-party apps
   - `applications/debug/` - Debug/development tools
   - `applications/examples/` - Example applications

2. **Create app structure:**
   ```
   applications/[category]/[app_name]/
   ├── application.fam
   ├── [app_name].c
   ├── [app_name]_i.h (if needed)
   ├── scenes/ (if using scene manager)
   └── icons/ (if custom icons needed)
   ```

3. **Generate application.fam:**
   ```python
   App(
       appid="app_name",
       name="App Display Name",
       apptype=FlipperAppType.EXTERNAL,
       entry_point="app_name_app",
       cdefines=["APP_NAME"],
       requires=["gui"],
       stack_size=2 * 1024,
       order=10,
       fap_icon="icon.png",
       fap_category="Category",
   )
   ```

4. **Create main C file with:**
   - Proper includes for Furi framework
   - App structure definition
   - Entry point function
   - GUI setup and event handling
   - Memory management

5. **Follow Momentum conventions:**
   - Use consistent naming (snake_case for files, PascalCase for types)
   - Include proper error handling
   - Use Furi logging system
   - Follow memory allocation patterns
   - Include proper cleanup in app exit

## Required Includes

```c
#include <furi.h>
#include <gui/gui.h>
#include <gui/view_dispatcher.h>
#include <gui/scene_manager.h>
#include <gui/modules/submenu.h>
```

## Build and Test

- Use `./fbt launch APPSRC=app_name` to build and run
- Test on actual hardware when possible
- Verify memory usage and cleanup
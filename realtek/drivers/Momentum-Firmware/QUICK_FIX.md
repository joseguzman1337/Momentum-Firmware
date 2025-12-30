# Quick Fix Reference Card

## 🚨 CRITICAL FIX - Do This First!

In Xcode, for your **DriverKit Extension target**:

```
Build Settings → Search "On-Demand" → Set ENABLE_ON_DEMAND_RESOURCES = NO
```

## ✅ Code Changes (Already Applied)

| File | Change | Status |
|------|--------|--------|
| `RTL8814AUDriverRTL8814AUDriver.swift` | Removed `import SystemExtensions` | ✅ Done |
| `RTL8814AUDriverTests.swift` | Added `import Testing` | ✅ Done |

## ⚙️ Xcode Settings (You Must Do)

### Each Target Needs Correct SDK:

| Target | Base SDK | Set To |
|--------|----------|--------|
| 🔌 DriverKit Extension | ❌ macOS | ✅ **DriverKit** |
| 🛠️ Builder Tool | ✅ macOS | ✅ **macOS** |
| 🧪 Tests | ✅ macOS | ✅ **macOS** |

**How to change:**
1. Select target in Xcode
2. Build Settings tab
3. Search "Base SDK"
4. Change dropdown

## 🔧 Quick Fix Steps

```bash
# 1. Run diagnostic
chmod +x fix-build-errors.sh
./fix-build-errors.sh

# 2. Open Xcode
open *.xcodeproj

# 3. For DriverKit target:
#    Build Settings → Base SDK → DriverKit
#    Build Settings → On-Demand Resources → NO

# 4. Clean & Build
# Product → Clean Build Folder (⇧⌘K)
# Product → Build (⌘B)
```

## 📖 Full Documentation

- **BUILD_FIX_SUMMARY.md** - Complete overview
- **BUILD_ERRORS_FIX.md** - Detailed error explanations
- **XCODE_PROJECT_SETUP.md** - Project setup guide

## ⚡ One-Liner Fix in Xcode

For the main error, in your DriverKit target Build Settings:

```
ENABLE_ON_DEMAND_RESOURCES = NO
```

That's it! 🎉

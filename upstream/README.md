# Official Flipper Zero Firmware Submodule

## Overview
The official Flipper Zero firmware has been added as a git submodule for reference, comparison, and upstream synchronization.

## Submodule Details
- **Location**: `upstream/flipperzero-firmware/`
- **URL**: https://github.com/flipperdevices/flipperzero-firmware.git
- **Current Commit**: `c9ab2b6827fc4d646e98ad0fc15a264240b58986`
- **Version**: 0.6.1-2270

## Usage

### Access Upstream Code
```bash
cd upstream/flipperzero-firmware/
```

### Update to Latest Official Release
```bash
# Update submodule to latest commit
git submodule update --remote upstream/flipperzero-firmware

# Or manually update
cd upstream/flipperzero-firmware
git fetch origin
git checkout origin/dev  # or specific tag/branch
cd ../..
git add upstream/flipperzero-firmware
git commit -m "chore: update official firmware submodule"
```

### Compare Changes
```bash
# Compare a specific file
diff applications/main/nfc/nfc_app.c upstream/flipperzero-firmware/applications/main/nfc/nfc_app.c

# Find differences in directory structure
diff -r applications/main/ upstream/flipperzero-firmware/applications/main/ --brief
```

### Merge Upstream Changes
```bash
# View upstream commits
cd upstream/flipperzero-firmware
git log --oneline -20

# Cherry-pick specific commits
git cherry-pick <commit-hash>

# Or merge entire branches
git merge upstream/dev
```

### Track Upstream Releases
```bash
# List available tags
cd upstream/flipperzero-firmware
git tag -l

# Checkout specific release
git checkout 0.6.1
```

## Integration Workflow

### 1. Monitor Upstream Changes
```bash
# Check for new commits
cd upstream/flipperzero-firmware
git fetch origin
git log HEAD..origin/dev --oneline
```

### 2. Review and Integrate
```bash
# Review changes
git diff HEAD..origin/dev

# Update submodule
git pull origin dev

# Return to main repo
cd ../..
git add upstream/flipperzero-firmware
git commit -m "chore: sync with official firmware"
```

### 3. Port Features
When porting features from official firmware:
1. Identify the feature in `upstream/flipperzero-firmware/`
2. Review implementation details
3. Adapt for Momentum-specific enhancements
4. Test thoroughly
5. Document the upstream source

## Automation

### Auto-Update Script
Create `.ai/scripts/sync_upstream.py`:
```python
#!/usr/bin/env python3
import subprocess
import os

os.chdir('upstream/flipperzero-firmware')
subprocess.run(['git', 'fetch', 'origin'])
subprocess.run(['git', 'checkout', 'origin/dev'])
os.chdir('../..')
subprocess.run(['git', 'add', 'upstream/flipperzero-firmware'])
subprocess.run(['git', 'commit', '-m', 'chore: auto-sync official firmware'])
```

### GitHub Actions Workflow
Add to `.github/workflows/sync-upstream.yml`:
```yaml
name: Sync Official Firmware
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          submodules: true
      
      - name: Update submodule
        run: |
          git submodule update --remote upstream/flipperzero-firmware
          git add upstream/flipperzero-firmware
          git diff --staged --quiet || git commit -m "chore: sync official firmware"
      
      - name: Create PR
        uses: peter-evans/create-pull-request@v7
        with:
          title: "chore: sync with official Flipper Zero firmware"
          body: "Automated sync with upstream official firmware"
```

## Benefits

1. **Reference Implementation**: Access official code for comparison
2. **Feature Porting**: Easily identify and port new features
3. **Bug Fixes**: Track and integrate official bug fixes
4. **Compliance**: Maintain alignment with official standards
5. **Documentation**: Reference official documentation and examples

## Notes

- The submodule is read-only for reference purposes
- Do not modify files in `upstream/flipperzero-firmware/` directly
- Always port changes to the main Momentum codebase
- Keep the submodule updated regularly to track latest changes
- Use for diff/comparison, not as a build dependency

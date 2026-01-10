# Forked Development Workflow

This repository utilizes a **Forked Submodule Architecture** to ensure stability, control, and secure backup of all dependencies. Instead of relying on upstream repositories (which may change or disappear), all submodules are forked to the maintainer's GitHub account and tied to specific synchronization branches.

## Architecture

*   **Main Repository**: `joseguzman1337/Momentum-Firmware` (Branch: `next`)
*   **Submodules**: All submodules (e.g., `lib/lwip`, `lib/FreeRTOS-Kernel`) point to forks under `https://github.com/joseguzman1337/`.
*   **Sync Branch**: Every submodule tracks a branch named `momentum-sync`. This branch represents the exact state of the code validated for the firmware build.

## Workflow

### 1. Initial Setup
When you first clone the repository, ensure you initialize submodules recursively:
```bash
git clone --recursive https://github.com/joseguzman1337/Momentum-Firmware.git
```

### 2. Making Changes to Submodules
If you need to patch a library (e.g., modify LwIP options):
1.  Enter the submodule directory.
2.  Make your changes.
3.  Commit them locally.
4.  Run the synchronization script (see below) to publish your changes to your fork.

### 3. Automated Synchronization
We have provided an automation script to simplify publishing submodule changes. This script:
1.  Iterates through all submodules.
2.  Pushes your current local commit to the `momentum-sync` branch on your remote fork.
3.  Ensures your local branch is tracking this remote branch.

**Usage:**
```bash
python3 .ai/scripts/sync_submodules.py
```

### 4. Updating the Main Repository
After syncing submodules, the main repository will detect valid pointer changes. You must commit these changes to the main firmware repo:

```bash
cd Momentum-Firmware
git add .
git commit -m "chore: Update submodule pointers"
git push origin next
```

## Maintenance
To migrate a new submodule or fix a broken remote:
1.  Fork the original repository to `joseguzman1337`.
2.  Update `.gitmodules` with the new URL.
3.  Run `git submodule sync`.
4.  Run the `.ai/scripts/sync_submodules.py` to initialize the sync branch.

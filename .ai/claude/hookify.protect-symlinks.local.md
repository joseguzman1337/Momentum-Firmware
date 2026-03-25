---
name: protect-symlinks
enabled: true
event: bash
pattern: rm\s+.*\s+(code/active|code/archive|tools|config/deploy)|unlink\s+(code/active|code/archive|tools|config/deploy)
---

🚨 **CRITICAL: SYMLINK DELETION DETECTED**

You're attempting to delete a legacy symlink that maintains backwards compatibility.

**Symlinks in this repository** (per STRUCTURE.md and CLAUDE.md):
- `code/active` → `src/`
- `code/archive` → `archive/`
- `tools/` → `scripts/`
- `config/deploy` → `infra/`

**Why these exist:**
These symlinks maintain backwards compatibility with existing scripts, documentation, and CI pipelines that reference the old paths.

**Before deleting:**

1. **Search for all references**:
   ```bash
   grep -r "code/active" .
   grep -r "tools/" . --exclude-dir=
   ```

2. **Update all references** in:
   - Documentation files (README, WARP.md, etc.)
   - Shell scripts
   - GitHub Actions workflows (.github/workflows/)
   - npm scripts in package.json files
   - Import statements in code

3. **Verify nothing breaks**:
   ```bash
   cd /src/core/tools
   make ci  # Full pipeline
   ```

**Per STRUCTURE.md:**
> Before removing symlinks, update all references (docs/scripts/CI) to the new paths.

Only proceed if you've completed the migration and verified all references are updated.

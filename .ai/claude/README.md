# Claude Code Configuration

This directory contains Claude Code configuration and hookify rules for this repository.

## Files

- `settings.local.json` - Claude Code permissions and settings
- `hookify.*.local.md` - Hookify rules (8 active rules)

## Hookify Rules Overview

This repository uses **intelligent hookify rules** that prevent architectural mistakes and enforce best practices during AI-assisted development.

### Security & Secrets (2 rules)

1. **prevent-secret-commits** - Blocks commits of `.env`, `*.key`, `*.pem`, credentials
2. **protect-firebase-security** - Warns when modifying security headers in firebase.json

### Architecture Enforcement (2 rules)

3. **enforce-prisma-workflow** - Blocks direct edits to generated Prisma clients
4. **protect-symlinks** - Prevents deletion of backwards-compatibility symlinks

### Development Safety (2 rules)

5. **warn-dangerous-docker** - Warns about destructive Docker commands
6. **require-tests-for-pentesting** - Reminds to add tests for security tools

### Workflow Optimization (2 rules)

7. **warn-lerna-without-stream** - Suggests `--stream` flag for better monorepo output
8. **completion-checklist** - Comprehensive checklist before marking tasks complete

## Managing Hooks

**List all hooks:**
```bash
/hookify:list
```

**Enable/disable a hook:**
Edit the `.local.md` file and change `enabled: true/false` in the frontmatter.

**Delete a hook:**
```bash
rm .claude/hookify.<name>.local.md
```

**Create new hooks:**
```bash
/hookify "description of behavior to prevent"
```

## Architecture Context

These hooks enforce constraints documented in:
- `CLAUDE.md` - Repository architecture and development guidelines
- `STRUCTURE.md` - Directory structure and symlink conventions
- `/src/README.md` - AI/ML lab pipeline requirements

## Why These Hooks?

Each hook addresses a real architectural constraint or common mistake pattern:

- **Secret commits**: Enforces "no secrets in repo" policy (STRUCTURE.md)
- **Firebase security**: Protects defense-in-depth design (CLAUDE.md)
- **Prisma workflow**: Prevents losing changes to generated code (Technical Debt #3)
- **Symlinks**: Maintains backwards compatibility with scripts/CI
- **Docker volumes**: Protects isolated service data architecture
- **Pentesting tests**: Ensures ethical use constraints are tested
- **Lerna streaming**: Improves developer experience with real-time output
- **Completion checklist**: Ensures quality before finishing tasks

## Customization

These hooks are **committed to the repository** to ensure all Claude Code instances follow the same architectural constraints. This creates consistency across:

- Team collaboration
- CI/CD automation
- Local development
- AI-assisted development sessions

If you need to temporarily disable a hook for a specific task, set `enabled: false` in the frontmatter rather than deleting the file.

## Documentation

See `CLAUDE.md § Hookify` for complete documentation including:
- Common use cases for this repository
- Hookify vs Git Hooks comparison
- Example workflows
- Best practices

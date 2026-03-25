---
name: warn-lerna-without-stream
enabled: true
event: bash
pattern: npx\s+lerna\s+run\s+(build|lint|test)(?!.*--stream)
---

💡 **LERNA COMMAND OPTIMIZATION TIP**

You're running a Lerna command without the `--stream` flag.

**Command:** `{command}`

**Why `--stream` matters** (per CLAUDE.md Monorepo Build System):

The repository uses **Lerna + npm workspaces** with topological dependency resolution. The `--stream` flag provides:

1. **Real-time output**: See build/lint progress immediately (not buffered)
2. **Better debugging**: Identify failures as they happen
3. **Interleaved output**: See all packages building in parallel

**Recommended commands:**

```bash
# Build in dependency order with streaming output
npx lerna run build --stream

# Lint all packages with real-time feedback
npx lerna run lint --stream

# Test with streaming (useful for long test suites)
npx lerna run test --stream
```

**Autonomous agent uses** (runs every 5 minutes):
```bash
npx lerna run lint --stream && \
npx lerna run build --stream && \
npm run test:e2e
```

**When to omit `--stream`:**
- You want summarized output only
- Running on CI where logs are captured differently
- Need to parse JSON output (`--json` flag)

This is just a tip - your command will still work without `--stream`.

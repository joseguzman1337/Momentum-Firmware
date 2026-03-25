---
name: enforce-prisma-workflow
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: node_modules/\.prisma/|@prisma/client
---

🛑 **GENERATED PRISMA CLIENT EDIT BLOCKED**

You're attempting to directly edit a generated Prisma client file:
**File:** `{file_path}`

**Why this is blocked:**
This is generated code that will be overwritten on the next Prisma generation. Direct edits will be lost.

**Documented in CLAUDE.md as Technical Debt #3:**
> Generated Prisma clients: Located in `/src/devsecops/node_modules/.prisma/`
> **NEVER edit directly** → always regenerate via `npm run db:generate`
> Pre-commit hook blocks direct edits (architectural enforcement)

**Correct workflow:**

1. **Modify the schema** (source of truth):
   ```bash
   cd /src/devsecops
   # Edit schema.prisma
   ```

2. **Create migration** (if schema changed):
   ```bash
   npm run db:migrate        # Postgres
   npm run db:migrate:sqlite # SQLite
   ```

3. **Regenerate client**:
   ```bash
   npm run db:generate
   ```

**If you need to extend Prisma client:**
- Use Prisma Client Extensions (official extension API)
- Add methods in separate service layer files
- Never modify generated files

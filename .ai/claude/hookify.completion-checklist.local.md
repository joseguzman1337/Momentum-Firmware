---
name: completion-checklist
enabled: true
event: stop
pattern: .*
---

✅ **COMPLETION CHECKLIST**

Before marking this task as complete, verify:

**Code Quality:**
- [ ] Code follows language-specific style guides (CLAUDE.md § Coding Standards)
  - JS/TS: 2-space indent, ESLint compliant
  - Python: Black/Ruff formatted, snake_case
  - Go: gofmt applied, lowercase packages
- [ ] No disabled ESLint rules added (technical debt item #1)
- [ ] No secrets/credentials in code or commits

**Testing:**
- [ ] Unit tests added for new functions (co-located with source)
- [ ] Integration tests updated if API contracts changed
- [ ] Tests pass: `make test` or `npm run test` in relevant directory
- [ ] For pentesting tools: pytest markers applied (`@pytest.mark.security`)

**Build System:**
- [ ] Build succeeds: `make build` or `npx lerna run build --stream`
- [ ] No new build warnings introduced
- [ ] Dependencies added to correct package.json (if any)

**Architecture Compliance:**
- [ ] Changes follow layered architecture (apps → packages → tools → dependencies)
- [ ] Shared types go in `@profil3r/shared` (not duplicated)
- [ ] Prisma schema changes regenerated via `npm run db:generate`
- [ ] Firebase security headers not weakened
- [ ] No direct edits to generated code

**Documentation:**
- [ ] CLAUDE.md updated if architectural changes made
- [ ] README updated if new commands/setup required
- [ ] Code comments added for non-obvious logic only

**Git Hygiene:**
- [ ] Commit message is descriptive and imperative mood
- [ ] Pre-commit hooks passed (Husky + lint-staged)
- [ ] No merge conflicts
- [ ] Branch is up to date with master

**Security (if applicable):**
- [ ] Security headers maintained (CSP, HSTS, X-Frame-Options)
- [ ] Input validation added for user-facing code
- [ ] No new vulnerabilities introduced (ran `npm audit` or `bandit`)
- [ ] Pentesting tools require explicit authorization

**Deployment (if applicable):**
- [ ] Environment variables documented (not committed)
- [ ] Firebase config updated if hosting changes
- [ ] Docker volumes backed up if data model changed
- [ ] Multi-cloud targets updated (Vercel/Cloudflare configs)

---

**This is a reminder, not a blocker.** Review items relevant to your changes.

If you've verified the applicable items, you may proceed.

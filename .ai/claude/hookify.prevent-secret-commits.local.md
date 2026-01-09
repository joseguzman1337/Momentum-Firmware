---
name: prevent-secret-commits
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: (\.env$|credentials\.json|\.pem$|\.key$|id_rsa|\.pfx$|\.p12$)
---

🚨 **SECRET FILE DETECTED - BLOCKING OPERATION**

You're attempting to write to a file that typically contains secrets:
**File:** `{file_path}`

**Why this is blocked:**
- Secret files should NEVER be committed to the repository
- This violates the security policy documented in CLAUDE.md
- Could expose API keys, credentials, or private keys

**What to do instead:**
1. Use `.env.example` as a template (gitignored actual `.env`)
2. Store secrets in environment variables
3. Use HashiCorp Vault for production secrets
4. Document required secrets in README without actual values

**Per STRUCTURE.md:**
> Keep secrets out of the repo; use environment-based injection and local `.env` files ignored by git.

If you absolutely need to add this file (e.g., creating .env.example template), acknowledge this warning explicitly.

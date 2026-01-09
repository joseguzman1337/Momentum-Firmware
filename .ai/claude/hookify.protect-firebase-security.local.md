---
name: protect-firebase-security
enabled: true
event: file
conditions:
  - field: file_path
    operator: equals
    pattern: firebase.json
  - field: new_text
    operator: regex_match
    pattern: (X-Frame-Options|Strict-Transport-Security|X-Content-Type-Options|X-XSS-Protection)
---

⚠️ **FIREBASE SECURITY HEADERS MODIFICATION DETECTED**

You're modifying security headers in `firebase.json`.

**Current headers enforce:**
- `X-Frame-Options: DENY` - Prevents clickjacking
- `Strict-Transport-Security: max-age=31536000` - Forces HTTPS for 1 year
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-XSS-Protection: 1; mode=block` - XSS protection

**Important architectural constraint:**
Per CLAUDE.md, security headers are enforced at Firebase level and CANNOT be bypassed by application code. This is a deliberate defense-in-depth security design.

**Before proceeding:**
1. Verify you're strengthening (not weakening) security
2. Understand the security implications
3. Document the change rationale in commit message
4. Consider if this should be reviewed by security team

**Acceptable changes:**
- Adding new security headers (Content-Security-Policy refinements)
- Increasing HSTS max-age
- Adding security-focused rewrites

**Unacceptable changes:**
- Removing security headers
- Weakening policies (e.g., X-Frame-Options: SAMEORIGIN)
- Reducing HSTS max-age

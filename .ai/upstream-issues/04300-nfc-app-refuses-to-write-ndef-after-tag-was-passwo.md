# Issue #4300: NFC app refuses to write NDEF after tag was password-protected, misinterprets AUTH0 / lock bytes for NTAG21x (tested on genuine NTAG216)

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4300](https://github.com/flipperdevices/flipperzero-firmware/issues/4300)
**Author:** @TomHarkness
**Created:** 2025-10-27T03:58:22Z
**Labels:** None

## Description

**Firmware:** Momentum & latest Official (latest build as of Oct 2025)  
**App:** Flipper NFC → NTAG21x / Advanced → Write / Read / Detect  
**Hardware tested:**  
- Genuine NXP NTAG216  
- Dangerous Things NExT implant (NTAG216 core)  

### Summary

After setting a password on a genuine NTAG216 or NExT implant (using standard NXP authentication scheme), Flipper detects the tag as "password protected" **even after the password is cleared and the tag is reset to default (AUTH0=FF)**.

Other NFC apps (e.g. NFC Tools, TagInfo) correctly detect the tag as **unprotected** and can read/write NDEF data normally.

The issue appears to be that Flipper’s NFC app incorrectly interprets bits in the **AUTH0** or **lock byte pages (0x28–0x2B)** as indicating password protection when it should not.

### Hypothesis

Flipper NFC’s NTAG21x detection logic likely interprets:
- `AUTH0` incorrectly (checking for non-`0xFF` or reserved bits)
- or `ACCESS` / `LOCK` bytes as indicating protection even when cleared.

The NTAG216 spec defines:
- `AUTH0 = 0xFF` → **no protection**
- `ACCESS` bits define protection granularity but do not indicate password presence directly.

Flipper might be reading stale or misaligned config bytes


### Reproduction

## Reproducible command sets (raw Type-2 frames)

> Use these command blocks in NFC Tools → Advanced → Raw / Advanced Commands (each comma-separated string is one run/sequence). They are the exact sequences we used to reproduce.

### 1) Check for a password / protection (diagnostic)
3029,302B,302A,3003,1B4E457854

**What this does**
- `3029` — READ page `0x29` (contains AUTH0; byte 3 = AUTH0). If AUTH0 != `FF` protection begins at that page.  
- `302B` — READ page `0x2B` (PWD page). Shows the 4-byte PWD if present.  
- `302A` — READ page `0x2A` (ACCESS byte + flags). Bit flags here (PROT, AUTHLIM, etc.) affect password behaviour.  
- `3003` — READ page `0x03` (Capability Container / CC) to confirm NDEF presence and memory sizing.  
- `1B4E457854` — PWD_AUTH using the lowercase `NExT` password (`4E 45 78 54`). If authentication succeeds the tag returns PACK (2 bytes). This proves whether `NExT` is accepted.

---

### 2) Set password to `NExT` and protect configuration pages only (leave user/NDEF area writable)
3029,302B,1B4E457854,A22B4E457854,A22CA55A0000,A22900002B00,1B4E457854,3029,302B

**What this does**
- `3029,302B` — Read current config & PWD pages (safety check).  
- `1B4E457854` — Attempt auth with `NExT` (safe; NAK if not set). If tag already protected it lets you proceed.  
- `A22B4E457854` — WRITE page `0x2B` = `4E 45 78 54` (set PWD = `NExT`).  
- `A22CA55A0000` — WRITE page `0x2C` = `A5 5A 00 00` (set PACK = `A5 5A`, padding zeroes).  
- `A22900002B00` — WRITE page `0x29` = `00 00 2B 00` (set `AUTH0 = 0x2B` so protection starts at page `0x2B` — this protects config pages but keeps NDEF/user memory writable).  
- `1B4E457854` — Authenticate again to verify the password returns PACK.  
- `3029,302B` — Read back `0x29` / `0x2B` to confirm changes.

---

### 3) Clear password and return tag to default/unprotected state
1B4E457854,A22B00000000,A22C00000000,A2290000FF00,3029,302B,3003,3004

**What this does**
- `1B4E457854` — Authenticate with current password `NExT` (required if config pages are currently protected).  
- `A22B00000000` — WRITE page `0x2B` = `00 00 00 00` (clear PWD).  
- `A22C00000000` — WRITE page `0x2C` = `00 00 00 00` (clear PACK).  
- `A2290000FF00` — WRITE page `0x29` = `00 00 FF 00` (set `AUTH0 = 0xFF` which disables password protection).  
- `3029,302B` — Read back `0x29` and `0x2B` to verify `AUTH0 = FF` and PWD cleared.  
- `3003,3004` — Read CC and first NDEF page to confirm the user memory and TLV are intact and writable.

---

## Observed vs expected behaviour

**Observed**
- After running the “clear password” block, `3029` shows `AUTH0 = 0xFF`, `302A` shows `ACCESS = 0x00`, and `302B`/`302C` show zeros — tag is unprotected and writable by phone tools.  
- Flipper NFC helper still reports “card protected by password AUTH0 or lock bits” and refuses to write saved NDEF via the helper. Raw page writes via Flipper CLI/UI may succeed, indicating the helper (not the hardware) is making the decision to abort.

**Expected**
- When `AUTH0 == 0xFF` and `ACCESS == 0x00` and `PWD/PACK` cleared, Flipper should treat the tag as unprotected and allow NDEF writes via the NFC helper.

---

## Suggested fixes for Flipper NFC app

1. **Correct AUTH0 interpretation** — treat `AUTH0 == 0xFF` as unprotected and allow writes. Do not conservatively block writes just because lock bytes are nonzero unless CFGLCK/permanent lock bits indicate irreversible config lock.  
2. **Distinguish permanent vs non-permanent lock bits** — interpret page `0x02` lock bytes according to the NTAG datasheet; only treat CFGLCK/irreversible bits as absolute blockers.  
3. **Prompt for PWD_AUTH when required** — if `AUTH0 <= first NDEF page` or `ACCESS` indicates protection that will affect the operation, prompt the user to supply a password and attempt `PWD_AUTH` rather than failing immediately.  
4. **Add an “Advanced/Force write (unsafe)” option** to allow expert users to bypass the helper checks (with clear warnings).  
5. **Always re-read config immediately before a write** — do not rely on cached/paranoid heuristics from earlier reads.

### 🧾 References

- [NXP NTAG213/215/216 Data Sheet — Section 8.8.2 AUTH0 definition](https://www.nxp.com/docs/en/data-sheet/NTAG213_215_216.pdf)
- [Dangerous Things NExT Documentation](https://dangerousthings.com/product/next/)

### Logs

```Text
## Commands & tag dumps (exact used during testing)

### Auth succeeded with `NExT`
1B4E457854
<< 00 00

---

### After clearing & setting `AUTH0 = FF`
A2 29 00 00 FF 00
<< 0A

30 29
<< 00 00 FF 00 00 00 00 00 00 00 00 00 00 00 00 00

30 2B
<< 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0

---

### CC and NDEF TLV
30 03
<< E1 10 6D 00 03 0B D1 01 07 54 02 65 6E 54 65 73

30 04
<< 03 0B D1 01 07 54 02 65 6E 54 65 73 74 FE 00 00

---

### UID and lock bytes
30 00
<< 04 A7 6E 45

30 01
<< 1A BD 39 80

30 02
<< 1E 48 00 00 // lock/OTP area (non-zero; normal for many tags)


> **Note:** tag is a genuine NXP NTAG216 sticker used for testing. Hu

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*

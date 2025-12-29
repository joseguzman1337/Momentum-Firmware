# FeliCa Protocol Security Considerations

## Code Scanning Alert: Use of 3DES Cryptographic Algorithm

### Issue Summary
Code scanning tools flag the use of `mbedtls_des3_set2key_enc()` and `mbedtls_des3_crypt_cbc()` in `felica.c` as security vulnerabilities due to the use of 3DES (Triple DES), a deprecated cryptographic algorithm.

### Why This Is NOT a Security Vulnerability

The use of 3DES in this implementation is **mandated by the FeliCa protocol specification** and cannot be changed without breaking compatibility with the entire FeliCa ecosystem.

#### Protocol Requirements
- **Specification**: FeliCa protocol (JIS X 6319-4, ECMA-340)
- **Requirement**: 3DES encryption for authentication and MAC calculation
- **Purpose**: Backward compatibility with existing FeliCa cards and infrastructure
- **Scope**: Used in Japan for transit cards (Suica, PASMO), payment cards, and other IC cards

#### Why 3DES Is Weak
Modern security standards consider 3DES weak because:
- **64-bit block size**: Vulnerable to birthday attacks with large amounts of data
- **Performance**: Slower than modern alternatives like AES
- **Deprecation**: NIST deprecated 3DES for new applications after 2023

#### Why We Can't Replace It
1. **Protocol Specification**: FeliCa spec requires 3DES for legacy card support
2. **Ecosystem Lock-in**: Billions of cards in circulation use 3DES
3. **No Alternative**: Changing the algorithm would make the implementation non-compliant
4. **Backward Compatibility**: Newer chips support AES but maintain 3DES for older cards

### Implementation Details

The 3DES algorithm is used in two critical functions:

1. **`felica_calculate_session_key()`** (line 544)
   - Derives session keys from card key and random challenge
   - Uses 3DES-CBC with 2-key variant

2. **`felica_calculate_mac()`** (line 590)
   - Calculates Message Authentication Codes
   - Uses 3DES-CBC for data integrity verification

### Mitigation Strategy

Since we cannot replace 3DES, we have implemented the following mitigations:

1. **Documentation**: Comprehensive comments explaining why 3DES is required
2. **Code Annotations**: CodeQL suppression annotations with justification
3. **Security Notes**: File-level and function-level security documentation
4. **Best Practices**: Correct implementation following the specification

### CodeQL Suppression

The code includes suppression annotations:
```c
// codeql[cpp/weak-cryptographic-algorithm] - Required by FeliCa protocol (JIS X 6319-4)
```

These annotations:
- Acknowledge the code scanner's concern
- Document that this is intentional and required
- Provide justification referencing the specification

### Future Considerations

For newer FeliCa implementations:
- **AES Support**: Newer FeliCa chips (2011+) support AES encryption
- **Dual Support**: Future versions could detect chip capabilities and use AES when available
- **Fallback**: 3DES would remain as fallback for older cards

### Recommendations

1. **Accept the Finding**: Acknowledge this is a protocol limitation, not a bug
2. **Document It**: Keep this security documentation for future reference
3. **Monitor Spec Changes**: Watch for FeliCa protocol updates that might add AES-only modes
4. **Consider Suppressions**: Add project-level suppressions for this specific case

### References

- **FeliCa Specification**: JIS X 6319-4, ECMA-340
- **Sony FeliCa**: https://www.sony.net/Products/felica/
- **NIST 3DES Deprecation**: NIST SP 800-131A Rev. 2
- **Wikipedia FeliCa**: https://en.wikipedia.org/wiki/FeliCa

### Conclusion

The use of 3DES in this FeliCa implementation is:
- ✅ **Correct** - Follows the specification
- ✅ **Necessary** - Required for compatibility
- ✅ **Documented** - Properly explained
- ✅ **Intentional** - Not an oversight

**This is a protocol-level limitation, not a code-level vulnerability.**

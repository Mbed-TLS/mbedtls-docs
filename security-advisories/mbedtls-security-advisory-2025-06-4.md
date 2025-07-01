# Out-of-bounds read in mbedtls_lms_import_public_key()

**Title** | Out-of-bounds read in mbedtls_lms_import_public_key()
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-49601
**Date** | 2025-06-30
**Affects** | Mbed TLS 3.3.0 through 3.6.3
**Not affected** | Mbed TLS 3.6.4 and later 3.6 versions and upcoming TF-PSA-Crypto 1.0 and later versions
**Impact** | Denial of service and possible information disclosure
**Severity** | MEDIUM
**Credits** | Found and reported by Linh Le and Ngan Nguyen from Calif.

## Vulnerability

An LMS public key starts with a 4-byte type indicator. The function `mbedtls_lms_import_public_key()`
reads this type indicator before validating the size of its input.

If a public key is shorted than 4 bytes, the function performs a buffer overread of up to 4 bytes,
resulting in undefined behavior. In practice this can only cause a crash and, at most,
leak whether those four bytes match a fixed value. No arbitrary code execution is possible.

## Impact

Denial of service and possible information disclosure of a few bytes of adjacent memory.
No arbitrary code execution or large‐scale memory disclosure is possible.

## Affected versions

Mbed TLS 3.3.0 through 3.6.3

## Resolution

Affected users should upgrade to Mbed TLS 3.6.4 or upcoming TF-PSA-Crypto 1.0 or later.

## Work-around

Validate that the key provided to `mbedtls_lms_import_public_key()` is at least 4 bytes long.

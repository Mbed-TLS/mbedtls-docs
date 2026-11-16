# Non-null-terminated output from mbedtls_x509_dn_gets (CVE-2026-115489)

**Title** | Non-null-terminated output from `mbedtls_x509_dn_gets()`
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-115489
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; all versions of Mbed TLS from 4.0.0 to 4.1.1; Mbed TLS 4.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later versions
**Impact** | Memory corruption in some calling applications
**CWE** | CWE-170: Improper Null Termination
**CAPEC** | CAPEC-123: Buffer Manipulation
**Severity** | HIGH
**Credits** | A. Pol (coredump.ws)

## Vulnerability

The documentation of `mbedtls_x509_dn_gets()` strongly implies that it writes a null-terminated string when it succeeds. It does so except in one edge case: when the output is empty. In this case, the output buffer is unmodified.

## Impact

Uses of `mbedtls_x509_dn_gets()` inside the library are unaffected. Applications that call this function directly may be affected, depending on how they use the function:

* If the output buffer passed to `mbedtls_x509_dn_gets()` starts with a null byte on entry (for example, if it was just obtained with `calloc()`), the usage is safe.
* If the output buffer `buf` starts with unpredictable content on entry and the caller reads the output using `strlen(buf)` as the size to read, this may disclose the content of the application memory until the next null byte.
* If the output buffer starts with unpredictable content on entry and the caller uses a function such as `strcpy()` or `sprintf` to copy the output to another buffer, this may overflow this other buffer.

## Affected versions

All versions of Mbed TLS up to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0 to 4.1.1 are affected.
Mbed TLS from 4.2.0 is affected.

## Work-around

Initializing the output buffer to 0 (e.g. with `calloc()`) avoids this vulnerability.

Reading or copying the output based solely on the length returned by `mbedtls_x509_dn_gets()`, and not on the presence of a null terminator, avoids this vulnerability.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version,
or to Mbed TLS 4.1.2 or a later 4.1.x version,
or to Mbed TLS 4.3.0 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.1.x | TF-PSA-Crypto 1.x (x&gt;1) | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | ------------------- | -------------------------- | -------------- | --------------------- |
| Basic fix | 8746a4afc62f310c28602598aa4511047c4f0e3d | N/A | N/A | c43dec5f2f877b27d555412a5ce24cb34940dd0c | 180af56b1082db4a8322ae20db24bc3b755d4450 |
| With tests and documentation | 57fdc54db8f94487a9c741c9dcf6ac6fffc1e56f..84714722f5b2aa840bd40d260fa5f1d4a79b0239 | N/A | N/A | cc95169ca370d94833f1fab0ea2a87c6f78e4b5f..2b073f7af453adcbcfe089fa1e3c9ead5dd75079 | 7128f9d7f9093e0ae71b6d0da3fb9d00bac37b87..96bb0647aff6ca5eea96236ee0bde1deb662b000 |

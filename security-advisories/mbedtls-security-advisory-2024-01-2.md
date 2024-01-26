# Buffer overflow in mbedtls_x509_set_extension()

**Title** |  Buffer overflow in mbedtls_x509_set_extension().
---|---
**CVE** |  CVE-2024-23775
**Date** |  09 January 2024
**Affects** |  All versions of Mbed TLS up to and including 2.28.6 and 3.5.1
**Impact** |  Potential DOS
**Severity** |  Low
**Credit** |  Jonathan Winzig (Hilscher Gesellschaft für Systemautomation mbH)

## Vulnerability

When writing x509 extensions we failed to validate inputs passed in to
mbedtls_x509_set_extension(), which could result in an integer overflow, causing
a zero-length buffer to be allocated to hold the extension. The extension would
then be copied into the buffer, causing a heap buffer overflow.

## Impact

Potential segfault resulting from the buffer overflow, thus potential DOS.

## Resolution

Affected users will want to upgrade to Mbed TLS 3.5.2 or 2.28.7 depending on the
branch they're currently using.

## Work-around

Ensure that a length of SIZE_MAX cannot be passed into
mbedtls_x509_set_extension()

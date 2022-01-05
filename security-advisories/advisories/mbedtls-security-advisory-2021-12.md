# Double Free in `mbedtls_ssl_set_session()` in an error case.

**Title** |  Double Free in `mbedtls_ssl_set_session()` in an error case.
---|---
**CVE** |  CVE-2021-44732
**Date** |  14th of December, 2021
**Affects** |  All versions of Mbed TLS
**Impact** |  An attacker could create memory / heap corruption.
**Severity** |  High
**Credit** |  duckPowerMB

## Vulnerability
If `mbedtls_ssl_set_session()` or `mbedtls_ssl_get_session()` were to fail with `MBEDTLS_ERR_SSL_ALLOC_FAILED` (in an out of memory condition), then calling `mbedtls_ssl_session_free()` and `mbedtls_ssl_free()` in the usual manner would cause an internal session buffer to be freed twice, due to two structures both having valid pointers to it after a call to `ssl_session_copy()`.

## Impact

An attacker could potentially trigger the out of memory condition, and therefore use this bug to create memory corruption, which could then be further exploited or targetted.

## Resolution

Affected users will want to upgrade to Mbed TLS 3.1.0, 2.28.0 or 2.16.12 depending on the branch they're currently using.

## Work-around
Either do not call `mbedtls_ssl_session_free()` (which will unfortunately cause a memory leak) or set the `mbedtls_ssl_session` field `ticket` to NULL manually, in the case where either `mbedtls_ssl_set_session()` or `mbedtls_ssl_get_session()` returns `MBEDTLS_ERR_SSL_ALLOC_FAILED`.


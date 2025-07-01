# Heap buffer under-read when parsing PEM-encrypted material

**Title** | Heap buffer under-read when parsing PEM-encrypted material
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-52497
**Date** | 30 June 2025
**Affects** | All versions of Mbed TLS up to 3.6.3 included
**Not affected** | Mbed TLS 3.6.4 and later 3.6 versions, upcoming releases of TF-PSA-Crypto (1.0 and later)
**Impact** | Denial of service, or potential information disclosure (CWE-127)
**Severity** | MEDIUM
**Credits** | Found and reported by Linh Le and Ngan Nguyen from Calif.

## Vulnerability

When parsing invalid PEM-encrypted material (with `mbedtls_pk_parse_key()`,
`mbedtls_pk_parse_keyfile()` or `mbedtls_pem_read_buffer()`), the decryption
code may attempt reading 1 byte before the beginning of a heap buffer (that was
allocated by the same function).

## Impact

This will typically result in a Denial of Service, or limited information
disclosure.

## Affected versions

All versions of Mbed TLS up to 3.6.3 are affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.4 or later - or TF PSA Crypto 1.0
or later when it is released.

## Work-around

Applications are only affected if they process untrusted PEM-encrypted material
(that is, if they call one of the above functions with a non-NULL password
argument and untrusted PEM input).

Applications built with `MBEDTLS_PEM_C` disabled are not affected.

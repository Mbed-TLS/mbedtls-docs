# TLS 1.2 server accepts client CertificateVerify algorithms outside configured sig_algs (CVE-2026-93777)

**Title** | TLS 1.2 server accepts client CertificateVerify algorithms outside configured sig_algs
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-93777
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; all versions of Mbed TLS from 4.0.0 to 4.1.1; Mbed TLS version 4.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3 and later 4.x versions
**Impact** | TLS 1.2 server accepts secure client CertificateVerify algorithms outside configured sig_algs
**CWE** | CWE-295: Improper Certificate Validation
**CAPEC** | CAPEC-114: Authentication Abuse
**Severity** | LOW
**Credits** | Reported by Ramesh Adhikari (IoTSec.in) and Saikumar Andure (saikumar279)

## Vulnerability

A server configured with `mbedtls_ssl_conf_sig_algs()`
or `mbedtls_ssl_conf_sig_hashes()` to request only specific TLS 1.2 client
signature and hash algorithms does not actually enforce that policy when
validating the client’s CertificateVerify message.

One real-world scenario where this might be encountered is using a TLS 1.2
mutual-auth handshake between the Mbed TLS server and client, because our client
ignores the server's requested signature and hash algorithms when constructing
the CertificateVerify message, and instead uses the key configured via the first
call to `mbedtls_ssl_conf_own_cert()` and the PRF of the negotiated ciphersuite.

See the documentation of `mbedtls_ssl_conf_own_cert()`, and the comments in
`ssl_parse_certificate_request()` and `ssl_write_certificate_verify()`.

## Impact

The TLS 1.2 server accepts secure client CertificateVerify algorithms supported
by the server, but disallowed via `mbedtls_ssl_conf_sig_algs()` or
`mbedtls_ssl_conf_sig_hashes()`

## Affected versions

All versions of Mbed TLS up to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0 to 4.1.1 are affected.
Mbed TLS version 4.2.0 is affected.

## Work-around

Disabling the undesired signature and hash algorithms in
`mbedtls_config.h` / `crypto_config.h` mitigates the issue.

Only servers accepting TLS 1.2 connections that have been configured to reject
signature or hash algorithms via `mbedtls_ssl_conf_sig_algs()` or
`mbedtls_ssl_conf_sig_hashes()`, which are otherwise supported by
the configuration in `mbedtls_config.h` / `crypto_config.h` are affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version,
or to Mbed TLS 4.1.2 or a later 4.1.x version,
or to Mbed TLS 4.3 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.1.x | TF-PSA-Crypto 1.x (x&gt;1) | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | ------------------- | -------------------------- | -------------- | --------------------- |
| Basic fix | f47df70cd11011d9f73808fd90543aa3e6117bef | N/A | N/A | d8b343ba9dbab2360ba83c98d525ccf7ebd05cf9 | ef8f3733e4a259109128f85e650d9818bd44ad2b |
| With tests and documentation | 7b7ff06d6a261f85dac20c013e2684180afa7c6e..1317d8fa657197abf995714962cff2290bd9a766 | N/A | N/A | 5471f382e5a4df392f86c3a80e0696d7250f6b5b..1b48601aeadb970c8b0e63187cb16570b8633b7f | 9d76b2ee09ce71b9a578ed566e60822bec30d03e..30d02638af2bc78425709a699bd02c0fa59374da |

# Signature Algorithm Injection

**Title** | Signature Algorithm Injection
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-25834
**Date** | 31 March 2026
**Affects** | All versions of Mbed TLS from 3.3.0 up to 3.6.5 and 4.0.0
**Not affected** | Mbed TLS 3.6.6 and later 3.6 versions, 4.1.0 and later 4.x versions
**Impact** | Policy bypass
**Severity** | LOW
**Credits** | EFR-GmbH and M. Heuft of Security-Research-Consulting GmbH

## Vulnerability

If the server ignores the signature algorithms extension sent by the client hello, the client needs to respond with an error message and break connection if it wants to enforce the security policy set during configuration (see `mbedtls_ssl_conf_sig_algs()`).

The Mbed TLS client in the affected versions will accept any signature algorithm choice that the server makes, so long as support for it was enabled at compile time. This happens even if the selected algorithm was not configured via `mbedtls_ssl_conf_sig_algs()` and thus advertised in the client hello. The issue affects only TLS 1.2.

## Impact

Security policy bypass: security policy set with `mbedtls_ssl_conf_sig_algs()` is ignored in the client.

## Affected versions

All versions of Mbed TLS from 3.3.0 up to 3.6.5 and 4.0.0 are affected.

## Work-around

Enable only the algorithms allowed by the security policy at compile time.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.6 or 4.1.0

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.x | Mbed TLS 4.x |
| ------ | -------------- | ----------------- | ------------ |
| Basic fix | 0165a8d7637a458f49cfe01be1f21aa0f91143d7 | N/A | d7b85b76a66354fedab299c27e6a8da9e26e08fe |
| With tests and documentation | branch up to 562326e4915f448406abd381c0bc23bd01e4159f | N/A | branch up to 6714b3901775978bd6ed6681cc65b957f9c9966f |

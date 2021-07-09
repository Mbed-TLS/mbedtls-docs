# mbed TLS Security Advisory 2017-02

**Title** |  Bypass of authentication of peer possible when the authentication
mode is configured as 'optional'
---|---
**Date** |  28th August 2017
**Affects** |  All versions of mbed TLS from version 1.3.10 and up, including
all 2.1 and later releases
**Not affected** |  mbed TLS 1.3.9 and earlier
**Impact** |  Use of the 'optional' authentication mode can permit the peer to
bypass peer authentication
**Severity** |  High

## Vulnerability

If a malicious peer supplies an X.509 certificate chain that has more than
`MBEDTLS_X509_MAX_INTERMEDIATE_CA` intermediates (which by default is 8), it
could bypass authentication of the certificates, when the authentication mode
was set to 'optional' eg. `MBEDTLS_SSL_VERIFY_OPTIONAL`. The issue could be
triggered remotely by both the client and server sides.

If the authentication mode, which can be set by the function
`mbedtls_ssl_conf_authmode()`, was set to 'required' eg.
`MBEDTLS_SSL_VERIFY_REQUIRED` which is the default, authentication would occur
normally as intended.

## Impact

Depending on the platform, an attack exploiting this vulnerability could allow
successful impersonation of the intended peer and permit man-in-the-middle
attacks.

## Resolution

Affected users should upgrade to mbed TLS 1.3.21, mbed TLS 2.1.9 or mbed TLS
2.6.0.

## Workaround

Users should wherever possible upgrade to the newer version of mbed TLS. Where
this is not practical, users should consider if changing the authentication to
the 'required' mode `MBEDTLS_SSL_VERIFY_REQUIRED` is practical for their
application.

### Like this?

**Section:**
Security Advisories

**Author:**
Simon Butcher

**Published:**
Aug 28, 2017

**Last updated:**
Aug 28, 2017
# mbed TLS Security Advisory 2018-01

This Security Advisory describes two vulnerabilities, their impact and fixes
for each possible attack.

* * *

**Title** |  Risk of remote code execution when truncated HMAC is enabled
---|---
**CVE** |  CVE-2018-0488
**Date** |  1st February 2018
**Affects** |  All versions of Mbed TLS from version 1.3.0 and up, including
all 2.1 and later releases
**Not affected** |  Mbed TLS 1.2.19 and earlier
**Impact** |  Enabling truncated HMAC can lead to remote code execution
**Severity** |  High

## Vulnerability

When the truncated HMAC extension is enabled and CBC is used, sending a
malicious application packet can be used to selectively corrupt 6 bytes on the
peer's heap, potentially leading to a crash or remote code execution. This can
be triggered remotely from either side in both TLS and DTLS.

If the truncated HMAC extension, which can be set by the compile time option
`MBEDTLS_SSL_TRUNCATED_HMAC` in `config.h`, is disabled when compiling the
library, then the vulnerability is not present. The truncated HMAC extension
is enabled in the default configuration.

The vulnerability is only present if

  * The compile-time option `MBEDTLS_SSL_TRUNCATED_HMAC` is set in `config.h`. (It is set by default) AND
  * The truncated HMAC extension is explicitly offered by calling `mbedtls_ssl_conf_truncated_hmac()`. (It is not offered by default)

## Impact

Depending on the platform, an attack exploiting this vulnerability could lead
to an application crash or allow remote code execution.

## Resolution

Affected users should upgrade to Mbed TLS 1.3.22, Mbed TLS 2.1.10 or Mbed TLS
2.7.0.

## Workaround

Users should wherever possible upgrade to the newer version of Mbed TLS. Where
this is not practical, users should consider disabling the truncated HMAC
extension by removing any call to `mbedtls_ssl_conf_truncated_hmac()` in their
application, and the option `MBEDTLS_SSL_TRUNCATED_HMAC` in the Mbed TLS
configuration is practical for their application.

* * *

**Title** |  Risk of remote code execution when verifying RSASSA-PSS
signatures
---|---
**CVE** |  CVE-2018-0487
**Date** |  1st February 2018
**Affects** |  All versions of Mbed TLS from version 1.3.8 and up, including
all 2.1 and later releases
**Not affected** |  Mbed TLS 1.3.7 and earlier
**Impact** |  Verifying a maliciously constructed RSASSA-PSS signature can
lead to remote code execution
**Severity** |  High

## Vulnerability

When RSASSA-PSS signature verification is enabled, sending a maliciously
constructed certificate chain can be used to cause a buffer overflow on the
peer's stack, potentially leading to crash or remote code execution. This can
be triggered remotely from either side in both TLS and DTLS.

RSASSA-PSS is the part of PKCS #1 v2.1 standard and can be enabled by the
compile time option `MBEDTLS_PKCS1_V21` in `config.h`. If `MBEDTLS_PKCS1_V21`
is disabled when compiling the library, then the vulnerability is not present.
RSASSA-PSS signatures are enabled in the default configuration.

## Impact

Depending on the platform, an attack exploiting this vulnerability could lead
to an application crash or remote code execution.

## Resolution

Affected users should upgrade to Mbed TLS 1.3.22, Mbed TLS 2.1.10 or Mbed TLS
2.7.0.

## Workaround

Users should wherever possible upgrade to the newer version of Mbed TLS. Where
this is not practical, users should consider if disabling the option
`MBEDTLS_PKCS1_V21` in the Mbed TLS configuration is practical for their
application. Disabling RSASSA-PSS signatures in the verification profile at
runtime is not a sufficient countermeasure.

### Like this?

**Section:**
Security Advisories

**Author:**
Simon Butcher

**Published:**
Feb 5, 2018

**Last updated:**
Feb 5, 2018
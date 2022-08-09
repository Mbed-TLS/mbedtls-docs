# mbed TLS Security Advisory 2017-01

This Security Advisory describes three vulnerabilities, their impact and fixes
for each possible attack.

* * *

**Title** | Freeing of memory allocated on stack when validating a public key<br>with a secp224k1 curve
--- | ---
**CVE** | CVE-2017-2784
**Date** | 10th March 2017 ( **Updated on 13th March 2017** )
**Affects** | mbed TLS 1.4 and up
**Not affected** | mbed TLS 1.3.19 and up, mbed TLS 2.1.7 and up, mbed TLS 2.4.2 and up,<br>and any version compiled without support for secp224k1 curves
**Impact** | Denial of service and possible remote code execution
**Severity** | High
**Credit** | Aleksandar Nikolic, Cisco Talos team and [rongsaws](https://github.com/rongsaws)

## Vulnerability

If a malicious peer supplies a certificate with a specially crafted secp224k1
public key, then an attacker can cause the server or client to attempt to free
block of memory held on stack.

## Impact

Depending on the platform, this could result in a Denial of Service (client
crash) or potentially could be exploited to allow remote code execution with the
same privileges as the host application.

## Resolution

Affected users should upgrade to mbed TLS 1.3.19, mbed TLS 2.1.7 or mbed TLS
2.4.2.

## Workaround

Users can disable the secp224k1 curve by disabling the option
`MBEDTLS_ECP_DP_SECP224K1_ENABLED` in their `config.h` file.

* * *

**Title** | SLOTH vulnerability
--- | ---
**Date** | 10th March 2017 ( **Updated on 13th March 2017** )
**Affects** | mbed TLS 2.4.0 and mbed TLS 2.4.1
**Not affected** | Any other version of mbed TLS
**Impact** | Client impersonation
**Severity** | Moderate

## Vulnerability

If the client and the server both support MD5 and the client can be tricked to
authenticate to a malicious server, then the malicious server can impersonate
the client. To launch this man in the middle attack, the adversary has to
compute a chosen-prefix MD5 collision in real time. This is very expensive
computationally, but can be practical.

This was introduced inadvertently in an interoperability fix in version 2.4.0.

## Impact

Depending on the platform and how it's configured, a client could be tricked
into authenticating to a malicious server, and then the malicious server could
impersonate the client, thereby performing a man in the middle attack.

## Resolution

Affected users should upgrade to mbed TLS 2.4.2.

* * *

**Title** | Denial of Service through Certificate Revocation List
--- | ---
**Date** | 10th March 2017 ( **Updated on 13th March 2017** )
**Affects** | mbed TLS versions prior to 1.3.19, 2.1.7 or 2.4.2
**Not affected** | mbed TLS 1.3.19 and up, mbed TLS 2.1.7 and up, mbed TLS 2.4.2 and up,<br>any version compiled without PEM support and when used by an application<br>not verifying CRLs
**Impact** | Denial of service
**Severity** | Moderate
**Credit** | Greg Zaverucha, Microsoft

## Vulnerability

A bug in the logic of the parsing of a PEM encoded Certificate Revocation List
in `mbedtls_x509_crl_parse()` can result in an infinite loop. In versions before
1.3.10 the same bug results in an infinite recursion stack overflow that usually
crashes the application.

## Impact

Methods and means of acquiring the CRLs is not part of the TLS handshake and in
the strict TLS setting this vulnerability cannot be triggered remotely. The
vulnerability cannot be triggered unless the application explicitely calls
`mbedtls_x509_crl_parse()` or `mbedtls_x509_crl_parse_file()`on a PEM formatted
CRL of untrusted origin. In which case the vulnerability can be exploited to
launch a denial of service attack against the application.

## Resolution

Affected users should upgrade to mbed TLS 1.3.19, mbed TLS 2.1.7 or mbed TLS
2.4.2.

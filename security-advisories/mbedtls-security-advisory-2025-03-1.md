# TLS clients may unwittingly skip server authentication

**Title** | TLS clients may unwittingly skip server authentication
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-27809
**Date** | 24 March 2025
**Affects** | All versions of PolarSSL and Mbed TLS
**Severity** | HIGH

## Vulnerability

The security of the TLS protocol relies on clients authenticating the server.
If a TLS client fails to authenticate the server, a network-based attacker can act as a man-in-the-middle and impersonate the server to the client.

Server authentication relies on one of two mechanisms, depending on the key exchange mode: either a pre-shared key or a certificate chain. The vulnerability considered here affects certificate-based authentication.

Certificate-based authentication has three steps, all of which are necessary:

* The end certificate must be issued for the server that the client is trying to reach. Mbed TLS checks that the certificate content matches the name passed to `mbedtls_ssl_set_hostname()`.
* The certificate chain must be valid. Mbed TLS always checks this.
* The root of the certificate chain must be a trusted certificate authority (trusted CA). Certificate authentication will fail if no trusted CAs are defined.

Due to an insecure default in Mbed TLS up to 2.8.9 and Mbed TLS 3.x up to 3.6.2, if a TLS client application does not call `mbedtls_ssl_set_hostname()`, the first step is silently skipped. This allows any server with a certificate signed by a trusted CA to impersonate any other server.

## Impact

TLS client applications that do not call `mbedtls_ssl_set_hostname()` are likely to be vulnerable to impersonation by a network-based attacker. This gives the attacker access to all the data exchanged over TLS, and the ability to modify this data.

## Affected versions

All versions of PolarSSL, all versions of Mbed TLS up to 2.28.9, and all versions of Mbed TLS 3.x up to 3.6.2 are affected.

## Resolution

Developers of TLS client applications should ensure that their application calls `mbedtls_ssl_set_hostname()` with the expected server name, unless they only allow cipher suites (key exchange modes in TLS 1.3) based on a pre-shared key.

Please note that TLS client applications typically need to mention the server name twice: once to the network stack (e.g. to `mbedtls_net_connect()`) to set up the underlying transport, and once to the TLS stack (to `mbedtls_ssl_set_hostname()`) to arrange for server authentication.

We recommend that users should upgrade to Mbed TLS 2.28.10 or Mbed TLS 3.6.3. These versions disable the insecure default, and instead cause certificate authentication to fail if `mbedtls_ssl_set_hostname()` has not been called.

## Work-around

TLS client applications should call `mbedtls_ssl_set_hostname()` with the expected server name, unless they only allow cipher suites (key exchange modes in TLS 1.3) based on a pre-shared key.

TLS clients are not affected if they operate in a closed ecosystem where the trusted certificate authority only issues certificates to trusted hosts. We still recommend calling `mbedtls_ssl_set_hostname()` as a second line of defense in case a part of the public-key infrastructure is compromised.

TLS clients are not affected if, before exchanging any data on the TLS connection, they check that the fingerprint of the server certificate matches a known good fingerprint (certificate pinning).

TLS clients that only allow connections using pre-shared keys are not affected.

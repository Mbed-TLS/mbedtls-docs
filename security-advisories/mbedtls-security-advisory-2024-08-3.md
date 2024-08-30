# Limited authentication bypass in TLS 1.3 optional client authentication

**Title** | Limited authentication bypass in TLS 1.3 optional client authentication
--------- | -----------------------------------------------------
**CVE** | CVE-2024-45159
**Date** | 30 August 2024
**Affects** | Mbed TLS 3.2.0 to 3.6.0 included
**Severity** | Medium

## Vulnerability

TLS servers can use optional authentication of the client with
`mbedtls_ssl_conf_authmode(..., MBEDTLS_SSL_VERIFY_OPTIONAL);`, then after the
handshake has completed, call `mbedtls_ssl_get_verify_result()` to check if
the client provided a certificate and if it was correct. If a certificate was
not provided or it was not valid, the return value of this function should be
non-zero, with particular bits set to indicate what exactly was wrong about
the certificate.

In particular, with TLS 1.3, if a client presents a certificate that does not
have the `digitalSignature` bit set in its `keyUsage` extension, the bit
`MBEDTLS_X509_BADCERT_KEY_USAGE` should be set in the return value of
`mbedtls_ssl_get_verify_result()`. Similarly, if the certificate doesn't have
`clientAuth` listed in its `extKeyUsage` extension, the return value should
have the bit `MBEDTLS_X509_BADCERT_EXT_KEY_USAGE` set.

With TLS 1.3 in Mbed TLS 3.6.0, this was not happening: those two bits were
always unset, regardless of whether the `keyUsage` and `extKeyUsage`
extensions were correct or not. In particular, if those were the only issues
with the certificate, `mbedtls_ssl_get_verify_result()` would return `0`,
incorrectly presenting the certificate as fully valid.

This only impacts TLS 1.3 optional client authentication. Mandatory authentication
(`MBEDTLS_SSL_VERIFY_REQUIRED`) is not affected (it will correctly abort the
handshake with a fatal alert if the client certificate is absent or invalid).
TLS 1.2 authentication is not affected. TLS 1.3 server authentication is not
affected, as before 3.6.1 it could not be made optional.

## Impact

An attacker in possession of a certificate valid for uses other than TLS
client authentication was able to use it for TLS client authentication.

Note that the certificate needs to be valid (in particular, signed by a CA
trusted by the victim TLS server) except for the `keyUsage` and `extKeyUsage`
extension values.

## Affected versions

The vulnerability was present in 3.2.0 which was the first version to support
client authentication in TLS 1.3.

Note that until 3.6.0, support for TLS 1.3 was disabled in the default
compile-time configuration, which meant the vulnerability was not present in a
default build. In 3.6.0, TLS 1.3 became enabled by default, making the
vulnerability present in the default configuration.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.1.

## Work-around

The issue can be avoided by forcing use of TLS 1.2 with connections that use
optional client authentication. That is, all servers that call
`mbedtls_ssl_conf_authmode(..., MBEDTLS_SSL_VERIFY_OPTIONAL);` should also call
`mbedtls_ssl_conf_max_tls_version(..., MBEDTLS_SSL_VERSION_TLS1_2);`.


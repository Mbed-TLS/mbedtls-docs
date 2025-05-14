# CVE-2025-27809 FAQ

This this an FAQ for [CVE-2025-27809](../../security-advisories/mbedtls-security-advisory-2025-03-1/).

## Too long, won't read!

In TLS client applications using Mbed TLS, make sure that `mbedtls_ssl_set_hostname()`is called.

If your application fails with `MBEDTLS_ERR_SSL_CERTIFICATE_VERIFICATION_WITHOUT_HOSTNAME` with Mbed TLS 3.6.3 or newer, or with Mbed TLS 2.28.10, [fix it by adding a call to `mbedtls_ssl_set_hostname()`](#my-application-is-vulnerable-how-do-i-fix-it).

## Am I affected?

### What versions of Mbed TLS are affected?

At the root, this is a vulnerability in application code.

In all versions of Mbed TLS up to and including 2.28.9, as well as all versions of Mbed TLS 3.x up to and including 3.6.2, affected applications are silently insecure. Newer versions of Mbed TLS ensure that affected applications will fail safely if they encounter an insecure situation.

### What versions of Mbed TLS fix the vulnerability?

Mbed TLS 2.28.10 and 3.6.3 fix the vulnerability by returning an error if the server host name is needed, but not set.

The error is a new error code `MBEDTLS_ERR_SSL_CERTIFICATE_VERIFICATION_WITHOUT_HOSTNAME`, which is only used for this specific purpose.

### Is my application vulnerable?

TLS clients that use a certificate to authenticate the server (as opposed to pre-shared keys) are affected. This is the most common way to use TLS.

Note that this is not related to whether the client has a certificate (one-way vs mutual TLS). The vulnerability is related to checking the server's certificate, which is the normal case for SSL/TLS.

If your application is a TLS client, check whether it calls `mbedtls_ssl_set_hostname()`. If a TLS client calls `mbedtls_ssl_set_hostname()` with a non-null host name on the SSL context before the handshake (i.e. before `mbedtls_ssl_handshake()`), then it is not vulnerable.

Note that applications should typically specify the server name twice: once to the TLS library with `mbedtls_ssl_set_hostname()`, and once to the network layer, for example with `mbedtls_net_connect()`.

### How do I test if my application is vulnerable?

You can test your TLS client application with Mbed TLS 2.28.10, 3.6.3 or newer. With these versions of Mbed TLS, the handshake fails with the error `MBEDTLS_ERR_SSL_CERTIFICATE_VERIFICATION_WITHOUT_HOSTNAME` if the server's certificate needs to be checked. If the handshake succeeds in normal usage, your application is not vulnerable.

Note a few unusual cases where the handshake might not fail in a vulnerable application:

* If a TLS client allows both pre-shared key (PSK) and certificate-based key exchange modes, make sure to test it with a certificate-based key exchange. A PSK handshake does not trigger the problematic case, so it is an inconclusive test.
* If a TLS client changes the certificate verification mode to `NONE` or `OPTIONAL` (from the default `REQUIRED`) with `mbedtls_ssl_conf_authmode()`, Mbed TLS assumes that you know what you're doing and does not raise `MBEDTLS_ERR_SSL_CERTIFICATE_VERIFICATION_WITHOUT_HOSTNAME`. TLS clients that don't require server authentication should call `mbedtls_ssl_get_verify_result()` and perform all required checks after the handshake and before exchanging data, including checking the server name in the certificate.

### Are all TLS clients vulnerable if they don't call `mbedtls_ssl_set_hostname`?

In most cases, in particular when connecting to a server on the web, `mbedtls_ssl_set_hostname()` is necessary. In a few cases, it is safe not to call this function:

* `mbedtls_ssl_set_hostname()` is only necessary for certificate authentication. It is not necessary when using a pre-shared key (PSK), since in that case the shared secret key is enough to authenticate the server.
* If the client operates in a closed ecosystem where the trusted certificate authority (CA) only issues certificates to trusted hosts, then even without `mbedtls_ssl_set_hostname()`, the client knows that it is connected to a trusted host. We still recommend calling `mbedtls_ssl_set_hostname()` as a second line of defense in case a part of the public-key infrastructure is compromised.
* A client is not vulnerable if, before exchanging any data on the TLS connection, it checks that the fingerprint of the server certificate matches a known good fingerprint (certificate pinning).
* The attack relies on the possibility to impersonate the server at the network level (e.g. at the IP level on the Internet). Passive attackers cannot exploit this vulnerability.

## How do I fix?

### My application is vulnerable, how do I fix it?

If your TLS client application is not calling `mbedtls_ssl_set_hostname()`, make sure that it does. Unless you have a good reason, the server name should be the same name that is passed to the network stack, for example to `mbedtls_net_connect()`.

A minimal set of calls to establish a TLS connection with default parameters in Mbed TLS 2.x or 3.x is:

```
mbedtls_ssl_config_init()
mbedtls_ssl_config_defaults()   // say I'm a client
mbedtls_ssl_conf_rng()
mbedtls_ssl_conf_ca_chain()     // declare my root CA
mbedtls_ssl_init()
mbedtls_ssl_setup()
mbedtls_ssl_set_bio()
mbedtls_ssl_set_hostname()      // which host to connect to: TLS
mbedtls_net_connect()           // which host to connect to: network
mbedtls_ssl_handshake()
```

See the example program `programs/ssl/ssl_client1.c` for a minimal secure example of a TLS client.

### I use an older version of Mbed TLS. How can I fix my application?

The fix is the same for all versions of Mbed TLS. TLS clients that rely on a certificate to authenticate the server (which is usually the case) must call `mbedtls_ssl_set_hostname()` to declare the server name.

### Do I need to upgrade Mbed TLS?

You do not need to upgrade Mbed TLS. [If your application is not vulnerable](#is-my-application-vulnerable), upgrading Mbed TLS is not necessary. If your application is vulnerable, the same fix works in old and new versions of Mbed TLS.

With respect to this vulnerability, the only advantage of upgrading Mbed TLS is that if an insecure scenario is detected at runtime, older versions establish a potentially insecure TLS connection, whereas newer versions close the TLS connection.

### I use Mbed TLS via a middleware layer. Am I affected?

If the middleware offers an interface to connect to a TLS server, and it takes care both of the network connection and the TLS channel, then the middleware should probably take care of calling `mbedtls_ssl_set_hostname()`. Consult the documentation of the middleware to see whether it does so, or it expects your application to do it.

If you are unsure whether the middleware calls `mbedtls_ssl_set_hostname()`, upgrade to at least Mbed TLS 3.6.3 (or Mbed TLS 2.28.10 if using the 2.28 long-time support branch) and try connecting to a TLS server. If the TLS handshake succeeds, the middleware is safe to use. If the TLS handshake fails with the error `MBEDTLS_ERR_SSL_CERTIFICATE_VERIFICATION_WITHOUT_HOSTNAME`, a call to `mbedtls_ssl_set_hostname()` is missing.

### How do I fix `MBEDTLS_ERR_SSL_CERTIFICATE_VERIFICATION_WITHOUT_HOSTNAME`?

You should change your TLS client application to call `mbedtls_ssl_set_hostname()` before starting the TLS handshake.

In rare cases, it is secure for a TLS client to accept arbitrary server names. See “[Are all TLS clients vulnerable if they don't call `mbedtls_ssl_set_hostname()`?](#are-all-tls-clients-vulnerable-if-they-dont-call-mbedtls_ssl_set_hostname)”. If you are sure that your application is only used in such scenarios, call `mbedtls_ssl_set_hostname(ssl, NULL)` to keep accepting arbitrary server names.

Note that `MBEDTLS_ERR_SSL_CERTIFICATE_VERIFICATION_WITHOUT_HOSTNAME` does not indicate that an attack is happening. It indicates that Mbed TLS has detected a situation where it would not be able to prevent an impersonation attack.

### I know my application is secure. Can I avoid changing it?

If you have a working application that does not call `mbedtls_ssl_set_hostname()`, and you are sure that this is secure (see See “[Are all TLS clients vulnerable if they don't call `mbedtls_ssl_set_hostname()`?](#are-all-tls-clients-vulnerable-if-they-dont-call-mbedtls_ssl_set_hostname)”), you can compile Mbed TLS 2.28.10, Mbed TLS 3.6.3 and later 3.6.x versions with the new compile-time option `MBEDTLS_SSL_CLI_ALLOW_WEAK_CERTIFICATE_VERIFICATION_WITHOUT_HOSTNAME`. This preserves the historical behavior.

## The background

### What is CVE-2025-27809?

CVE-2025-27809 is a vulnerability in some applications written against historical versions of Mbed TLS. Applications using Mbed TLS as an SSL or TLS clients should call `mbedtls_ssl_set_hostname()` to declare the expected name of the server. Otherwise, the server cannot be authenticated, so the TLS client is vulnerable to impersonation.

Historically, Mbed TLS did not require `mbedtls_ssl_set_hostname()` to be called. If no server host name was specified, every host name was accepted. This is an example of an insecure default weakness ([CWE-1188](https://cwe.mitre.org/data/definitions/1188.html)).

### How does the vulnerability work?

The security of the TLS protocol relies on clients authenticating the server.
If a TLS client fails to authenticate the server, a network-based attacker can act as a man-in-the-middle and impersonate the server to the client.

Server authentication relies on one of two mechanisms, depending on the key exchange mode: either a pre-shared key or a certificate chain. The vulnerability considered here affects certificate-based authentication.

Certificate-based authentication has three steps, all of which are necessary:

* The end certificate must be issued for the server that the client is trying to reach. Mbed TLS checks that the certificate content matches the name passed to `mbedtls_ssl_set_hostname()`.
* The certificate chain must be valid. Mbed TLS always checks this.
* The root of the certificate chain must be a trusted certificate authority (trusted CA). Certificate authentication will fail if no trusted CAs are defined.

Due to an insecure default in Mbed TLS up to 2.8.9 and Mbed TLS 3.x up to 3.6.2, if a TLS client application does not call `mbedtls_ssl_set_hostname()`, the first step is silently skipped. This allows any server with a certificate signed by a trusted CA to impersonate any other server.

### History

Belated thanks to Moti Avrahami and Daniel Stenberg for identifying the problem.

The vulnerability was identified in Curl by Moti Avrahami, disclosed as [CVE-2016-3739](https://curl.haxx.se/docs/adv_20160518.html). Daniel Stenberg [reported the issue to Mbed TLS](https://github.com/Mbed-TLS/mbedtls/issues/466), but unfortunately the Mbed TLS maintainers only noticed a functional limitation at the time, and not the deeper security issue. Renewed activity on the issue led the Mbed TLS maintainers to reexamine the problem and make Mbed TLS more robust.

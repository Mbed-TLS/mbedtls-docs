# A random generator fault can compromise TLS data integrity (CVE-2026-73064)

**Title** | A random generator fault can compromise TLS data integrity
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-73064
**Date** | 7th of July, 2026
**Affects** | All versions of Mbed TLS from 3.2.0 to 3.6.6; Mbed TLS 4.0.0; Mbed TLS 4.1.0
**Not affected** | Mbed TLS 3.6.7 and later 3.6.x versions; Mbed TLS 4.1.1 and later 4.1.x version; Mbed TLS 4.2.0 and later 4.x versions
**Impact** | TLS 1.3 application data integrity
**Severity** | LOW
**Credits** | Mohammad Seet (mhdsait101)

## Vulnerability

A logic error in `ssl_tls13_prepare_new_session_ticket()` causes it to return 1 rather than a negative error code if `psa_generate_random()` fails. On some platforms, an attacker with physical or local access may glitch the entropy source, which can cause `psa_generate_random()` to fail, depending on the random generator configuration.

The TLS library internally treats any nonzero value as an error, so for the most part, the impact is limited to returning the wrong error code for this error condition. However, applications may call `mbedtls_ssl_read()` or `mbedtls_ssl_write()` before the handshake is complete, in which case the functions will try to complete the handshake (and return `MBEDTLS_ERR_SSL_WANT_READ` or `MBEDTLS_ERR_SSL_WANT_WRITE`). If `ssl_tls13_prepare_new_session_ticket()` returns 1 due to the random generator failure, `mbedtls_ssl_read()` or `mbedtls_ssl_write()` returns 1, letting the application believe that one byte of application data has been read or written. With `mbedtls_ssl_read()`, the byte value that has seemingly been read is the previous content of the output buffer.

## Impact

Consider an application running a TLS server, that receives a TLS 1.3 connection. Suppose that an attacker can cause the platform's entropy source to fail.

If the application calls `mbedtls_ssl_read()` before the TLS handshake is over, the attacker can inject extra data before the actual data from the client. The attacker can control how many bytes are injected, but not the value of these bytes.

If the application calls `mbedtls_ssl_write()` before the TLS handshake is over, the attacker can cause some initial bytes not to be sent from the server.

## Affected versions

All versions of Mbed TLS 3.x from 3.2.0 to 3.6.6 are affected. Mbed TLS 4.0.0 and 4.1.0 are affected.

## Work-around

Applications are only affected if they call `mbedtls_ssl_read()` or `mbedtls_ssl_write()` before the initial TLS handshake is over.

The bug only affects TLS 1.3 servers. TLS 1.2 connections are not affected, and in particular renegotiation handshakes are not affected.

Applications are only affected if they issue TLS 1.3 session tickets. They only do so when `MBEDTLS_SSL_SESSION_TICKETS` is enabled (it is enabled by default) and the application has configured a ticket callback with `mbedtls_ssl_conf_session_tickets_cb()`. Furthermore tickets are not issued if the application has disabled them by calling `mbedtls_ssl_conf_new_session_tickets()` with a count of 0.

Applications are only affected if the random generator is configured to fail if the entropy source fails, which is the case by default, but can be avoided by setting the reseed interval to `INT_MAX`.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.7, Mbed TLS 4.1.1 or Mbed TLS 4.2.0 depending on which branch they are tracking.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | --------------------- |
| Basic fix | a5699bdb914ac6f65c867cf842911cdaa9d5618e | 465d6e9669a24ff7fe1a018fafe0e9f44aa4a48b | 465d6e9669a24ff7fe1a018fafe0e9f44aa4a48b |
| With tests and documentation | 77b1a22bc31d0017b07425bba61e5a4ecb82b9c5..8b7af9d421c62497f3a4e4a8be476b7fe8323c3f | 0fe989b6b514192783c469039edd325fd0989806..b05434c1b1df14cb3b2ce52dd1200c3ba9f9b198 | 0fe989b6b514192783c469039edd325fd0989806..b05434c1b1df14cb3b2ce52dd1200c3ba9f9b198 |

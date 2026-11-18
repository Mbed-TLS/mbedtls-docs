# TLS 1.2 server and client accept certificates using curves disallowed by the configured policy (CVE-2026-90471)

**Title** | TLS 1.2 server and client accept certificates using curves disallowed by the configured policy
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-90471
**Date** | 16 November 2026
**Affects** | Versions of Mbed TLS from 4.1.0 to 4.1.1; Mbed TLS version 4.2.0
**Not affected** | Mbed TLS 4.0.0 and earlier versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3 and later 4.x versions
**Impact** | TLS 1.2 server and client accept certificates using curves disallowed by the configured policy
**CWE** | CWE-295: Improper Certificate Validation
**CAPEC** | CAPEC-114: Authentication Abuse
**Severity** | LOW
**Credits** | Reported by jjfz123 on GitHub

## Vulnerability

A (D)TLS 1.2 server or client configured with `mbedtls_ssl_conf_groups()` to accept only
specific elliptic curves does not actually enforce that policy when validating certificates.

One real-world usecase where this might be encountered is using a TLS 1.2
handshake between the Mbed TLS server and client.

## Impact

The (D)TLS 1.2 server/client accepts secure curves supported by the
by the library, but disallowed via `mbedtls_ssl_conf_groups()`.

## Affected versions

Versions of Mbed TLS from 4.1.0 to 4.1.1 are affected.
Mbed TLS version 4.2.0 is affected.

## Work-around

Disabling the undesired curves in
`crypto_config.h` mitigates the issue.

Only servers and clients accepting (D)TLS 1.2 connections that have been configured to reject
curves otherwise supported by the configuration in `crypto_config.h`
via `mbedtls_ssl_conf_groups()` are affected.

## Resolution

Affected users should upgrade to Mbed TLS 4.1.2 or a later 4.1.x version,
or to Mbed TLS 4.3 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.1.x | TF-PSA-Crypto 1.x (x&gt;1) | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | ------------------- | -------------------------- | -------------- | --------------------- |
| Basic fix | N/A | N/A | N/A | a48935588a933b20076ca6e13244d31ab13709ad | c824263361e05fd95e8fde1772c036b708f81313 |
| With tests and documentation | N/A | N/A | N/A | a48935588a933b20076ca6e13244d31ab13709ad 7a9efa19b3f1a92444a779004428f5c3af5f574e^..22498abec16029ce50eda69f25bdee51ceb5e914 | c824263361e05fd95e8fde1772c036b708f81313 c828cfb8672a276a192b1959289ac0c3704647af^..a2945a5c7084fc198700abd0c7bee5584adf184b |

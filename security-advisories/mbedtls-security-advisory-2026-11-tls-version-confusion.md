# TLS client completes a TLS 1.3 handshake without secret keying material (CVE-2026-115490)

**Title** | TLS client completes a TLS 1.3 handshake without secret keying material
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-115490
**Date** | 16th of November 2026
**Affects** | All versions of Mbed TLS from 3.2.0 up to 3.6.7; all versions of Mbed TLS from 4.0.0 to 4.1.1; Mbed TLS 4.2.0
**Not affected** | Mbed TLS 3.1.0 and earlier; Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3 and later 4.x versions
**Impact** | Loss of TLS confidentiality and integrity; conditional server impersonation
**CWE** | CWE-290: Authentication Bypass by Spoofing; CWE-1288: Improper Validation of Consistency within Input
**CAPEC** | CAPEC-272: Protocol Manipulation
**Severity** | HIGH
**Credits** | Claude (Anthropic) and Ada Logics

## Vulnerability

During a fresh handshake that offers TLS 1.2 and TLS 1.3, a malicious server can reply with a ServerHello that omits the TLS 1.3 supported_versions extension, sets legacy_version to 0x0304, and selects a configured TLS 1.3 ciphersuite. TLS 1.3 ServerHello preprocessing interprets the missing extension as a TLS 1.2 fallback and passes the message to the TLS 1.2 ServerHello parser, which overwrites ssl->tls_version with legacy_version and accepts 0x0304 because it validates the value against the client’s global configured version range rather than requiring TLS 1.2 for the ServerHello being processed.

The same inconsistent transition is possible during a TLS 1.2 resumption attempt when the client’s global configuration permits both TLS 1.2 and TLS 1.3. Although Mbed TLS pins this particular attempt to TLS 1.2, the TLS 1.2 parser uses the broader configured range, accepts 0x0304 and a configured TLS 1.3 ciphersuite that was not offered in this attempt, abandons resumption, and advances to a full handshake.

A connection started with a TLS 1.3 session selected for resumption is not affected. Mbed TLS pins the minimum version for that connection to TLS 1.3, so a ServerHello without supported_versions is rejected before the TLS 1.2 ServerHello parser is reached.

After the faulty transition, handshake dispatch follows ssl->tls_version and enters the TLS 1.3 state machine in SERVER_CERTIFICATE. TLS 1.3 ServerHello post-processing and key-schedule initialization have not occurred: neither a configured PSK nor an ephemeral shared secret has contributed to the session keys. The key-exchange mode is unset, and the handshake and master secrets are initialized to zero.

### Affected configurations

The zero-key handshake can complete on a fresh handshake or a TLS 1.2 resumption attempt when:

- `MBEDTLS_SSL_PROTO_TLS1_2`, `MBEDTLS_SSL_PROTO_TLS1_3`, and `MBEDTLS_SSL_TLS1_3_KEY_EXCHANGE_MODE_EPHEMERAL_ENABLED` are enabled at build time;
- the client’s runtime configuration permits both TLS 1.2 and TLS 1.3 and includes a TLS 1.3 ciphersuite that the attacker can select.

Both the build-time and runtime prerequisites are met by the default Mbed TLS configuration.

TLS-1.2-only, TLS-1.3-only, and TLS 1.3 builds that do not contain the certificate/ephemeral mode cannot go through the attack path.

## Impact

Exploiting the vulnerability requires a malicious server or an active on-path attacker to send the malformed ServerHello and complete the server side of the handshake. An active attacker cannot use this vulnerability to tamper with a connection in progress with a server. A passive observer between a server and the vulnerable client gains no advantage.

Once the attacker triggers the faulty handshake, the client reports a completed TLS 1.3 connection even though neither a configured PSK nor an ephemeral shared secret contributes to the key schedule. The session's traffic keys, exporter master secret, and resumption master secret are derived from all-zero secret input and the public transcript, so any party that records the handshake can calculate them. A passive observer can then decrypt application traffic, and an active observer capable of injecting records can forge traffic accepted by the client.

An intended, authenticated server already sees and controls the connection's plaintext. If it triggers the vulnerability, the additional exposure is principally to independent or colluding network observers.

More critically, the unexpected switch to TLS 1.3 certificate authentication may bypass the server authentication mechanism that the client intended for the connection, as detailed below.

### Server impersonation

Under the affected configurations described above, the vulnerability can be exploited during either of the following:

- a fresh handshake that offers both TLS 1.2 and TLS 1.3;
- a TLS 1.2 session resumption attempt when the client's broader configuration also permits TLS 1.3.

For a fresh handshake that proposes certificate authentication, potentially alongside other authentication mechanisms, the vulnerability does not allow an active attacker to bypass the checks associated with the Certificate and CertificateVerify handshake messages. With certificate verification correctly configured for the targeted server, they therefore still need the private key for a certificate accepted for that server identity. Server impersonation is not possible in this case unless they already possess such a private key.

For fresh handshakes that do not propose certificate authentication, and for TLS 1.2 resumption attempts, the faulty transition may bypass the expected proof of a secret. TLS 1.2 PSK and ECJPAKE handshakes and TLS 1.3 configurations restricted to the runtime key-exchange modes `MBEDTLS_SSL_TLS1_3_KEY_EXCHANGE_MODE_PSK` and/or `MBEDTLS_SSL_TLS1_3_KEY_EXCHANGE_MODE_PSK_EPHEMERAL` require proof of a pre-shared secret. A TLS 1.2 resumption handshake similarly requires proof of the existing session secret. The faulty transition skips that proof and enters the certificate path. An active attacker that does not know the required secret can therefore impersonate the server if they can complete the unexpected certificate-authentication path.

In these cases, certificate verification may be unconfigured or only partially configured because the client application does not expect certificate authentication to be used. This allows server impersonation when the unexpected certificate path accepts credentials that do not authenticate the targeted server, notably:

- With the client's certificate-verification mode (`authmode`) set to `MBEDTLS_SSL_VERIFY_NONE`, the active attacker can use their own parseable, compatible certificate and corresponding private key.

- With `MBEDTLS_SSL_VERIFY_OPTIONAL`, the same is possible unless the client application rejects the verification flags reported through `mbedtls_ssl_get_verify_result()` or a custom certificate-verification callback returns a fatal error.

- With `MBEDTLS_SSL_VERIFY_REQUIRED` and a configured trust source (a CA chain or trusted-certificate callback), impersonation may be possible if hostname verification is disabled and the active attacker possesses a certificate and private key for another server authorized by that trust source, or if a custom certificate-verification callback weakens verification sufficiently to accept their certificate.

Note that with untouched runtime defaults (MBEDTLS_SSL_VERIFY_REQUIRED and no configured trust source), an active attacker cannot complete the malformed handshake.

## Affected versions

The vulnerable TLS 1.2/TLS 1.3 switching logic was introduced in Mbed TLS 3.2.0.
The versions of Mbed TLS from 3.2.0 up to 3.6.7 are affected.
The versions of Mbed TLS from 4.0.0 up to 4.1.1 are affected.
The 4.2.0 version of Mbed TLS is affected.

## Work-around

Until an update containing the fix is available, configure each client connection to permit only TLS 1.2 or only TLS 1.3. Correctly configuring `MBEDTLS_SSL_VERIFY_REQUIRED`, a trust source, and an expected hostname prevents server impersonation, but it does not restore confidentiality or integrity against an intended authenticated server that triggers the faulty transition or independent parties that receive the handshake transcript.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version, Mbed TLS 4.1.2 or a later 4.1.x version, Mbed TLS 4.3.0, or a later maintained release containing the fix.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS development |
| ------ | -------------- | -------------- | --------------------- |
| Basic fix | 2ef67e4bb03d1ae7bb94a835fd1c8898c1ec7994^..c32c47a824c074d25ff77b6955f4c13452e7f15d | ff52b208fe85cccc6ab5820aece68fca07310c2d^..d5a52ce0f2bc31dc1c92ddab8cf255b1d9d7121d | 77163771c7f03f4f6a9ffacc3110c12acbf2e441^..c03566992ed6f0ea799f670ad7a0aebf19e2d674 |
| With tests | c5a9caca0fb79dadea57d0a734d6298ae6b92c28^..5b4775e3aa3bd2e151d5f2d44de46adad8485df5 | eb5835c94bfaff27d4e7e24afeb898670697c46e^..f969949f1f094d6981a560a4b28a87ac921bb160 | 707c20f0bdc8cb925399a7f56ac4ddf52a385b6f^..670963870cd6a2cc40be333a51a0dcc529b47c0a |

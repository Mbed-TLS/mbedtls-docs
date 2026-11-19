# TLS 1.3 HRR can bypass SNI-based client authentication (CVE-2026-116375)

**Title** | TLS 1.3 HRR can bypass SNI-based client authentication
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-116375
**Date** | 16th of November 2026
**Affects** | Mbed TLS 3.0.0 through 3.6.7; Mbed TLS 4.0.0 through 4.1.1; Mbed TLS 4.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later versions
**Impact** | A TLS 1.3 server may accept a client without the certificate required for the requested host
**CWE** | CWE-303: Incorrect Implementation of Authentication Algorithm
**CAPEC** | CAPEC-272: Protocol Manipulation
**Severity** | HIGH
**Credits** | saikumar279, Duong Gia Huy and Giovanni Mancino

## Vulnerability

When a TLS 1.3 server uses an SNI callback to set per-host client-authentication
requirements, state from the first ClientHello could persist after a
HelloRetryRequest. A client could change or omit SNI in the second ClientHello
and retain a less restrictive authentication mode. This affects servers that
use the SNI callback to select different client-authentication policies.

## Impact

An attacker may complete a TLS connection to a host that requires client
authentication without presenting a valid client certificate. The resulting
access depends on how the application routes and authorizes connections.

## Affected versions

All versions of Mbed TLS from 3.0.0 to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0 to 4.1.1 are affected.
Mbed TLS 4.2.0 is affected.

## Work-around

Until upgrading, disable TLS 1.3 on servers that use SNI callbacks to set
per-host client-authentication modes. Servers using one uniform
client-authentication mode are not affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version,
Mbed TLS 4.1.2 or a later 4.1.x version, or Mbed TLS 4.3.0 or a later version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if
you are maintaining a branch with backported bug fixes, here are the most
relevant commits. Please note that these commits may not apply cleanly to
older versions of the library, and may not provide a complete fix even if they
do apply. The Mbed TLS development team does not provide support outside of
maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | --------------------- |
| Basic fix | c6b3ffd8d17b77be62d872d93c0341196d433a02, f83d748d4d01e7d7250c8295ba5f061b05ceae4a, 9974878acc1fc2281e3a191a17e5b21a369bde1f, e7d68f26bc92835d13f210936fc579a55b150f9b, 7e8dffdc1a7b80224f6bb43a376a153077265e53, 091279d81f12a8f989029844d9d7d713f45d2521 | 68288c75d77652336f78ba24644630bae73e11e2, bb90aafdc9d94b3cc8045021013ed91d51ede9ab, 7cdab72fbf034bac31040c0b0e9dd26fbf6a854a, fd60895dddba9828f4ee99d4bc2a25942f8c784a, e361e51827d5e299d5b31aea77efc110fa25356c | 18f75e0c4ae29def941b922b0d007954d89c462b, c2c2bc3d6fd255707e990df734a4348be8b5deda, 1504890606655a8e82a268420216e5924c65e004, 77b83a0ac3f6b12f314d431be3c2d7f23e4a3f56, 0c23a42c4e0944642f6aeefa26604ad23075ecbe |
| With tests and documentation | b98eac00dcfb13048948121c8573a9635bdc398b..ab85695f9cf82790219ee45ac12091d55d3d9ebb | 228aee212ea584a7942c8dcb3ef7d691b6fa2b46..a405ef78fb5cdc90403d59b85f96cd05c6d96020 | 4237f71d337db2580fe472d01391510d8b988450..5fe685fe3eb9246ee5ca7877c7956bccd86b2c0c |

# TLS 1.3 early data integrity failure due to buffered plaintext across key change (CVE-2026-73096)

**Title** | TLS 1.3 early data integrity failure due to buffered plaintext across key change
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-73096
**Date** | 7th of July, 2026
**Affects** | Mbed TLS 3.6.0 to 3.6.6; Mbed TLS 4.0.0 to 4.1.0
**Not affected** | All versions before Mbed TLS 3.6.0; Mbed TLS 3.6.7 and later 3.6.x versions; Mbed TLS 4.1.1 and later 4.1.x versions; Mbed TLS 4.2.0 and later 4.x versions
**Impact** | A network attacker capable of modifying traffic between a TLS 1.3 client and server can cause accepted TLS 1.3 early data to be silently discarded while the handshake completes successfully. |
**Severity** | MEDIUM
**Credits** | Ben Smyth, https://bensmyth.com

## Vulnerability

TLS 1.3 requires handshake messages immediately preceding a key change to align with record boundaries. In affected versions, Mbed TLS may retain and subsequently process trailing bytes that follow a ClientHello message within the same TLS record.

An attacker capable of modifying traffic between a TLS 1.3 client and server can exploit this behavior by appending a forged `EndOfEarlyData` message to a ClientHello record and suppressing the client's genuine early-data records. The server may process the forged message, transition to handshake traffic keys, and complete the TLS handshake successfully.

As a result, TLS 1.3 early data (0-RTT) sent by the client can be silently discarded while both endpoints complete the handshake and report successful establishment of the connection.

The attack requires:

* TLS 1.3 to be enabled.
* Server-side support for TLS 1.3 early data (0-RTT).
* An attacker capable of modifying traffic between the client and server.

## Impact

A successful attack can cause 0-RTT application data sent by the client to be silently discarded while the TLS handshake succeeds and the client receives an indication that the early data was accepted.

Applications relying on TLS 1.3 early data for latency-sensitive operations may incorrectly assume that requests or commands were processed when they were never delivered to the server.

The vulnerability affects the integrity of early-data delivery. It does not enable disclosure of encrypted early data or modification of authenticated post-handshake application data.

## Affected versions
Mbed TLS 3.6.0 to 3.6.6 included; Mbed TLS 4.0.0 to 4.1.0 included.

## Work-around

Users can mitigate the issue by:

* Not enabling TLS 1.3 early data (`MBEDTLS_SSL_EARLY_DATA`), disabled by default.
* Avoiding application reliance on successful delivery of 0-RTT data until an updated release is deployed.

Applications that do not enable TLS 1.3 early data are not vulnerable to the reported integrity impact.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.7 or a later 3.6.x version,
or to Mbed TLS 4.1.1 or a later 4.1.x version, or to Mbed TLS 4.2 or a later
4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | -------------- | --------------------- |
| Basic fix (5 commits)| 27c489be620005ae5ba935b1cc717ca6636efa79 835ffb3a7c75e5d44df2608b42c7b5b0c6bbfbfb 8f1e330f20f9abcea9547c8dc113a8695571f9e5 b71ec46f4f129cc583cffc791ba9a55a8a22b8e3 26eb6a36cf4e753a6550b75bbf566a936b6139f2 | f17c5ff90d625f6b793acf97c2d9ee0b811a483c 7dc69f331fb19246b1b463feea97d79f709b6342 1235722aa12df370f057540270d99f112b038e8f 0fe502312d2fb2664985886db19693557de7e669 45d892ea3d69d2996937503e269c2ec04a2e7557 | 3861588b47d045afcc66d9ba8b73b8217e87d2ce 0c9d3d4a0fb50216993d4142335a2888929bcd72 6c557a70f6a2992282e5a342714be4c89130b8f4 74b9ab200820537b8f5cf8e55bd4f42d912a4c78 b188f399f926af64d06fdb842cbbceed2209f6a8 |
| With tests and documentation | 46069c6127b75ba786c9001d5a8ad84f82d27576..26eb6a36cf4e753a6550b75bbf566a936b6139f2 | 5aac408d2a5dbb25357cd5ac49b60e9c18f54ab9..45d892ea3d69d2996937503e269c2ec04a2e7557 | f74ef9b3ab885d9956b37ffd95065779563c69ca..b188f399f926af64d06fdb842cbbceed2209f6a8 |

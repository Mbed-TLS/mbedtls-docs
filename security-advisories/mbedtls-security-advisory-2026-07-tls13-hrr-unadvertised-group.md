# TLS 1.3 client accepts HelloRetryRequest selecting an unadvertised group (CVE-2026-25832)

**Title** | TLS 1.3 client accepts HelloRetryRequest selecting an unadvertised group
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-25832
**Date** | 7th of July, 2026
**Affects** | Mbed TLS 3.5.0 through 3.6.6, all Mbed TLS 4 versions up to 4.1.0
**Not affected** | all versions up to and including 3.4.1, Mbed TLS 3.6.7 and later, and Mbed TLS 4.1.1 and later.
**Impact** | TLS 1.3 client group policy bypass; Limited denial of service in some configurations
**Severity** | LOW
**Credits** | Din Asotic / Xiangdong Li, Beijing University of Posts and Telecommunications (BUPT) / Bin Luo, University of Electronic Science and Technology of China (UESTC)

## Vulnerability

When an Mbed TLS client processes a TLS 1.3 HelloRetryRequest, it is required to check that the `selected_group` in the server's `key_share` extension was present in the `supported_groups` extension of the original ClientHello. If this check fails, RFC 8446 requires the client to abort the handshake with an `illegal_parameter` alert.

Affected versions did not correctly perform this validation.

A misbehaving server could use HelloRetryRequest to nudge the client into bypassing its security policy by selecting a cryptographic group that the client did not advertise.

## Impact

The impact is low: a malicious/misbehaving server can bypass a TLS 1.3 client's configured group policy, or cause handshake failure when selecting an unacceptable group. This does not by itself compromise session keys or certificates.

## Affected versions

All Mbed TLS 3.5 versions, all 3.6 versions up to 3.6.6,  all Mbed TLS 4 versions up to 4.1.0.

Applications are affected when all of the following are true:

* TLS 1.3 client support is enabled.
* A TLS 1.3 ephemeral or PSK-ephemeral key exchange mode is enabled.
* The application relies on `mbedtls_ssl_conf_groups()` or equivalent configuration to restrict the groups that the client may offer.
* The client connects to a malicious or compromised server that sends a HelloRetryRequest selecting a group outside the client's originally advertised `supported_groups` list.

## Work-around

Where upgrading is not immediately possible, applications can avoid exposure by disabling TLS 1.3 client connections, or by only connecting TLS 1.3 clients to trusted servers that cannot send malicious HelloRetryRequest messages.

Applications are not affected if they do not enable TLS 1.3 client support, use TLS 1.3 PSK-only key exchange, or do not rely on the TLS 1.3 supported group list as a security or compliance boundary.

## Resolution

Affected users of the 3.6 LTS branch should upgrade to 3.6.7 or later. Affected users of the 4.x series should upgrade to 4.1.1 or later.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.1.x | TF-PSA-Crypto 1.x (x&gt;1) | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | ------------------- | -------------------------- | -------------- | --------------------- |
| Basic fix | 55ccd932658b933f224cc0384ab5a5197e5680e2 | Not applicable  | Not applicable  | cec2cef6b5ce9ae3cb2bbcd43f3ac8c06f1f9508 | 902762039334c91813ab9e9ba8ccef5356e819e4 |
| With tests and documentation | aecc26ac7c..8c458b8cca4c4a55142efd65348e93595ec71723 | Not applicable  | Not applicable  | b2e36d7d7a..e16f0e0b014be310f423de5e52109cd0712db6f7 | cb4d172ce0..e2a6f05640528b1eff715824f3d931b81e7c911d |

# Unbounded iteration count in PKCS5/PKCS12 (CVE-2026-50582)

**Title** | Unbounded iteration count in PKCS5/PKCS12
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-50582
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; all versions of TF-PSA-Crypto 1.1.x up to 1.1.1; TF-PSA-Crypto 1.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; TF-PSA-Crypto 1.1.2 and later 1.1.x versions; TF-PSA-Crypto 1.3.0 and later versions
**Impact** | Denial of service (DoS) when parsing a PKCS#8 encrypted private key
**CWE** | CWE-834: Excessive Iteration
**CAPEC** | CAPEC-153: Input Data Manipulation
**Severity** | LOW
**Credits** | jiliang; Tanish Saxena ("Logic26"); Hila Cohen (https://github.com/hillalee)

## Vulnerability

When parsing a PKCS#8 encrypted private key using PBES2, the PBKDF2 iteration count is read from the key material and used without any upper bound. An attacker can craft a key with an iteration count up to `INT_MAX` (about 2^31). Since the key derivation runs before the password is checked, the attacker does not need to know the password.

Applications are vulnerable if they call `mbedtls_pk_parse_key()` (or `mbedtls_pk_parse_keyfile()`) with a non-empty password on key data that may come from an untrusted source. In Mbed TLS 3.6, applications that call `mbedtls_pkcs5_pbes2_ext()` directly on untrusted parameters are also affected.

## Impact

The key derivation can take minutes on desktop-class hardware and hours or more on constrained devices, blocking the calling thread.

## Affected versions

The issue first appeared in release `polarssl-1.3.0` which means that the following versions are affected:
- All versions of Mbed TLS up to 3.6.7 (LTS).
- All versions of TF-PSA-Crypto 1.1.x up to 1.1.1 (LTS);
- TF-PSA-Crypto 1.2.0.

## Work-around

Applications can parse the PBES2 parameters of untrusted encrypted keys themselves and reject those with an excessive iteration count before calling the library.

Applications that only parse unencrypted keys, never pass a password, or only parse keys from trusted sources are not affected.

## Resolution

Affected users should upgrade to:
- Mbed TLS 3.6.8 (LTS);
- TF-PSA-Crypto 1.1.2 (LTS);
- TF-PSA-Crypto 1.3.0.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.1.x | TF-PSA-Crypto 1.x (x&gt;1) |
| ------ | -------------- | ------------------- | -------------------------- |
| Basic fix | a14f7732e03493262b6829a2753b7fd20a3e3a28 | f47ccf50424aa5d4bae4e52aee755ff1eedf56d0 | 4fd8e58e7db6295275efa3239726331c04890ab3 |
| With tests and documentation | 122c3e49445dfb47c5fe72d4075bbb03bfafe76d^..a8d7eed7fb115cff9bada4679b1b591e0cd5045e | dff42f9c82f89298365ecdb638605b8a027347cd^..f62a3224c1e6b674bb7d87fa86ca6f8220d88b44 | e2b462ed50dd14ba38706528a741ecab8deda723^..7a9451ca6e30ec899ce15029fbe11b05cdb33995 |

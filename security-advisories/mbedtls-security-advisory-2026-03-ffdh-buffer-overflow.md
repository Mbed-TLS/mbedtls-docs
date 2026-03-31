# Buffer overflow in FFDH public key export (CVE-2026-34875)

**Title** | Buffer overflow in FFDH public key export
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-34875
**Date** | 31 March 2026
**Affects** | All versions of Mbed TLS from 3.5.0 up to 3.6.5, TF-PSA-Crypto 1.0.0
**Not affected** | Mbed TLS 3.6.6 and later 3.6 versions, TF-PSA-Crypto 1.1.0 and later versions
**Impact** | Memory corruption
**Severity** | HIGH
**Credits** | Haruto Kimura (Stella)

## Vulnerability

When exporting FFDH public keys, the function `psa_export_public_key()` does not properly check the size of the user-supplied output buffer to ensure that it is large enough to contain the public key. If the caller supplies an output buffer that is smaller than the length of the public key, the whole key will still be written, overflowing the buffer.

## Impact

The buffer overflow causes memory corruption which may allow arbitrary code execution by an attacker who can cause the application to export an arbitrary FFDH key.

## Affected versions

All versions of Mbed TLS from 3.5.0 up to 3.6.5 and TF-PSA-Crypto 1.0.0 are affected.

## Work-around

When calling `psa_export_public_key()` for FFDH keys, ensure that the output buffer is always at least as large as size of the exported key. The output buffer size required may be determined using one of the following macros:
* `PSA_EXPORT_PUBLIC_KEY_OUTPUT_SIZE()` ([documented here](https://arm-software.github.io/psa-api/crypto/1.0/api/keys/management.html#c.PSA_EXPORT_PUBLIC_KEY_OUTPUT_SIZE)), if the key type and bit length are available.
* `PSA_EXPORT_PUBLIC_KEY_MAX_SIZE` ([documented here](https://arm-software.github.io/psa-api/crypto/1.0/api/keys/management.html#c.PSA_EXPORT_PUBLIC_KEY_MAX_SIZE)) otherwise.

Applications exporting public keys for algorithms other than FFDH are unaffected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.6 or TF-PSA-Crypto 1.1.0

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.x | Mbed TLS 4.x |
| ------ | -------------- | ----------------- | ------------ |
| Basic fix | 01bcc1f75457b7089a796f222abc28c62c3f2ef8 | a235a62633f2e3125d62577216abd0db16849c48 | N/A |
| With tests and documentation | branch up to 01b04ab723b7fa3cdaae26fd8770db5e5ba5d260 | branch up to 1d9b4ad314a8d1a91778fd7a89aebc155805c714 | N/A |

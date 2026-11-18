# Spectre-PHT side channel in the cipher module (CVE-2026-93833)

**Title** | Spectre-PHT side channel in the cipher module
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-93833
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; all versions of Mbed TLS from 4.0.0 to 4.1.1; Mbed TLS 4.2.0; all versions of TF-PSA-Crypto up to 1.1.1; TF-PSA-Crypto 1.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later versions; TF-PSA-Crypto 1.1.2 and later 1.1.x versions; TF-PSA-Crypto 1.3.0 and later versions
**Impact** | Partial key leakage to powerful local attackers
**CWE** | CWE-208: Observable Timing Discrepancy
**CAPEC** | CAPEC-663: Exploitation of Transient Instruction Execution
**Severity** | MEDIUM
**Credits** | Oleksii Oleksenko (Azure Research, Microsoft) and Alvise de Faveri Tron (Vrije Universiteit Amsterdam)

## Vulnerability

In the cipher module, the type `mbedtls_cipher_context_t` has a field `cipher_ctx` which points to a different data type depending on the mode. For CCM (including unauthenticated CCM\*) and GCM, `cipher_ctx` points to a CCM or GCM context which itself contains a pointer to the context for the underlying block permutation (AES, ARIA or Camellia). For other moduesl `cipher_ctx` directly points to the underlying block permutation or other low-level context.

The functions `mbedtls_cipher_set_iv()` and `mbedtls_cipher_update()` have a branch that contains special handling for unauthenticated CCM\*. When this code is executed, an attacker who can observe precise memory access patterns may be able to obtain part of the data behind the `cipher_ctx` pointer. For CCM, this is harmless, because the data in question is not sensitive. But if the branch is wrongly executed speculatively when the cipher mode is not CCM or GCM, the leaked data is part of the expanded key.

This is an instance of a Spectre v1 (Spectre-PHT) speculative-execution side channel attack.

In Mbed TLS 3.6 and earlier versions, a similar data misinterpretation happens if branch misprediction causes a legacy context to be interpreted as a PSA context, or a legacy non-KW context to be interpreted as a NIST KW context.

## Impact

On platforms with speculative execution, when unauthenticated CCM\* is enabled, a powerful local attacker (for example, a normal world operating system attacking a secure enclave) may recover part of the key of a cipher operation.

With the PSA API, this impact unauthenticated ciphers.

In Mbed TLS 3.6, with the `cipher.h` API, this also impacts authenticated ciphers.

## Affected versions

All versions of TF-PSA-Crypto up to 1.1.1 are affected.
TF-PSA-Crypto 1.2.0 is affected.

All versions of Mbed TLS up to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0 to 4.1.1 are affected.
Mbed TLS from 4.2.0 is affected.

## Work-around

Since TF-PSA-Crypto 1.0.0, applications are not affected if the library is compiled without support for unauthenticated CCM\*, i.e. if `PSA_WANT_ALG_CCM_STAR_NO_TAG` is disabled. Applications are also not affected if `PSA_WANT_ALG_CCM` is enabled, but all cipher support is provided by drivers and built-in CCM is disabled.

In Mbed TLS 3.6, to avoid the vulnerability, all of the following must be disabled:

* CCM support: `PSA_WANT_ALG_CCM_STAR_NO_TAG`, `PSA_WANT_ALG_CCM` and `MBEDTLS_CCM_C`.
* NIST KW support: `MBEDTLS_NIST_KW_C`.
* PSA context support in `cipher.h`: `MBEDTLS_USE_PSA_CRYPTO`. (However, `MBEDTLS_USE_PSA_CRYPTO` can safely be enabled if `MBEDTLS_DEPRECATED_REMOVED` is also enabled.)

## Resolution

Affected users should upgrade to TF-PSA-Crypto 1.1.2 or a later 1.1.x version,
or to TF-PSA-Crypto 1.3.0 or a later 1.x version.

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version,
or to Mbed TLS 4.1.2 or a later 4.1.x version,
or to Mbed TLS 4.3.0 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.1.x | TF-PSA-Crypto 1.x (x&gt;1) | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | ------------------- | -------------------------- | -------------- | --------------------- |
| Basic fix | 5cc12852d5640c2f02b25f0a44136445a143e0c8 5c7250131cbbe1c526f494cb23b3be851714fc17 82bafdba2370eac2267f711b94249f0913c5abff 4cec3c8b4288ec007aa963d803f62deb0fd69a54 6a23d269be69d995a34780d38931090cd47b3972 7521b1084fc6b218219ba3faedb37b6e6b5b0063 | de81da9a1c24c1ac2ad1eadd6710cbf558d1c1bb 3e2a477d51cc871128e4aa1435a936192ff74a17 8a826d9d00c5f85b98e688232f373944e0ae7274 | 7380b26aa763a54b363fb5c4d145ad9bc7d88375 9ac4508debb64da281b4d68d8e5f77f959b54c87 5d21a518ff7e66b1590fa700f1aa61ae3b75640a | N/A | N/A |
| With CVE-2026-115493 | 5cc12852d5640c2f02b25f0a44136445a143e0c8^..9049805bb3bd2de64020e8629a5acad0bee2bedf | de81da9a1c24c1ac2ad1eadd6710cbf558d1c1bb^..65fcb5684018f581d9ae3b972b52ba66f4c44595 | 7380b26aa763a54b363fb5c4d145ad9bc7d88375^..728175f34f6353b5ebb7bcea99a0fd819277eabc | N/A | N/A |

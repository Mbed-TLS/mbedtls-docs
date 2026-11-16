# Spectre-PHT bypass of hardware AES and GCM (CVE-2026-115493)

**Title** | Spectre-PHT bypass of hardware AES and GCM
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-115493
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; all versions of Mbed TLS from 4.0.0 to 4.1.1; Mbed TLS 4.2.0; all versions of TF-PSA-Crypto up to 1.1.1; TF-PSA-Crypto 1.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later versions; TF-PSA-Crypto 1.1.2 and later 1.1.x versions; TF-PSA-Crypto 1.3.0 and later versions
**Impact** | Key or plaintext leakage to powerful local attackers
**CWE** | CWE-208: Observable Timing Discrepancy
**CAPEC** | CAPEC-663: Exploitation of Transient Instruction Execution
**Severity** | MEDIUM

## Vulnerability

On platforms where AESNI or AESCE is supported, by default, TF-PSA-Crypto and Mbed TLS try a hardware-assisted implementation of AES and GCM, and fall back to a pure software implementation if the hardware is not available. The hardware-assisted implementation is resistant to timing attacks, but the pure software implementation is not, because it performs table lookups at an offset that is derived from the key. This can leak key material to a powerful local attacker through a cache timing attack.

If the branch to the pure software implementation is wrongly taken speculatively, the processor may start to execute the leaky table lookups, even if a constant-time implementation is available and is ultimately used.

This is an instance of a Spectre v1 (Spectre-PHT) speculative-execution side channel attack.

## Impact

On platforms with speculative execution, when both AESNI/AESCE and the software fallback are enabled, a powerful local attacker (for example, a normal world operating system attacking a secure enclave) may recover AES keys and GCM keys.

## Affected versions

All versions of TF-PSA-Crypto up to 1.1.1 are affected.
TF-PSA-Crypto 1.2.0 is affected.

All versions of Mbed TLS up to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0 to 4.1.1 are affected.
Mbed TLS from 4.2.0 is affected.

## Work-around

Applications using AES are not affected if the pure software implementation is disabled, i.e. if `MBEDTLS_AES_USE_HARDWARE_ONLY` is enabled. Note that GCM remains affected.

Applications are not affected if built-in support for AES and GCM are disabled, and AES and GCM are provided through third-party PSA drivers.

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
| Basic fix           | 5cc12852d5640c2f02b25f0a44136445a143e0c8 f68e54e48996335e5a4b76a057e53476c259f0c7 ce4836cc688aaae9a0cccb3dfc1c62129a405858 ea9b696b3e4e8f207715e164207ba5ec45e1f741 26786aad1be2c818d00bdae9a21c2a41349e9a23 9049805bb3bd2de64020e8629a5acad0bee2bedf c3b3bff6e2728ad810948dd85626c287dd218f3e 9a498d0761fd3203570911fde427ba28f596af3e | de81da9a1c24c1ac2ad1eadd6710cbf558d1c1bb 90f82a38b5f09bfc60987dd6e021877f90387b6f 8412445f9bce8f89d40e92a2b6de3f4323d1edff 48c53f22d42c7b703d4867edc88cd9c74e52782b 65fcb5684018f581d9ae3b972b52ba66f4c44595 5c0fc677dd23fee05e13d4717051e4ce3ef6a087 5088d900056bd63b997aa7fd6763b6240eb28aa9 | 7380b26aa763a54b363fb5c4d145ad9bc7d88375 39820dff268738a498e39bdba3add9949126c370 e6405a261d82c7599162a0dacab982701182e86b 1496b3cab0f44988f758743568ecbb75aab9e80e 728175f34f6353b5ebb7bcea99a0fd819277eabc 09bf4b6bc5b7012283efd6648aec60d4a5831fb6 5bdd5c1e8781978c954648c14cd17b48093daa04 | N/A | N/A |
| With CVE-2026-93833 | 5cc12852d5640c2f02b25f0a44136445a143e0c8^..9049805bb3bd2de64020e8629a5acad0bee2bedf c3b3bff6e2728ad810948dd85626c287dd218f3e 9a498d0761fd3203570911fde427ba28f596af3e | de81da9a1c24c1ac2ad1eadd6710cbf558d1c1bb^..65fcb5684018f581d9ae3b972b52ba66f4c44595 5c0fc677dd23fee05e13d4717051e4ce3ef6a087 5088d900056bd63b997aa7fd6763b6240eb28aa9 | 7380b26aa763a54b363fb5c4d145ad9bc7d88375^..728175f34f6353b5ebb7bcea99a0fd819277eabc 09bf4b6bc5b7012283efd6648aec60d4a5831fb6 5bdd5c1e8781978c954648c14cd17b48093daa04 | N/A | N/A |

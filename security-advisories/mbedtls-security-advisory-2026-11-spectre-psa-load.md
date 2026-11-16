# Spectre-PHT side channel in PSA ECC operations (CVE-2026-93842)

**Title** | Spectre-PHT side channel in PSA ECC operations
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-93842
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; all versions of Mbed TLS from 4.0.0 to 4.1.1; Mbed TLS 4.2.0; all versions of TF-PSA-Crypto up to 1.1.1; TF-PSA-Crypto 1.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later versions; TF-PSA-Crypto 1.1.2 and later 1.1.x versions; TF-PSA-Crypto 1.3.0 and later versions
**Impact** | Partial key leakage to powerful local attackers
**CWE** | CWE-208: Observable Timing Discrepancy
**CAPEC** | CAPEC-663: Exploitation of Transient Instruction Execution
**Severity** | LOW
**Credits** | Oleksii Oleksenko (Azure Research, Microsoft) and Alvise de Faveri Tron (Vrije Universiteit Amsterdam)

## Vulnerability

When a PSA function calls the built-in ECC code to perform an operation, it calls the auxiliary function `mbedtls_psa_ecp_load_representation()` to parse the key from the PSA export format to an internal data structure. This function has a branch for public keys and a branch for private keys. The private-key path is protected against timing side channels thanks to a combination of constant-time operations and blinding. The public-key path is not protected.

On platforms with speculative execution, if the private/public branch is mispredicted and the public-key code runs speculatively on what is actually private key data, the execution timing reveals some information about the private key, which is mostly restricted to the first byte of the representation. This is an instance of a Spectre v1 (Spectre-PHT) speculative-execution side channel attack.

## Impact

On platforms with speculative execution, a powerful local attacker (for example, a normal world operating system attacking a secure enclave) may recover partial information about a private key.

## Affected versions

All versions of TF-PSA-Crypto up to 1.1.1 are affected.
TF-PSA-Crypto 1.2.0 is affected.

All versions of Mbed TLS up to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0 to 4.1.1 are affected.
Mbed TLS from 4.2.0 is affected.

## Work-around

There is no workaround.

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
| Basic fix | 2d281b0a767da15102933272e0f147763a720e74 | 2ddc5a6517070e066c383aadc316b3b8b1c1cece | 535bcfc3c8c203477cc645e6fecf82c0db59bed1 | N/A | N/A |
| With tests and documentation | 2d281b0a767da15102933272e0f147763a720e74^..ad67748bfbe8d3ae526758ed3acc52cc9b190d56 | 2ddc5a6517070e066c383aadc316b3b8b1c1cece^..39bb25d0ff4a3f2302e319b5c5c92ca0a05dd39c | 535bcfc3c8c203477cc645e6fecf82c0db59bed1^..c3517bc1867a9ddaa78420a0bd8e71b096e5958a | N/A | N/A |

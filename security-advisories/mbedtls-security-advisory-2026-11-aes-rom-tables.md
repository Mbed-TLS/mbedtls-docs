# AES timing side channel through flash reads to ROM table (CVE-2026-115492)

**Title** | AES timing side channel through flash reads to ROM table
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-115492
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS; all versions of TF-PSA-Crypto
**Necessary mitigation** | Affected users must apply the changes described under “[Resolution](#resolution)”
**Impact** | Key leakage to external observers
**CWE** | CWE-208: Observable Timing Discrepancy
**CAPEC** | CAPEC-97: Cryptanalysis
**Severity** | MEDIUM
**Credits** | Colin O'Flynn

## Vulnerability

The built-in implementation of block ciphers (AES, ARIA, Camellia) uses a naive approach that looks up values in a table based on data derived from the key. The timing of these accesses can leak the key material.

For AES, if the compile-time option `MBEDTLS_AES_ROM_TABLES` is enabled, the table is stored with the code. (Otherwise, it is constructed at run time and thus stored in RAM.) On most microcontrollers, the code is executed from flash memory, and the timing of flash reads depends on the sequence of indexes at which table lookups happen. As a result, an adversary who can observe the timing of a block cipher operation may be able to reconstruct the key.

Note that this does not require the adversary to run any code on the device. Merely observing the timing of responses over a bus or a local network can be sufficient if the device's response time is sufficiently correlated with the time spent in encryption or decryption. However, a large number of traces will be needed, which may make the attack impractical if the amount of traffic is low or there are other factors affecting the timing of responses.

For Camellia and ARIA, the built-in implementation always uses a table stored with the code. The rate of information leakage is less than AES, and no exploit is known.

## Impact

An external observer who can measure the timing of responses to a request that involve encryption or decryption with a long-term AES key may be able reconstruct the key.

## Affected versions

All versions of TF-PSA-Crypto and Mbed TLS affected.

## Work-around

As discussed [in the TF-PSA-Crypto and Mbed TLS security policy](https://github.com/Mbed-TLS/TF-PSA-Crypto/blob/development/SECURITY.md#block-ciphers), the built-in implementation of block ciphers is not protected against timing attacks. Implementations using a hardware accelerator are typically protected against such timing side channels, but please review your accelerator's documentation carefully. If your platform lacks a hardware accelerator, if possible, use ChaCha20+Poly1305 instead of a mode based on a block cipher.

Only devices where code is executed from flash memory are affected. (However, if the code is executed from RAM, other timing side channels may be present.)

For AES, to avoid this vulnerability, make sure that the compile-time option `MBEDTLS_AES_ROM_TABLES` is disabled (it is disabled by default). For Camellia and ARIA, no exploit is known, but caution is advised.

The attack requires a large number of traces unless the attacker can observe the timing of individual flash reads. As a consequence, in many environments, long-term keys and keys used to encrypt a large amount of data (such as a firmware update) are at risk, but session keys that are only used for a short transmission are still safe.

## Resolution

Affected users should use one of the workarounds described above.

## Fix commits

N/A

# Spectre-PHT side channel in ECDSA (CVE-2026-93835)

**Title** | Spectre-PHT side channel in ECDSA
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-93835
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; all versions of Mbed TLS from 4.0.0 to 4.1.1; Mbed TLS 4.2.0; all versions of TF-PSA-Crypto up to 1.1.1; TF-PSA-Crypto 1.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later versions; TF-PSA-Crypto 1.1.2 and later 1.1.x versions; TF-PSA-Crypto 1.3.0 and later versions
**Impact** | Partial key leakage to powerful local attackers
**CWE** | CWE-208: Observable Timing Discrepancy
**CAPEC** | CAPEC-663: Exploitation of Transient Instruction Execution
**Severity** | MEDIUM
**Credits** | Oleksii Oleksenko (Azure Research, Microsoft) and Alvise de Faveri Tron (Vrije Universiteit Amsterdam)

## Vulnerability

When calculating an ECDSA signature, the last step is to calculate the second component of the signature `s = ((e + r * d) / k) mod N` where `d` is the private key and `k` is a nonce that must remain secret. Publishing the result of this computation is safe, but publishing intermediate values, or values that result from a glitched computation, is not safe. The library uses a combination of constant-time operations and blinding to avoid leaking intermediate values through timing.

The calculation of the addition `e + r*d` may have a carry, and the precise timing of the execution reveals whether a carry is present. On its own, leaking the value of the carry is not known to be problematic. The addition is a multi-word bignum addition. On platforms with branch prediction, the processor may speculatively exit the loop early. In this case, the information that leaks is a predicate on the low word(s) of `e + r*d`, and since `e` and `r` are public values, this provides independent predicates on the low `i` words of `d` for each value of `i`. Across many signatures, this may provide enough information to reconstruct part or all of the private key `d`.

This is an instance of a Spectre v1 (Spectre-PHT) speculative-execution side channel attack.

## Impact

On platforms with speculative execution, a powerful local attacker (for example, a normal world operating system attacking a secure enclave) may recover ECDSA keys used for signing.

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
| Basic fix | a64940ce66f78a68c9015db94d3f4754311500ee 6ccb2b30e8947ded1cf44e292b03f5854c4ea2d5 7b89e9d1c42d25f20d9bb61ff3c7a9e34bc44b85 081ac997a71630a37d51d952bf30ef98cee47ba6 4c577a7843ec819c8f6b0d43311aadf6b53e730e fd2cc5767ce5844fb46093c4b91070645c8bdb08 c38bc001a55064d4a38ef4d3754840ecccc38ad6 | 9e0785e5e1533e580886ff97a6d2a9a4284f4735 0774a74135a800b8634ee8a134b4d3baca9af90f d6450b91c0f8c30c1c5fb01b71e8e8c46efd428e ff14cb7adb5893b6cdf682d4a66e3d820294160e b09b2e7854c65c5f1196247d4dd9f2619f2a05db 4207a5685b0ad890fe0bedd6a014049737e8dbfb 8d437f38aa3542a8b6c730255b3c7a8e600b7f56 | 4fcc778e1d1c72a2be717064ac0caa8010f29a14 be8ab95d286ca3ddd0e85a55807a50af676053d0 494f0f6b2b240ba08f0306f4b50ac8b8de954de1 14458bb24a1198b7024c67296ea789ace83cf657 7ed809576bdcdc912ed2ceccfe624002838fe6fc 8124c4b65676eddd4f28328ef8932e005b2b5533 22faeba6dfeb1ed9771f94cf9e732f96c9d97d70 | N/A | N/A |
| With tests and documentation | dbd19367068742a54fdb8f6fe3eacd799fb76d74^..2b3b55125c047b1f953a34095db0b1d9b0fe1085 | 215784ced9d2fc788ce35ab070e5335db033f8e0^..a8f681b8b535dd3b040b6495f33a70ff90aa58ba | f1fd2d3aedd871cda6ddf87722e8f339da26751a^..327c2284578955e1c8696ca64bc36dd607f0f549 | N/A | N/A |

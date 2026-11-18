# Secret-dependent branches in p256-m P-256 arithmetic (CVE-2026-93845)

**Title** | Secret-dependent branches in p256-m P-256 arithmetic
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-93845
**Date** | 16 November 2026
**Affects** | Mbed TLS through 3.6.7; Mbed TLS 4.0.0 through 4.1.1; Mbed TLS 4.2.0; TF-PSA-Crypto through 1.1.1; TF-PSA-Crypto 1.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later versions; TF-PSA-Crypto 1.1.2 and later 1.1.x versions; TF-PSA-Crypto 1.3.0 and later versions
**Impact** | Leakage of ECDSA ephemeral scalar bits, potentially leading to private key recovery
**CWE** | CWE-208: Observable Timing Discrepancy
**CAPEC** | CAPEC-621: Analysis of Packet Timing and Sizes; CAPEC-97: Cryptanalysis
**Severity** | MEDIUM
**Credits** | Zahiya Zahid (MS Information Security, MCS, NUST) and Shahzaib Tahir (MS Information Security, MCS, NUST)

## Vulnerability

The p256-m implementation of ECDH and ECDSA on NIST P-256 performs 256-bit
addition and subtraction using operations that can cause some compilers to
generate branches depending on carry or borrow values. When the operands
depend on a secret scalar, these branches can reveal information about that
scalar through a side channel. Whether the branches occur depends on the
target architecture and compiler (see below).

This affects builds with `MBEDTLS_PSA_P256M_DRIVER_ENABLED` defined. The driver
can be enabled explicitly, or implicitly when NIST P-256 is the only supported
curve and EC J-PAKE is disabled.

An attacker can exploit the leak if they can distinguish whether the first
iteration of `u256_sub()` borrows. This may be possible by measuring the
latency of that specific iteration or monitoring a shared branch predictor or
instruction cache. Such fine-grained observation typically requires a
capable local attacker.

## Impact

During ECDSA signing, a local attacker may be able to recover some bits of
the ephemeral scalar from the branch behavior. Leakage from signatures may
allow recovery of the signing private key.

## Affected versions

TF-PSA-Crypto versions through 1.1.1 and version 1.2.0 are affected when the
p256-m driver is enabled and the compiler generates secret-dependent branches.

Mbed TLS versions through 3.6.7, versions 4.0.0 through 4.1.1, and version
4.2.0 are affected under the same conditions. In Mbed TLS 4.x, p256-m is
provided through TF-PSA-Crypto.

## Affected platforms

All 64-bit architectures are unaffected.

The following 32-bit architectures were checked and found unaffected with the
tested versions of GCC and Clang: Arm, Intel, MIPS, PowerPC and RISC-V.

The only architecture known to be affected so far is Xtensa.

## Work-around

There is no work-around.

Applications that do not enable the p256-m driver are not affected by this
vulnerability.

## Resolution

Affected TF-PSA-Crypto users should upgrade to 1.1.2 or a later 1.1.x
version, or to 1.3.0 or a later version.

Affected Mbed TLS users should upgrade to 3.6.8 or a later 3.6.x version,
4.1.2 or a later 4.1.x version, or 4.3.0 or a later version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if
you are maintaining a branch with backported bug fixes, here are the most
relevant commits. Please note that these commits may not apply cleanly to
older versions of the library, and may not provide a complete fix even if
they do apply. The TF-PSA-Crypto and Mbed TLS development team does not
provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.1.x | TF-PSA-Crypto 1.x (x&gt;1) | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | ------------------- | -------------------------- | -------------- | --------------------- |
| Basic fix | 650c1a451e474b73aa16f5e2de8c4aa157c502dd^..83b7298732d8b80fcc59c1cc623f4f146f6f1452 | f954b5a00b1be5c5df5b68934aa523a29eb534fb^..9b061de1254d0c4845a0e4bf18a35e9390f105ee | 34fa6650fcaa618273dd419003dce2ec62d219cd^..5738a1c1c1283e012439f543bdae6d44277d855f | N/A (submodule) | N/A (submodule) |

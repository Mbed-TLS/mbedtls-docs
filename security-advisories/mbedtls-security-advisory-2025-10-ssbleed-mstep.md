# Side channel in RSA key generation and operations (SSBleed, M-Step) (CVE-2025-54764)

**Title** | Side channel in RSA key generation and operations (SSBleed, M-Step)
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-54764
**Date** | 15 October 2025
**Affects** | all version of Mbed TLS up to 3.6.4
**Not affected** | Mbed TLS 3.6.5 and later, TF-PSA-Crypto 1.0 and later
**Impact** | Disclosure of private key material
**Severity** | MEDIUM
**Credits** | Independently: SSBleed team, M-Step team (see below)


## Vulnerability

Mbed TLS's modular inversion routine and GCD routine are vulnerable to local
timing attacks in a number of settings discussed below.

These functions are used in RSA, making the following operations vulnerable in
all configurations:

- RSA key generation with any API (`mbedtls_rsa_gen_key()` and all
  `psa_generate_key*()` functions).
- Use of `mbedtls_rsa_complete()` to import RSA private keys that are incomplete
  or not in the standard format. (The only exception is when
  `MBEDTLS_RSA_NO_CRT` is enabled and all of `N`, `E`, `D`, `P` and `Q` have
  been set before calling `mbedtls_rsa_complete()`.) (Note: internal uses of
  `mbedtls_rsa_complete()` in the library are always safe.)

Additionally, if `MBEDTLS_RSA_NO_CRT` is enabled, the following operations are
also vulnerable:

- Import of RSA key pairs with `psa_import_key()`.
- Export of RSA key pairs with any key export API (PSA, PK).

Additionally, if `MBEDTLS_RSA_NO_CRT` and `MBEDTLS_USE_PSA_CRYPTO` are both
enabled, the following operations are also vulnerable:

- Signature generation with PK (`mbedtls_pk_sign()`, `mbedtls_pk_sign_ext()`).
- Decryption with PK (`mbedtls_pk_decrypt()`).

Elliptic curve cryptography (ECDSA, ECDH, EC-JPAKE) is not affected as the
vulnerable functions are used in a safe way (with blinding).

Finite-field Diffie-Hellman (FFDH) is not affected as it does not use the
vulnerable functions.

Direct use of `mbedtls_mpi_inv_mod()` by applications on secret data is most
likely vulnerable unless you use proper blinding.

Direct use of `mbedtls_mpi_gcd()` by applications on secret data is most likely
vulnerable, unless the compiler used has `__builtin_ctz` (GCC 10 and above has
it, earlier versions don't), and it is not implemented using a loop (most
architectures have instructions that are more efficient than using a loop).

## Impact

When one of the vulnerable RSA functions mentioned above is used, the
vulnerability allows the attacker to fully recover the RSA private key.

When `mbedtls_mpi_mod_inv()` is directly called by an application (or
`mbedtls_mpi_gcd()` in a build where it is affected, see above), the
vulnerability allows the attacker to recover both inputs.

## Attack settings

The side channels in GCD and modular inversion can be exploited by a local
attacker in a number of circumstances. Two teams independently developed tools
allowing to trace a victim process, recover the inputs to
`mbedtls_mpi_mod_inv()` and break RSA key generation:

1. SSBleed: this uses the Memory Dependence Predictor (MDP) on some
   Arm-v9 CPUs. The attacker only needs to be able to run code on the same core
   as the victim but does not need elevated privileges. The proof of concept
   fully recovers RSA private keys from `mbedtls_rsa_gen_key()` and the same
   principle applies to other unblinded uses of `mbedtls_mpi_inv_mod()`.
2. M-Step: in a setting where TrustZone-M is used, the M-Step framework allows
   the non-secure world to abuse timer interrupts to effectively single-step the
   secure world and trace its execution flow.
   The proofs of concepts fully recover RSA private keys from
   `mbedtls_rsa_gen_key()` and `mbedtls_rsa_complete()`. Several other
   exploitation paths in RSA are identified. In particular, `mbedtls_mpi_gcd()`
   is found to be vulnerable when Mbed TLS is compiled with a compiler that does
   not have `__builtin_ctz`.

The same functions are most probably also vulnerable in other circumstances
using similar attack techniques: SGX-Step, SEV-Step, microarchitectural
attacks similar to SSBleed...

### Credits

**SSBleed:** Chang Liu from Tsinghua University and Trevor E. Carlson from National University of Singapore

**M-Step:** Cristiano Rodrigues (University of Minho), Marton Bognar (DistriNet, KU Leuven), Sandro Pinto (University of Minho), Jo Van Bulck (DistriNet, KU Leuven)

## Affected versions

All versions of Mbed TLS up to 3.6.4 are affected.

## Work-around

Applications that do not generate RSA keys and do not import private RSA keys
with `mbedtls_rsa_import()`+`mbedtls_rsa_complete()`, but use other RSA
functions that are only vulnerable with `MBEDTLS_RSA_NO_CRT`, can recompile
without `MBEDTLS_RSA_NO_CRT`.

Applications that do not use RSA private keys and do not directly call
`mbedtls_mpi_inv_mod()` or `mbedtls_mpi_gcd()` are not affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.5 or TF-PSA-Crypto 1.0.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

```
8f4779c6fa40374f88404787bebad85cc7e9969b..eb346801263ba4612b5e29633bd55fe18943ca65
9b54f934588bc373f3c3f5d45b5a3ad0ae003082..99270322ffac3546f813b1069fd6efb667cdce3f
246d86b941ef2d2bdeabd7035efe7200bc609b91..a08faf90700e46f6aa2a6e3fee8a6a71ddb816ce
246d86b941ef2d2bdeabd7035efe7200bc609b91..30f073236922fe4e528fdf82eb442babb50516fa
```

**Title** | Unchecked return value in LMS verification allows signature bypass
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-49600
**Date** | 2025-06-30
**Affects** | Mbed TLS 3.3.0 through 3.6.3
**Not affected** | Mbed TLS 3.6.4 and later 3.6 versions and upcoming TF-PSA-Crypto 1.0 and later versions
**Impact** | LMS signature verification bypass
**Severity** | MEDIUM
**Credits** | Found and reported by Linh Le and Ngan Nguyen from Calif.

## Vulnerability

In `mbedtls_lms_verify()`, the return values of the internal Merkle tree
functions `create_merkle_leaf_value()` and `create_merkle_internal_value()` are
not checked. These functions return an integer that indicates whether the call
succeeded or not. If a failure occurs, the output buffer (`Tc_candidate_root_node`)
may remain uninitialized, and the result of the signature verification is
unpredictable. When the software implementation of SHA-256 is used,
these functions will not fail. However, with hardware-accelerated hashing, an attacker
could use fault injection against the accelerator to bypass verification.

Under the following plausible scenario, an adversary could bypass signature verification:

- `mbedtls_lms_verify()` is first called to verify a valid message and signature.
  A valid value for Tc_candidate_root_node is stored on the stack.
- The adversary then injects a fault into the hash accelerator, causing all
  subsequent hashing operations to fail.
- `mbedtls_lms_verify()` is called again with the same key and signature but a different message,
  without invoking other functions that would overwrite the stack. Because the `Tc_candidate_root_node`
  is not updated due to the failure of the hashing operations, the previous valid value remains
  on the stack, causing the verification to incorrectly succeed.

## Impact

LMS signature verification bypass

## Affected versions

Mbed TLS 3.3.0 through 3.6.3

## Resolution

Affected users should upgrade to Mbed TLS 3.6.4 or upcoming TF-PSA-Crypto 1.0 or later.

## Work-around

Do not use a hardware hash accelerator that can fail without
halting the system. If a hardware accelerator is required, choose
accelerators that are tamper-proof or include fault-injection detection.

Alternatively use the built-in software implementation of SHA-256 if possible.
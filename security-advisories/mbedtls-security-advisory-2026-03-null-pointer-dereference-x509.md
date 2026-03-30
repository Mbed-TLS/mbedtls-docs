# Null pointer dereference when setting a distinguished name (CVE pending)

**Title** | Null pointer dereference when setting a distinguished name
--------- | ----------------------------------------------------------
**CVE** | Pending
**Date** | 31 March 2026
**Affects** | All versions of Mbed TLS from 3.5.0 up to 3.6.5, Mbed TLS 4.0.0
**Not affected** | Mbed TLS 3.6.6 and later 3.6 versions, Mbed TLS 4.1.0 and later 4.x versions
**Impact** | Arbitrary code execution
**Severity** | HIGH
**Credits** | Haruto Kimura (Stella)

## Vulnerability

An attacker who can cause a memory allocation failure during the execution of `mbedtls_x509_string_to_names()` can cause a call to `memcpy()` with a null pointer as the destination address.

`mbedtls_x509_string_to_names()` is also called indirectly via the following functions:
* `mbedtls_x509write_csr_set_subject_name()`
* `mbedtls_x509write_crt_set_subject_name()`
* `mbedtls_x509write_crt_set_issuer_name()`

## Impact

On a platform with memory protection this is likely to result in a segmentation fault. On a microcontroller this may write to an interrupt vector at address 0 and thereby allow arbitrary code execution.

## Affected versions

All versions of Mbed TLS from 3.5.0 up to 3.6.5 and Mbed TLS 4.0.0 are affected.

## Work-around

Ensure that Mbed TLS has ample memory when calling `mbedtls_x509_string_to_names()` so that `mbedtls_calloc()` will not fail.

On systems with memory protection where address 0 is not writable, this vulnerability will generate a segmentation fault or a memory protection error. As a result it will lead to a denial of service (DoS) on such systems rather than arbitrary code execution.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.6 or 4.1.0.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.x | Mbed TLS 4.x |
| ------ | -------------- | ----------------- | ------------ |
| Basic fix | bfaf4a47fd33da860796feaba6235847acb71127 | N/A | f549fc7bdcc9b435236de5594bec0ed8e587988c |
| With tests and documentation | branch up to 4704b6b4bd963f1331582374e881184addf8f523 | N/A | branch up to fe2599ea8238bdf5340a2f76ff2f3e3df095524b |

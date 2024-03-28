# Insecure handling of shared memory in PSA Crypto APIs

**Title** | Insecure handling of shared memory in PSA Crypto APIs
--------- | -----------------------------------------------------
**CVE** | CVE-2024-28960
**Date** | 25 March 2024
**Affects** | All versions of Mbed TLS from 2.18.0 to 2.28.7 and from 3.0.0 to 3.5.2; all versions of Mbed Crypto
**Severity** | High

## Vulnerability

This vulnerability affects products that use Mbed TLS to provide an implementation of the PSA Crypto API with domain isolation between API callers (“client application”) and the API implementation (“crypto server”), where communication is done through shared memory. Applications that use Mbed TLS as a library inside their own process space are not affected.

When a function takes parameters in memory that is shared with another protection domain (process, partition, etc.) that is untrusted, the untrusted domain can access the shared memory during the execution of the function, which can compromise security properties:

* If the untrusted domain modifies an input parameter while it is being processed, the function may obtain inconsistent data that could lead to exploitable vulnerabilities. For example, the function may run a validation pass and conclude that the data is valid, then process data that is now invalid due to the modification.
* If the function stores intermediate results in shared memory and reads them back, the untrusted domain can modify this intermediate result in a way that violates the function's expectations and lead to exploitable vulnerabilities.
* If the function stores intermediate results in an output parameter, the untrusted domain can read this value, which may leak confidential information.

The [PSA Certified Crypto API specification](https://arm-software.github.io/psa-api/crypto/1.1/overview/conventions.html#stability-of-parameters) requires implementations of the PSA Crypto API to ensure that when a function has buffer parameters, if the buffers are located in shared memory, the function must access the buffers in such a way that there is no security risk if the content of the buffer is read or modified during the execution of the function. In other words, it puts the responsibility on the API implementation to prevent the attack paths described above.

The implementation in previous versions of Mbed TLS (and in the discontinued product Mbed Crypto) does not take any particular precaution to protect the shared memory. This can allow unprivileged applications to break the security guarantees expected from domain isolation between them and a crypto server.

## Impact

The impact on crypto servers depends on the available cryptographic mechanisms, as well as the details of how memory accesses are performed at runtime. The following problematic scenarios are known:

* `psa_import_key` reading an RSA public key or RSA key pair from shared memory: a malicious client application may be able to trigger a buffer overread in the crypto server. This is possible on all builds when RSA support and `MBEDTLS_PEM_PARSE_C` are enabled, and may also be possible even if `MBEDTLS_PEM_PARSE_C` is disabled depending on how ASN.1 memory accesses are compiled.
* `psa_sign_hash` or `psa_sign_message` writing an RSA signature in shared memory: a malicious client application can perform arbitrary operations using the private key, bypassing the key's policy.

In addition, a client application that passes buffers that it shares with an untrusted application (in violation of the API specification) could be affected in at least the following scenarios:

* `psa_sign_hash` or `psa_sign_message` writing an RSA signature in memory that is shared directly between an untrusted application and the crypto server: this allows the untrusted application to sign arbitrary data, even if it would not otherwise be in control of the data to be signed.

Note that the impact can depend on how the code is compiled and optimized, since attacks rely on how many times the same memory location is accessed, which is not specified by the C language.

## Resolution

Affected users will want to upgrade to Mbed TLS 2.28.8 or Mbed TLS 3.6.0, and to ensure that the configuration option `MBEDTLS_PSA_ASSUME_EXCLUSIVE_BUFFERS` is disabled.

Users of a platform where the PSA Crypto API is implemented as a service using shared memory should review whether it is using shared memory in a way that is affected by this vulnerability.

## Work-around

Applications where Mbed TLS functions do not receive parameters that are in shared memory are unaffected. In particular, crypto servers that receive buffers in shared memory can avoid the vulnerability by copying inputs in shared memory into a server-owned memory buffer before passing the input to Mbed TLS library functions, and copying outputs from server-owned memory to shared memory. For example, a crypto server relying on the standard PSA Firmware Framework 1.0 APIs is not affected.

Please note that although all the currently known exploitable scenarios involve RSA, it is plausible that other cryptographic mechanisms could lead to exploitable scenarios in some environments.


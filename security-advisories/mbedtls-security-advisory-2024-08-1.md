# CTR\_DRBG prioritized over HMAC\_DRBG as the PSA DRBG

**Title** | CTR\_DRBG prioritized over HMAC\_DRBG as the PSA DRBG
--------- | -----------------------------------------------------
**CVE** | TODO
**Date** | TODO
**Affects** | All versions of Mbed TLS since 2.26.0
**Severity** | Low

## Vulnerability

Mbed TLS 2.26.0 introduced the configuration option `MBEDTLS_PSA_HMAC_DRBG_MD_TYPE` and documented that enabling it explicitly would cause the PSA cryptography subsystem to use HMAC\_DRBG as its pseudorandom generator component. However, this feature was accidentally documented but not implemented. In fact, all versions of Mbed TLS and Mbed Crypto have used CTR\_DRBG in the PSA subsystem if `MBEDTLS_CTR_DRBG_C` is enabled, regardless of whether `MBEDTLS_PSA_HMAC_DRBG_MD_TYPE` is set.

## Impact

Both HMAC\_DRBG (using a hash such as SHA-256 or SHA-512) and CTR\_DRBG (using AES) are generally acceptable choices as pseudorandom generators, and both are secure in terms of the quality of their output. However, they have different security postures with respect to side channels. In particular, when AES is implemented in software, it is more prone to timing and power side channels than hashes, so CTR\_DRBG is weaker against side channel attacks than HMAC\_DRBG. Hence some users may prefer to use HMAC\_DRBG.

## Resolution

Starting with Mbed TLS 3.6.1 and 2.28.9, the documentation accurately represents the behavior. The behavior does not change: `MBEDTLS_PSA_HMAC_DRBG_MD_TYPE` is ignored when PSA uses CTR\_DRBG.

## Work-around

To use HMAC\_DRBG as the pseudorandom generator in the PSA subsystem, make sure that the compile-time option `MBEDTLS_CTR_DRBG_C` is disabled.

# RSASSA-PSS

## Introduction

**RSASSA-PSS** is an improved probabilistic signature scheme with appendix. This means that you can use a private RSA key to sign data in combination with random input. The other side of the communication can then verify the signature with the corresponding public RSA key. Because random data is used in this signature scheme, the two signatures for the same input are different and both can be used to verify the original data.

RSASSA-PSS was standardized in [PKCS#1 v2.1](https://tools.ietf.org/html/rfc3447). It can be used as an alternative to the more widespread RSASSA algorithm in PKCS#1 v1.5.

## RSASSA-PSS vs RSASSA (PKCS#1 v1.5)

RSASSA-PSS is more robust than RSASSA (PKCS#1 v1.5) and you do not need to take as many precautions to use it securely as you do with the older version. However, the original RSASSA is more widely supported by existing protocols and software. For example, the SSL protocol only supports RSASSA (PKCS#1 v1.5) for RSA signatures, and does not support RSASSA-PSS. So, although RSASSA-PSS is more advantageous from a security perspective, in practice, RSASSA is still more widely used.

## Mbed TLS support of RSASSA-PSS

Mbed TLS fully supports RSASSA-PSS directly in its [RSA module](/rsa-source-code). To use RSA as specified in PKCS#1 v2.1, with SHA1 as the hash method, for example, you should initialize your RSA context with:

```
mbedtls_rsainit( &rsa, RSA_PKCS_V21, MBEDTLS_MD_SHA256);
```

After loading the RSA key into that context, you can then use it to sign, with the RSASSA-PSS scheme, by using the generic `mbedtls_rsapkcs1_sign()` for signing and `mbedtls_rsapkcs1_verify()` for verification. Alternatively, you can use the more specific  `mbedtls_rsarsassa_pss_sign()` and `mbedtls_rsarsassa_pss_verify()`.

<!--",Short article on what RSASSA-PSS is, the differences with RSASSA-PKCS#1-v1.5 and how to use RSASSA-PSS within Mbed TLS.",,"RSASSA-PSS, PKCS#1, RSA",published,"2013-12-10 12:52:00",1,9774,"2015-07-24 09:51:00","Paul Bakker"-->

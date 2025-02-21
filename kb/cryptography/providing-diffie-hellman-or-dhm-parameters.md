# Providing Diffie-Hellman-Merkle (DHM) parameters

## Choosing DHM parameters

Developers have the option to set the DHM parameters for SSL servers with `mbedtls_ssl_conf_dh_param_bin()`. This is not a requirement as the default parameters are preloaded.

## Default DHM parameters

The DHM parameters that the TLS handshake uses are set by default to the 2048-bit MODP parameters from [RFC 3526](https://www.ietf.org/rfc/rfc3526.txt) (`MBEDTLS_DHM_RFC3526_MODP_2048_P_BIN` and `MBEDTLS_DHM_RFC3526_MODP_2048_G_BIN`). From a security perspective, it is desirable to use a larger value, unless you have clients for which this will cause interoperability issues. Larger values are provided in [dhm.h](https://github.com/Mbed-TLS/mbedtls/blob/development/include/mbedtls/dhm.h).

## Custom and standard parameters

We used to recommend using standard parameters rather than generating your own. However, the team of researchers behind the [Logjam attack](https://weakdh.org/) also showed that a risk associated is with that if the parameters are not large enough. More precisely, they showed that the amount of computation required to break any number of MODP DHM key exchanges is close to the amount required to break just one of them, as long as they all use the same parameters. So if your parameter size is just at the limit of what an adversary can break, using standard parameters allows the adversary to amortize the cost of the initial computation, which is not what you want.

1,024 bits is considered within reach of the most powerful adversaries, and 2,048 bits safe according to public knowledge. If you absolutely must use 1,024 bit parameters for compatibility with old clients, it is highly desirable to generate your own rather than use the standard parameters, as long as you take into consideration [backdoor vulnerabilities](/tech-updates/blog/dh-backdoors). If you can use parameters of 2,048 bits or more, then you are safe either way.

An alternative is to switch to Elliptic Curve Diffie-Hellman (ECDH ciphersuite), which does not have this security issue and also improves the performance, as [this article](ephemeral-diffie-hellman.md) describes.

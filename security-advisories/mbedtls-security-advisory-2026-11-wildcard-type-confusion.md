# Subject Alternative Name type confusion in certificate verification (CVE-2026-90470)

**Title** | Subject Alternative Name type confusion in certificate verification
--------- | ----------------------------------------------------------
**CVE** | CVE-2026-90470
**Date** | 16 November 2026
**Affects** | All versions of Mbed TLS up to 3.6.7; all versions of Mbed TLS from 4.0.0 to 4.1.1; Mbed TLS 4.2.0
**Not affected** | Mbed TLS 3.6.8 and later 3.6.x versions; Mbed TLS 4.1.2 and later 4.1.x versions; Mbed TLS 4.3.0 and later 4.x versions
**Impact** | Improper certificate validation
**CWE** | CWE-297: Improper Validation of Certificate with Host Mismatch
**CAPEC** | CAPEC-114: Authentication Abuse
**Severity** | MEDIUM
**Credits** | saikumar279

## Vulnerability

A certificate containing a DNS wildcard is suffix-matched against the expected name string supplied by the user, even if the expected name is not a DNS name. For example, the URIs "sip:sip.example.com" and "https://unqualified-host-name/abc.example.com" will be incorrectly matched against the DNS wildcard "\*.example.com".

## Impact

If the victim is expecting a certificate with a given URI in the certificate name and passes it as a string to `mbedtls_x509_crt_verify()`, the attacker may be able to acquire a certificate with a wildcard DNS name that shares a suffix with the required URI and be accepted. This is an authentication bypass.

## Affected versions

All versions of Mbed TLS up to 3.6.7 are affected.
All versions of Mbed TLS from 4.0.0 to 4.1.1 are affected.
Mbed TLS 4.2.0 is affected.

## Work-around

There is no work-around.

Applications that only check for IP address or DNS Subject Alternative Names are not affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.8 or a later 3.6.x version,
or to Mbed TLS 4.1.2 or a later 4.1.x version,
or to Mbed TLS 4.3 or a later 4.x version.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The TF-PSA-Crypto and Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.1.x | TF-PSA-Crypto 1.x (x&gt;1) | Mbed TLS 4.1.x | Mbed TLS 4.x (x&gt;1) |
| ------ | -------------- | ------------------- | -------------------------- | -------------- | --------------------- |
| Basic fix | e238cb8fff1dab9800efea0228dc229db5796f67 b2211588d782ebafd6df665f2441034c841a0299 e37fb402f5656fb49d84956464787e60b9309b1f 2e68fb46e5e7484a634485ce76e68916bca0e95d 691bbbc8625905b4e38495128ee139132838f9c1 2d8d9b9a6a24a03721e35d20e65a073631a361fd 20a7c60f41c433c1fabc59bcdde0124f0b7df99c aa3460e7380f89e1380e7372d77ebf09b2b225cb 54d6dec9ef43948057d4b9114d33d2e586a28b0f e093476ff647012a15fdfe408cefd06764f65c49 aff778062ae57e44dbf0aa2e3ab822f09cd79e23 9a77a3c0110cfee73991247488c50a10315f2f67 39c46b849a8eb5a45d9905923829d6852ad8b27e 03efe139c6740be0d7f929b7135940da489f0ed7 24450c755df47e921e97e8147dd7f677fb9a8a37 1fb96a9980678674713644771636f2b443d6213c d2fdd9eff548c03ec22d139a38fece7a9435e610 545775216944008b817a61aca1f6fcd227ff7e1f | N/A | N/A | 1d73f5521f457fcd3b06010133b201fa7e948d39 6478f5c4452bec7287f1706c89672a27925277fa 2a913318c820e0b7cb889248b297371fbbe98eb4 0d8516ef89f93fa949b58a40ebaa8a824ff165df 7c847c06ac93cbf41b6c5eb779ffca46a90a6e46 1a0c103570b8dffd7c5c68435804185a12061062 65b7196e70277959b1927ed7d6d53446fef8283a ff43e72332a60501ea28c7e982600494ff0e83da d2f74636de934d0d6eacbe80c24e12b63629010d 7261057e6fc9235fc1ec0bd11b94e5c41fdaea74 f75100f63834d6c8683128689179368fd228585e 1065d8e81c8fa91ad72d1816e56851ac666a8184 8bf783dad35e2ef09b9b7e58d5436ea91bd37736 1013df2664b8f59b3d676ee0e905b1abcf5f2ce1 8b6254aad4b67281c0aab916d46abc77296192e7 09d36e0c202497fe4731ee603b0163574468e044 80e3bb488456d38d4f8d9e783632424cdffaf09d | 5026847530994ffa52d4379ad461897f8fe7ce9d bc245946472a1fd031f33bbbb348c9a6ee23dda8 57d2e36f5996fa423519714f12ea95c9049bf9f6 7a58c289d65df0c0f155bd199b514c44b44dd35f 1c31e0800edd661e31cdcf5b073e01bef2cf115d e59b5902538a27a8f218fda39679b4e0b11375e9 4ddd3f8602da923753b7ad1e81e5ebfc16bcbb78 81cd3496c3e178301ae3fcba964f7b986171e67f 360d84c291f3814f364155a4ca9976a2d897f9b3 47fc08a389d3dee2180a49c16f4385203a1c962c 861a8583cf934b6acce4ab2fb089822764d7ab46 4bbedd2c5a27bf975c5f2f04927955d591ac0cfb 8c581babe44a643d28042ff31ea41556107a89e9 1b34f7a8247e67a276b75ae6bc53e323a08c7948 f11550eb580e154717fcddef7e5a0dc200e2a369 871a3c612932463aae9af26e823b5cc00ddd64bb e7e43a345f183db5d3f00c8aae84d8e544b25001 |
| With tests and documentation | ba2d3180e42fdfd0d99fed502d08ca7b45230267^..1674341c81e8264c99bd3286659fe03ad770a690 | N/A | N/A | 7a553209be31233b64324322657c4e2fb2b953d6^..35077b7e9b7dd2bae3563a1bf3b9f6f1f7767ea2 | ef2a6dfdfb64dd96f4f9852fd3ef48990c3295b5^..1e7ee00052e648763e148f9cb458e206c6fc95ef |

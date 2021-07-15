# PolarSSL Security Advisory 2014-02

**Title** |  Denial of Service against GCM enabled servers (and clients)
---|---
**CVE** |  CVE-2014-4911
**Date** |  11th of July 2014
**Affects** |  All PolarSSL versions before 1.2.11 and 1.3.8
**Not affected** |  All branches before 1.2.x and version > 1.2.10 or > 1.3.7
**Impact** |  Crash of server application (or clients by a malicious server)
**Exploit** |  Withheld

A denial of service against PolarSSL servers that offer GCM ciphersuites has
been found using the fuzzing techniques of the Codenomicon Defensics toolkit.
Potentially clients are affected too if a malicious server decides to execute
the denial of service attack against its clients.

## Impact

A server or client that is targeted with this attack can be potentially
crashed with a segfault.

## Workaround

Disabling of the GCM ciphersuites prevents this attack.

Alternatively the following patch can be applied to your current PolarSSL
1.3.7 code base:



    diff --git a/library/ssl_tls.c b/library/ssl_tls.c
    index 480c5e5..a57f3f1 100644
    --- a/library/ssl_tls.c
    +++ b/library/ssl_tls.c
    @@ -1416,9 +1416,15 @@ static int ssl_decrypt_buf( ssl_context *ssl )
             size_t dec_msglen, olen, totlen;
             unsigned char add_data[13];
             int ret = POLARSSL_ERR_SSL_FEATURE_UNAVAILABLE;
    +        size_t gcm_overhead = ssl->transform_in->ivlen +
    +                              ssl->transform_in->fixed_ivlen +
    +                              16; /* explicit IV + tag */
    +
    +        if( ssl->in_msglen < gcm_overhead )
    +            return( POLARSSL_ERR_SSL_INVALID_MAC );
    +
    +        dec_msglen = ssl->in_msglen - gcm_overhead;

    -        dec_msglen = ssl->in_msglen - ( ssl->transform_in->ivlen -
    -                                        ssl->transform_in->fixed_ivlen );
    -        dec_msglen -= 16;
             dec_msg = ssl->in_msg;
             dec_msg_result = ssl->in_msg;


## Resolution

Upgrade to PolarSSL 1.3.8 for the 1.3 branch or PolarSSL 1.2.11 for the 1.2
branch.

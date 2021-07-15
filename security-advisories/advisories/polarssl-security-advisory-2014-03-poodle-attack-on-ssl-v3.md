# PolarSSL Security Advisory 2014-03

**Title** |  POODLE attack on SSLv3
---|---
**CVE** |  CVE-2014-3566
**Date** |  16th of October 2014
**Affects** |  The SSL v3 protocol
**Not affected** |  TLS 1.0 and up
**Impact** |  Potential disclosure of information
**Exploit** |  Active Man-in-the-Middle required

On October the 14th a paper was released on the so-called POODLE attack on
SSLv3.

This Security Advisory only describes the impact and workaround for the POODLE
attack. A more detailed explanation can be found in our post that puts [the
POODLE attack in perspective](/tech-updates/blog/sslv3-and-poodle-in-
perspective).

## Impact of POODLE

The POODLE attack assumes that the attacker is successful in actively
manipulating the packets of the handshake between the client and the server,
resulting in a downgraded SSL v3 connection.

If the attacker is then able to actively manipulate packets sent during the
connection, the impact can be leakage of secret information, such as the
session cookie in HTTPS.

For a lot of protocols other than HTTPS there is no real impact as there is
nothing to reveal that is session bound and not incidental.

## Workaround and resolution

PolarSSL allows you to disable SSLv3 at compile time and at runtime.

If you disable `POLARSSL_SSL_PROTO_SSL3` in _config.h_ , support for SSLv3 is
not compiled into your library.

At runtime you can call:



    ssl_set_min_version( ssl, SSL_MAJOR_VERSION_3, SSL_MINOR_VERSION_1 );


This forces your SSL context to only negotiate TLS 1.0 or higher.

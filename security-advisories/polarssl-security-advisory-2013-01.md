# PolarSSL Security Advisory 2013-01

**Title** |  Lucky thirteen - timing side channel during decryption
---|---
**CVE** |  CVE-2013-0169
**Date** |  4th of February 2013 ( **Updated on 12th of July 2013** )
**Affects** |  all checked SSL libraries including PolarSSL versions prior to<br>PolarSSL 1.2.6
**Not affected** |  AES-GCM-based or RC4-based ciphersuites. Servers and<br>clients that only communicate over a private network
**Impact** |  Possible (partial) recovery of plaintext
**Exploit** |  Withheld
**Solution** |  Upgrade to PolarSSL 1.2.6 or PolarSSL 1.1.6
**Workaround** |  Only use AES-GCM-based of RC4-based ciphersuites
**Credits** |  Kenny Paterson and Nadhem Alfardan

The paper [Lucky Thirteen: Breaking the TLS and DTLS Record
Protocols](http://www.isg.rhul.ac.uk/tls) by Kenny Paterson and Nadhem
Alfardan describes a family of attacks that applies to implementations of CBC-
mode ciphersuites in TLS 1.1 and 1.2 / DTLS 1.0 and 1.2 (and earlier
implementations).

The attack is based on the fact that, when badly formatted padding is
encountered during decryption, a MAC check must still be performed on some
data to prevent the known timing attacks. The RFCs for TLS 1.1 and TLS 1.2
recommend checking the MAC as if there was a zero-length pad. Depending on
some other factors, the small timing difference introduced here can be used to
perform a an attack to reveal (part of) the plaintext.

## Impact

When a CBC-based ciphersuite is used and an adversary has the ability to
inject packets at will into the connection between the client and the server,
the adversary can potentially use statistical analysis to retrieve plaintext
from ciphertext messages.

All SSL libraries checked by the authors were revealed to be vulnerable in
some way.

This attack works better against DTLS than regular TLS. PolarSSL only uses
regular TLS at this point. In addition PolarSSL does not send the alert
messages required for the adversary to properly perform this attack. Keep this
in mind when assessing the impact for your situation.

## Resolution

PolarSSL 1.2.5 and PolarSSL 1.2.6 contain fixes in the SSL decrypt process (
**ssl_decrypt_buf()** ) that remove the timing differences that can result
from malformed padding data. As a result our timing tests show that
**ssl_decrypt_buf()** now returns in a semi-fixed amount of time independent
of the padding length preventing an adversary to use these timing differences
to attack the secured communication channel.

## Workaround

As a workaround it is also possible to disable CBC-based ciphersuites and only
allow AES-GCM-based or RC4-based ciphersuites. Due to the nature of these
ciphersuites they are not vulnerable to the attacks described in the paper.

## Advice

We strongly advise you to upgrade to PolarSSL 1.2.6 if an adversary can gain
access to (part of) the network and inject packets between your servers and
clients.

## Special thanks

We want to thank Kenny and Nadhem for their support during the disclosure
phase and the testing of our patch.

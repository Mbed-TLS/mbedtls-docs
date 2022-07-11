# PolarSSL Security Advisory 2013-05

**Title** |  Timing Attack against protected RSA-CRT implementation used in<br>PolarSSL
---|---
**CVE** |  CVE-2013-5915
**Date** |  1st of October 2013
**Affects** |  PolarSSL versions prior to 1.2.9 and 1.3.0
**Not affected** |  PolarSSL 1.3.0 and above
**Impact** |  Recovery of the private RSA key
**Exploit** |  Withheld
**Solution** |  Upgrade to PolarSSL 1.3.0 or 1.2.9
**Credits** |  Cyril Arnaud and Pierre-Alain Fouque

The researchers Cyril Arnaud and Pierre-Alain Fouque investigated the PolarSSL
RSA implementation and discovered a bias in the implementation of the
Montgomery multiplication that we used. For which they then show that it can
be used to mount an attack on the RSA key. Although their test attack is done
on a local system, there seems to be enough indication that this can properly
be performed from a remote system as well.

The attack has been added to the known attacks in [our Security
Center](/security).

## Impact

All versions prior to PolarSSL 1.2.9 and 1.3.0 are affected if a third party
can send arbitrary handshake messages to your server.

If correctly executed, this attack reveals the entire private RSA key after a
large number of attack messages (> 600.000 on a local machine) are sent to
show the timing differences.

## Workaround

Disable CRT (`#define POLARSSL_RSA_NO_CRT`) in _config.h_. Your code will be
much slower, but unaffected by this attack.

## Resolution

Upgrade to PolarSSL version 1.3.0 of 1.2.9.

## Advice

We strongly advise you to consider upgrading to the 1.3 branch if outside
parties are present or can connect to your network.

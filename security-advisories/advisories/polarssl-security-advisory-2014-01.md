# PolarSSL Security Advisory 2014-01

**Title** |  Heartbleed Bug
---|---
**CVE** |  CVE-2014-0160
**Date** |  8th of April 2014
**Affects** |  PolarSSL not affected
**Not affected** |  All version of PolarSSL
**Impact** |  Recovery of the key material
**Exploit** |  None

There is a lot of news about a new high-impact vulnerability called 'The
Heartbleed Bug' that affects OpenSSL. This Security Advisory is to inform
PolarSSL users about possible impact for them.

_"The Heartbleed Bug is a serious vulnerability in the popular OpenSSL
cryptographic software library. This weakness allows stealing the information
protected, under normal conditions, by the SSL/TLS encryption used to secure
the Internet. SSL/TLS provides communication security and privacy over the
Internet for applications such as web, email, instant messaging (IM) and some
virtual private networks (VPNs)._

_The Heartbleed bug allows anyone on the Internet to read the memory of the
systems protected by the vulnerable versions of the OpenSSL software. This
compromises the secret keys used to identify the service providers and to
encrypt the traffic, the names and passwords of the users and the actual
content. This allows attackers to eavesdrop communications, steal data
directly from the services and users and to impersonate services and users."_
[[1]](http://heartbleed.com/)

The attack has been added to the known attacks in [our Security
Center](/security).

## Impact

No versions of PolarSSL are affected.

In the affected versions of OpenSSL it is possible to retrieve key material
and other data from the server.

## Workaround

**For PolarSSL users:** No workaround needed.

**For OpenSSL users:** Switch to PolarSSL or upgrade to the latest version of
OpenSSL.

## Resolution

**For PolarSSL users:** No workaround needed.

**For OpenSSL users:** Switch to PolarSSL or upgrade to the latest version of
OpenSSL.

### Like this?

**Section:**
Security Advisories

**Author:**
Paul Bakker

**Published:**
Apr 8, 2014

**Last updated:**
Apr 8, 2014
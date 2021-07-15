# Mbed TLS Security Advisory 2018-02

This Security Advisory describes three vulnerabilities, their impact and fixes
for each possible attack.

* * *

**Title** |  Remote plaintext recovery on use of CBC based ciphersuites
through a timing side-channel
---|---
**CVE** |  CVE-2018-0497
**Date** |  25th July 2018
**Affects** |  All versions of Mbed TLS from version 1.2 upwards, including
all 2.1, 2.7 and later releases
**Impact** |  Allows a remote attacker to partially recover the plaintext
**Severity** |  High
**Credit** |  Kenny Paterson, Eyal Ronen and Adi Shamir

## Vulnerability

When using a CBC based ciphersuite, a remote attacker can partially recover
the plaintext. To be able to mount an attack, the attacker requires the
following:

  * to be able to observe and manipulate network packets
  * for TLS, to be able to generate multiple sessions where the same plaintext is sent. For DTLS a single session is sufficient

The attacker can then partially recover the plaintext of messages exploiting
timing side-channels. The attack is feasible for all versions of TLS and DTLS,
from 1.0 to 1.2.

With DTLS, the attacker can perform the attack by sending many messages across
the same connection. With TLS or if `mbedtls_ssl_conf_dtls_badmac_limit()` was
used, the attack only works if the same secret (for example a HTTP cookie) has
been repeatedly sent over connections manipulated by the attacker.

The vulnerability was caused by a miscalculation for SHA-384 in a
countermeasure to the original Lucky 13 attack.

## Impact

If the attacker has the advantage of all the conditions of the attack
described above, they can potentially at least partially recover the plaintext
sent in the connection.

## Resolution

Affected users should upgrade to one of the most recent versions of Mbed TLS,
including 2.12.0, 2.7.5 or 2.1.14 or later.

## Workaround

Where possible, we recommend all users upgrade to a newer version of Mbed TLS.

If this is not possible, as a workaround, we recommend disable CBC based
ciphersuites from your configuration. Connections using GCM or CCM instead of
CBC, or using hash sizes other than SHA-384, or using Encrypt-then-Mac ([RFC
7366](https://tools.ietf.org/html/rfc7366)) are not affected.

* * *

**Title** |  Plaintext recovery on use of CBC based ciphersuites through a
cache based side-channel
---|---
**CVE** |  CVE-2018-0498
**Date** |  25th July 2018
**Affects** |  All versions of Mbed TLS from version 1.2 upwards, including
all 2.1, 2.7 and later releases
**Impact** |  Allows partial recovery of the plaintext
**Severity** |  High
**Credit** |  Kenny Paterson, Eyal Ronen and Adi Shamir

## Vulnerability

When using a CBC based ciphersuite, an attacker with the ability to execute
arbitrary code on the machine under attack can partially recover the plaintext
by use of cache based side-channels. To be able to mount an attack, the
attacker requires the following:

  * the ability to execute arbitrary code on the machine under attack
  * to be able to observe and manipulate network packets

The attacker can then partially recover the plaintext of messages exploiting
timing side-channels. The attacks are feasible for all versions of TLS and
DTLS, from 1.0 to 1.2.

Two attacks are possible - an attack targeting an internal message digest
buffer and an attack targeting the TLS input record buffer.

With DTLS, the attacker can perform the attack by sending many messages across
the same connection. With TLS or if `mbedtls_ssl_conf_dtls_badmac_limit()` was
used, the attack only works if the same secret (for example a HTTP cookie) has
been repeatedly sent over connections manipulated by the attacker

## Impact

If the attacker has the advantage of all the conditions of the attack
described above, they can potentially at least partially recover the plaintext
sent in the connection.

## Resolution

Affected users should upgrade to one of the most recent versions of Mbed TLS,
including 2.12.0, 2.7.5 or 2.1.14 or later.

## Workaround

Where possible, we recommend all users upgrade to a newer version of Mbed TLS.

If this is not possible, as a workaround, we recommend disable CBC based
ciphersuites from your configuration. Connections using GCM or CCM instead of
CBC, or using hash sizes other than SHA-384, or using Encrypt-then-Mac ([RFC
7366](https://tools.ietf.org/html/rfc7366)) are not affected.

We also recommend all users ensure any machine or device hosting Mbed TLS is
properly secure:

  * Maintain up-to-date systems with the latest security updates from the operating system vendor, and if necessary, any microcode updates issued by the processor vendor.
  * Ensure you follow security best practices and guidelines. For example, do not run any unstrusted software.

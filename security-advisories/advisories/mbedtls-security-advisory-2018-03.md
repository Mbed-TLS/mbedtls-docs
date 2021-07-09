# Mbed TLS Security Advisory 2018-03

**Title** |  Local timing attack on RSA decryption
---|---
**CVE** |  CVE-2018-19608
**Date** |  30th Nov 2018
**Affects** |  All versions of Mbed TLS
**Impact** |  Allows a local _unprivileged_ attacker to recover the plaintext
of RSA decryption, which is used in RSA-without-(EC)DH(E) cipher suites
**Severity** |  High
**Credit** |  Eyal Ronen (Weizmann Institute), Robert Gillham (University of
Adelaide), Daniel Genkin (University of Michigan), Adi Shamir (Weizmann
Institute), David Wong (NCC Group), and Yuval Yarom (University of Adelaide
and Data61).

## Vulnerability

An attacker who can run code on the same machine that is performing an RSA
decryption can potentially recover the plaintext through a Bleichenbacher-like
oracle ([ _The 9 Lives of Bleichenbacher’s CAT: New Cache ATtacks on TLS
Implementations_](http://cat.eyalro.net/)). To mount the attack, the attacker
needs:

  * a ciphertext that they want to decrypt;
  * the ability to submit modified ciphertexts for decryption;
  * the ability to run code on the same machine while Mbed TLS is decrypting the modified ciphertexts.

In particular, this affects (D)TLS connections that use a cipher suite that
uses RSA decryption (these are cipher suites whose name includes RSA but not
DH, DHE, ECDH or ECDHE). If the attacker is able to record the encrypted
connection and to mount the ciphertext recovery attack against the server,
they can decrypt the connection. If the attacker is able to intercept the
connection, they may be able to perform a man-in-the-middle attack on the
content.

The ciphertext recovery is made possible by two information leaks in the RSA
decryption routine. An attacker who can execute code on the same machine as
the decryption may observe branch prediction patterns and data or code memory
access patterns. The vulnerabilities leak the size of the decrypted value or
the content of the padding, which allows the attacker to obtain up to one bit
of information about the plaintext for their chosen ciphertext, and by
combining information about multiple chosen ciphertexts the attacker can
recover the plaintext for the original ciphertext.

## Impact

If the attacker has the advantage of all the conditions of the attack
described above, they can potentially decrypt plaintexts encrypted with RSA.
Furthermore, if the same RSA key is used for both decryption and signature,
the attacker is able to use this vulnerability to forge a signature.

In particular, an attacker _who can run unprivileged code on a (D)TLS server_
can decrypt connections _to that server_ that use a cipher suite based on RSA
decryption. _If the attacker can perform a man-in-the-middle attack, they can
downgrade connections to an affected cipher suite if the client is willing to
use one. Furthermore, if the server uses the same RSA private key for
encryption and signature, the attacker can use this vulnerability to forge a
signature and thus affect even clients that do not accept cipher suites based
on RSA decryption._

## Resolution

Affected users should upgrade to one of the most recent versions of Mbed TLS,
including 2.14.1, 2.7.8 or 2.1.17 or later.

Up-to-date versions of Mbed TLS remain vulnerable to one of the leaks if the
size of the RSA key is not a multiple of the machine word size. We recommend
that you use key sizes that are a multiple of 64 bits.

## Workaround

Where possible, we recommend all impacted users upgrade to a newer version of
Mbed TLS.

If this is not possible, as a workaround, we recommend that you disable _all_
cipher suites using RSA decryption from your configuration. Cipher suites that
use RSA signature combined with (EC)DH(E) are not affected.

In all cases, we recommend that you use key sizes that are a multiple of 64
bits. We also recommend not to use the same key for decryption and for
signature.

### Like this?

**Section:**
Security Advisories

**Author:**
Janos Follath

**Published:**
Nov 28, 2018

**Last updated:**
Dec 4, 2018
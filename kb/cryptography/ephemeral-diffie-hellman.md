# Why use Ephemeral Diffie-Hellman

## Ephemeral Diffie-Hellman vs static Diffie-Hellman

**Ephemeral Diffie-Hellman** (DHE in the context of TLS) differs from the **static Diffie-Hellman** (DH) in the way that static Diffie-Hellman key exchanges always use the same Diffie-Hellman private keys. So, each time the same parties do a DH key exchange, they end up with the same shared secret.

When a key exchange uses Ephemeral Diffie-Hellman a temporary DH key is generated for every connection and thus the same key is never used twice. This enables **Forward Secrecy** (FS), which means that if the long-term private key of the server gets leaked, past communication is still secure.

This distinction also holds for the Elliptic Curve variants ECDHE (ephemeral, provides Forward Secrecy) and ECDH (static).

Due to increasing concern about pervasive surveillance, key exchanges that provide Forward Secrecy are recommended, see for example [RFC 7525, section 6.3](https://tools.ietf.org/html/rfc7525#section-6.3).

## Authentication

Ephemeral Diffie-Hellman doesn't provide authentication on its own, because the key is different every time. So neither party can be sure that the key is from the intended party.

Within SSL you will often use DHE as part of a key-exchange that uses an additional authentication mechanism (e.g. **RSA**, **PSK** or **ECDSA**). So the fact that the SSL server **signs** the content of its server key exchange message that contain the ephemeral public key implies to the SSL client that this Diffie-Hellman public key is from the SSL server.

## Ciphersuites supporting Ephemeral Diffie-Hellman

There are a lot of ciphersuites that support Ephemeral Diffie-Hellman. The key exchange methods that use (EC)DHE in TLS are:

- Ephemeral Diffie Hellman with RSA (DHE-RSA) key exchange
- Elliptic Curve Ephemeral Diffie Hellman with RSA (ECDHE-RSA) key exchange
- Elliptic Curve Ephemeral Diffie Hellman with ECDSA (ECDHE-ECDSA) key exchange
- Pre Shared Key with Diffie Hellman (DHE-PSK) key exchange
- Pre Shared Key with Elliptic Curve Diffie Hellman (ECDHE-PSK) key exchange
The full list of ciphersuites can be found in our [list of supported SSL ciphersuites](/supported-ssl-ciphersuites).

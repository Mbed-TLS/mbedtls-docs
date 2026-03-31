# Client impersonation while resuming a TLS 1.3 session (CVE-2026-34873)

**Title** | Client impersonation while resuming a TLS 1.3 session
--------- | -----------------------------------------------------
**CVE** | CVE-2026-34873
**Date** | 31 March 2026
**Affects** | Mbed TLS versions 3.5.0 up to and including 3.6.5, and 4.0.0
**Impact** | Client impersonation
**Severity** | HIGH
**Credits** | Jaehun Lee, Pohang University of Science and Technology (POSTECH)

## Vulnerability

When a TLS 1.2- and TLS 1.3-capable Mbed TLS server is requested to resume a
TLS 1.3 session using a ticket and responds with a HelloRetryRequest message,
if the subsequent ClientHello negotiates TLS 1.2 (for example, because it does
not include the supported_versions extension), the server incorrectly proceeds
to resume a TLS 1.2 session using an all-zero master secret.

A man-in-the-middle attacker who intercepts the HelloRetryRequest and replies
with a ClientHello negotiating TLS 1.2 may then be able to complete the
handshake that was originally initiated using a TLS 1.3 ticket.

As a result, a TLS 1.2- and TLS 1.3-capable Mbed TLS server configured to
authenticate connecting clients may fail to provide the authentication
guarantees expected by the application operating it.

## Impact

Under the conditions described above, a man-in-the-middle attacker may be able
to bypass the client authentication mechanisms configured in the Mbed TLS server.

If the application relies solely on the successful establishment of a TLS
connection for client authentication, an attacker may be able to impersonate a
legitimate client.

Finally, if the application provides its own implementation of session ticket
handling via the `mbedtls_ssl_ticket_write_t` and `mbedtls_ssl_ticket_parse_t`
callbacks and encodes additional application-level information in tickets
beyond the negotiated TLS session parameters and client identity (for example,
authorization state or access rights), an attacker able to complete the resumed
handshake described above may inherit the same application-level privileges as
the legitimate client whose ticket was used.

## Affected versions

Mbed TLS versions 3.5.0 up to and including 3.6.5, and 4.0.0

## Work-around

Based on our current analysis, an application operating an Mbed TLS server
appears to be vulnerable only if all of the following conditions are met:
. The server supports both TLS 1.2 and TLS 1.3.
. The server is configured to authenticate clients.
. The server issues TLS 1.3 session tickets to authenticated clients for later
  session resumption.

Furthermore, if the Mbed TLS server does not respond with a HelloRetryRequest
message when an authenticated client attempts to resume a TLS 1.3 session using
a ticket, the issue does not appear to be exploitable. This is typically the
case if the server always supports at least one of the groups proposed in the
key_share extension of the ClientHello used for TLS 1.3 session resumption.

If the server may respond with a HelloRetryRequest under the above conditions,
the impact can be mitigated through configuration choices, including:

. Disabling “PSK with (EC)DHE” key establishment.
This can be done at build time by disabling the configuration option
`MBEDTLS_SSL_TLS1_3_KEY_EXCHANGE_MODE_PSK_EPHEMERAL_ENABLED`, and at runtime
via the `mbedtls_ssl_conf_tls13_key_exchange_modes()` API.
In this configuration, only “PSK-only” key establishment is enabled.
Note that this mode does not provide forward secrecy.

. Disabling session ticket generation.
This can be done at build time by disabling the `MBEDTLS_SSL_SESSION_TICKETS`
configuration option, and at runtime by configuring the server to send zero
NewSessionTicket messages after handshake completion using the
`mbedtls_ssl_conf_new_session_tickets()` API.

## Resolution

Affected users of the 3.6 LTS branch should upgrade to 3.6.6 or later.
Affected users of the 4.x series should upgrade to 4.1.0 or later.

## Fix commits

We recommend that users upgrade to a release including the fix. However, if you are maintaining a branch with backported bug fixes, here are the most relevant commits. Please note that these commits may not apply cleanly to older versions of the library, and may not provide a complete fix even if they do apply. The Mbed TLS development team does not provide support outside of maintained branches.

| Branch | Mbed TLS 3.6.x | TF-PSA-Crypto 1.x | Mbed TLS 4.x |
| ------ | -------------- | ----------------- | ------------ |
| Basic fix | 365a16dc384203f8a75982cc4b47e20e804b2d1a,500c155de96607445783a83c35365a9473512d65 | N/A | ed767bada9108fb7e15a1012f384a08e2cd637f2,8731587e41379e8ea5cd7ddda7e418059947ed7a |
| With tests and documentation | branch up to 0d48c34169a1235c5656c968019027d32e7aad40 | N/A | branch up to d8868c432fcf2cea29922fcb51c5892c1d3536f2 |

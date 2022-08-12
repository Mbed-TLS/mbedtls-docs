# Mbed TLS over low-bandwidth, unreliable datagram networks

This article reviews the following topics:

1. [Configuring Mbed TLS in networks with low MTU](#configuring-mbed-tls-in-networks-with-low-mtu): using `mbedtls_ssl_set_mtu()` to configure the _Maximum Transmission Unit_ (MTU).
1. [Negotiating a maximum message size with the peer](#negotiating-a-maximum-message-size-with-the-peer): using `mbedtls_ssl_conf_max_frag_len()` to configure the _Maximum Fragment Length_ (MFL).
1. [Comparing MTU and MFL](#comparing-mtu-and-mfl): highlighting the differences between MTU and MFL.
1. [Reducing memory footprint in Mbed TLS version 2.x](#reducing-ram-usage-for-internal-message-buffers): using `MBEDTLS_SSL_IN_CONTENT_LEN` and `MBEDTLS_SSL_OUT_CONTENT_LEN` to determine the size of internal input and output buffers.
1. [Configuring Mbed TLS in networks with high loss rates](#configuring-mbed-tls-in-lossy-networks): using `MBEDTLS_SSL_DTLS_MAX_BUFFERING` and `mbedtls_ssl_set_datagram_packing()` to control two features improving DTLS
   handshake reliability.

<span class="notes">**Note:** This article is _not_ meant as an introduction to Mbed TLS; you can find that in the separate [Mbed TLS tutorial](/kb/how-to/mbedtls-tutorial.md). Also, this article is about _DTLS only_ (the MFL extension exists in TLS, too, but currently Mbed TLS does not comprehensively support it), and it assumes that you are familiar with what DTLS is, why you would want to use it, and how to configure Mbed TLS to implement it. If you are looking for answers to those questions, please see the [DTLS tutorial](/kb/how-to/dtls-tutorial.md).</span>

## Configuring Mbed TLS in networks with low MTU

### Background: The Maximum Transmission Unit (MTU)

The maximum size of packets that a specific network connection is able to handle is commonly called the _maximum transmission unit_, or _MTU_ for short. If a message needs to be sent whose size exceeds the MTU, this requires a higher layer protocol in the networking stack. This protocol is aware of the MTU limitation, and is able to split the message into sufficiently small fragments on the sender side, then reassemble those fragments on the receiving side. For example, if an [IPv4](https://en.wikipedia.org/wiki/IPv4) router finds an IPv4 packet too large for the link layer, which transports it to its destination, the router may fragment the packet (or refine existing fragmentation) before passing it to the link layer. In contrast, [IPv6](https://en.wikipedia.org/wiki/IPv6) fragmentation during routing is not allowed, and an IPv6 router will drop a packet that is too large to be passed to the underlying link layer; instead, IPv6 fragmentation must happen at the endpoints or be handled by an upper layer protocol. The minimum requirement for implementation is an MTU of 576 bytes for IPv4 and 1280 bytes for IPv6. In that regard, note that even though the IPv4 and IPv6 specifications provide methods for fragmentation at the endpoints, constrained devices might use implementations that do not support those, and only provide these minimal MTU requirements.

We must therefore consider that DTLS may use a handshake message of a size larger than the MTU of the datagram transport it is based on. For example, the `Certificate` and `NewSessionTicket` messages can be larger than the IPv4 / IPv6 MTUs mentioned in the previous paragraph. To still allow the use of DTLS over such datagram links, [DTLS RFC 6347, Section 4.2.3](https://tools.ietf.org/html/rfc6347#section-4.2.3) specifies a mechanism for fragmentation and reassembly of handshake messages. This allows reducing the size of datagrams passed to the underlying datagram link to below the link's MTU. This assumes, though, that the DTLS implementation is aware of the MTU limitation of the underlying datagram link, so the next section explains how the user can inform Mbed TLS about it.

### Setting the MTU of the underlying datagram link

The value of the underlying datagram link's MTU - or a safe under-approximation of it - may be configured through the API call:

```
mbedtls_ssl_set_mtu()
```

This function may be called at any point during the lifetime of an SSL context, depending on when information about the underlying datagram link's MTU becomes available or gets updated (for example, when the rate of package loss indicates that your MTU configuration is too large). It takes effect immediately, ensuring that no datagram of a size exceeding the MTU is sent, and fragmenting handshake messages if necessary to guarantee this.


For example, to set the initial MTU value used for the handshake, the function should be called after the SSL context has been set up using `mbedtls_ssl_setup()`, but before performing the handshake using `mbedtls_ssl_handshake()`. This is exemplified in the [ssl_server2](https://github.com/ARMmbed/mbedtls/blob/development/programs/ssl/ssl_server2.c) and [ssl_client2](https://github.com/ARMmbed/mbedtls/blob/development/programs/ssl/ssl_client2.c) example programs.

### Getting the maximum application data size

The API call `mbedtls_ssl_set_mtu()` informs Mbed TLS about the MTU of the underlying datagram link, but a natural question from the perspective of the user is what the 'outgoing' MTU of the DTLS connection itself is; that is, what is the maximum size of (unprotected) application datagrams that the DTLS connection can send.

In that regard, it is important to note that the DTLS fragmentation mechanism referred to above applies to the DTLS-internal handshake messages only. In contrast, no fragmentation mechanism for application datagrams sent and received by the user is built into DTLS. An MTU restriction on the underlying datagram link directly restricts the MTU of the DTLS connection from the perspective of the application layer: The MTU of the DTLS connection is smaller than the datagram link's MTU by at least the overhead for DTLS headers and encryption as determined by `mbedtls_ssl_get_record_expansion()` (However, note that it can be larger, for example due to the use of the maximum fragment length configuration discussed below).

The maximum application data size of a DTLS connection can be queried using the API call:

```
mbedtls_ssl_get_max_out_record_payload()
```

The library guarantees that application datagrams of a size not exceeding this value can be sent through the DTLS connection to reach the peer's DTLS stack (provided the MTU value configured through `mbedtls_ssl_set_mtu()` is valid). In contrast, if the user attempts to send larger application datagrams, the corresponding call to `mbedtls_ssl_write()` fails.

It is the responsibility of the application layer protocol to implement fragmentation of application data, if necessary, to ensure that the data it passes to `mbedtls_ssl_write()` is within the bounds set by `mbedtls_ssl_get_max_out_record_payload()`.

## Negotiating a maximum message size with the peer

### Background

The value of `mbedtls_ssl_get_max_out_record_payload()` indicates the maximum size of outgoing application datagrams, but it does not bound the size of _incoming_ application datagrams. The latter may be larger, as MTU values set by `mbedtls_ssl_set_mtu()` may be a strict under-approximation of the underlying datagram link's capabilities. For example, we might think the MTU is 512 bytes, when it is in fact 1024 bytes, while the peer might use a larger, yet still valid, approximation to the MTU, say, 800 bytes. In this case, we might receive datagrams of up to 800 bytes, even though we estimated the MTU as 512 bytes. This is acceptable as long as both parties use valid estimates of the datagram link's MTU _and_ have enough memory to store incoming and outgoing messages.

Constrained devices, however, might not have enough available RAM to store incoming messages of a size up to the underlying datagram link's MTU. For example, if the datagram link uses its own fragmentation mechanism to allow sending of packets of size 16K, that doesn't mean the DTLS stack has enough RAM to handle them. If a DTLS stack limits the size of incoming datagrams it is willing to accept because of RAM limitations, this might lead to messages from the peer being dropped even if the peer has properly configured the underlying MTU through `mbedtls_ssl_set_mtu()` and did not send packets larger than what `mbedtls_ssl_get_max_out_record_payload()` returns.

As a remedy, the communicating parties need to negotiate the maximum size of the datagrams they exchange. One such mechanism is provided by the _maximum fragment length extension_ (MFL) of DTLS, specified in [RFC 6066, Section 4](https://tools.ietf.org/html/rfc6066#section-4). This extension lets the client suggest the maximum size of datagram payloads that can be sent during the communication. The possible values are 512, 1024, 2048 and 4096 bytes. If the server consents to it, it must only send messages of a size not exceeding the client's MFL value.

Note that the server cannot suggest a different MFL value; if it knows about the MFL extension, it can only consent to the client's suggestion or abort the handshake. The [Record Size Limit Extension, RFC 8449](https://tools.ietf.org/html/rfc8449) aims to
correct this asymmetry, but is not yet implemented in Mbed TLS.

### Using the maximum fragment length (MFL) extension in Mbed TLS

Use of the MFL extension is controlled through the API call:

```
mbedtls_ssl_conf_max_frag_len()
```

Its semantics is very different depending on the caller (client or server), due to the asymmetry of the MFL extension:

* If called by the **client**, `mbedtls_ssl_conf_max_frag_len()` prevents the exchange of datagram payloads of a size exceeding the respective MFL value, _provided_ that the server supports the MFL extension and explicitly consents to the client's request. If the server is aware of the extension but doesn't explicitly acknowledge the client's request, the connection fails; if the server doesn't know the extension or does not respond to it, the connection continues without any guarantees for the client (see the example below).
    Mbed TLS does not provide an API call to determine if the server consented to an MFL request.
* If called by the **server**, `mbedtls_ssl_conf_max_frag_len()` bounds the server's maximum outgoing payload size. If the client requests a smaller MFL value, the server will accept it and not send payloads larger than the client's MFL value. However, as mentioned in the previous section, the server has no means of requesting the use of smaller packets from the client (when the server's MFL value is lower then the client's MFL value).

Note that on the server, `mbedtls_ssl_conf_max_frag_len()` is very similar to `mbedtls_ssl_set_mtu()`, the difference being that the MFL is about payload size before encryption and adding DTLS headers, while `mbedtls_ssl_set_mtu()` is about the final datagram size.

The MFL values that `mbedtls_ssl_conf_max_frag_len()` accepts are those defined in the standard: 512, 1024, 2048 and 4096 bytes. If `mbedtls_ssl_conf_max_frag_len()` is not called, the MFL defaults to the minimum of the size of the internal incoming and outgoing datagram buffers as configured by `MBEDTLS_SSL_IN_CONTENT_LEN` and `MBEDTLS_SSL_OUT_CONTENT_LEN`, respectively, which is at most 16384 bytes (the maximum record payload size according to the TLS/DTLS standards, see for example [TLS 1.2 RFC 5246, Section 6.2.1](https://tools.ietf.org/html/rfc5246#section-6.2.1) and [DTLS 1.2 RFC 6347, Section 3.2.3](https://tools.ietf.org/html/rfc6347#section-3.2.3)). In particular, unconstrained applications not wishing to restrict the MFL should not call
`mbedtls_ssl_conf_max_frag_len()`, because the MFL extension does not support values above 4096 bytes (one of the limitations leading to development of the [Record Size Limit Extension, RFC 8449](https://tools.ietf.org/html/rfc8449).

Examples:

* The server is unconstrained and doesn't call `mbedtls_ssl_conf_max_frag_len()`, but supports the MFL extension; the client has limited RAM and calls `mbedtls_ssl_conf_max_frag_len()` with an MFL value of 2048 bytes.

    Subsequently, all messages between client and server have a payload size of 2048 bytes at most.

* The server is unconstrained and doesn't support the MFL extension; the client has limited RAM and calls `mbedtls_ssl_conf_max_frag_len()` with an MFL value of 2048 bytes. In this case, no restriction applies to the size of messages sent from the server to the client.

    Potential consequences: On the one hand, the handshake might fail, for example when the server sends a certificate larger than 2KB (which the client cannot handle). On the other hand, even if the handshake succeeds, server packets of size > 2KB are dropped, resulting in a connection that may be unreliable or even unusable (depending on the amount of such packets, as well as the tolerance and adaptation mechanisms of the application layer protocol towards packet loss).

* The server and client are constrained to MFLs of 4096 bytes and 1024 bytes, respectively. The client takes precedence, and all messages subsequently sent between client and server have a payload size of 1024 bytes at most.

* The server and client are constrained to MFLs of 1024 bytes and 4096 bytes, respectively. The server has no way to lower the client's request from 4096 bytes to 1024 bytes, and must therefore either abort the connection or accept the client's MFL of 4096 bytes. In the latter case, the same remarks as in the second example apply in regards to potential handshake failure or unreliability of the resulting connection.

You can query the currently configured or negotiated MFL value through the API call:

```
mbedtls_ssl_get_max_frag_len()
```

For the **client**, this will always return the value configured in `mbedtls_ssl_conf_max_frag_len()` (or the default value mentioned above if the function hasn't been called). For the **server**, it returns the smaller of the values configured through `mbedtls_ssl_conf_max_frag_len()` and the one requested by the client (if any).

Note that `mbedtls_ssl_get_max_frag_len()` should not be used to determine the maximum datagram payload, as it does not take the configured MTU into consideration. Instead, you should always call `mbedtls_ssl_get_max_out_record_payload()` to determine the maximum application data size the stack is able to handle, which takes both MTU and MFL settings into account.

## Comparing MTU and MFL

The **underlying datagram link's MTU**, as set through `mbedtls_ssl_set_mtu()`, guards only the _total_ size of _outgoing_ datagrams; it does _not_ control the size of incoming datagrams. Because the total datagram size includes overhead for headers and encryption, the bound `mbedtls_ssl_set_mtu()` sets on the _payload_ of outgoing datagrams is strictly smaller than the MTU value, by (at most) `mbedtls_ssl_get_record_expansion()`.

For the **client**, the MFL as configured by `mbedtls_ssl_conf_max_frag_len()` guards the _payload_ size of both _incoming and outgoing_ datagrams (provided the server supports the MFL extension and acknowledges the client's request). The MFL is strictly smaller than the maximum datagram size, because of overhead from headers and protection. In particular, an MFL of 512 bytes can still lead to exchange of datagrams or records of about ~550 bytes.

For the **server**, the MFL as configured by `mbedtls_ssl_conf_max_frag_len()` guards the _payload_ size of _outgoing datagrams only_. The client is not informed about this limitation and hence need not obey it. Therefore, `mbedtls_ssl_conf_max_frag_len()`, which applies to the payload, is roughly equivalent to `mbedtls_ssl_set_mtu()`, which applies to the _total_ datagram size.

When both MFL and MTU are configured, the guards are applied independently. For example, say a client configures an MFL of 512 bytes and an MTU of 512 bytes. The stack will not send datagrams larger than 512 bytes due to the MTU setting. But, it may receive datagrams slightly larger than 512 bytes, since the MFL only restricts the server to
512 bytes of payload.

In DTLS, the maximum datagram payload size, as determined by both the MTU and the MFL setting, can be queried by `mbedtls_ssl_get_max_out_record_payload()`, and must be obeyed by both client and server. Datagrams exceeding this size will be rejected by `mbedtls_ssl_write()`.

## Reducing RAM usage for internal message buffers

As of Mbed TLS 2.13, the library uses separate, statically-sized buffers for processing incoming and outgoing messages. They are user-configurable compile-time constants in `mbedtls/config.h`. The user sets their size so that they can hold arbitrarily protected records with payload size `MBEDTLS_SSL_IN_CONTENT_LEN` (for incoming records) or `MBEDTLS_SSL_OUT_CONTENT_LEN` (for outgoing records).

It is tempting to assume that any reduction of MTU and MFL would allow saving RAM by reducing `MBEDTLS_SSL_IN_CONTENT_LEN` and `MBEDTLS_SSL_OUT_CONTENT_LEN`, but you must consider the following points:

1. Both incoming and outgoing handshake messages are currently prepared in a contiguous buffer, regardless of whether they are being fragmented before sending, or reassembled after receiving (this might change in a future version of Mbed TLS). Hence, `MBEDTLS_SSL_IN_CONTENT_LEN` and `MBEDTLS_SSL_OUT_CONTENT_LEN` must not be smaller than the maximum expected size of handshake messages during connection setup. Judging from [RFC 6347, Section 4.2.2](https://tools.ietf.org/html/rfc6347#section-4.2.2), handshake messages may be up to 16Mb in size, but estimates of their _realistic_ size should be based on the following:

   1. Are certificates used? If so, what algorithms are supported (RSA keys are longer than ECDSA ones), and how long do we expect certificate chains to be? On a generic stack making no assumptions about the kind and length of certificate chains of the peer, it must be considered that they are a few KB in length.
   1. Are session tickets used? If so, how large are they?
1. Outgoing application data packets must fit in the outgoing data buffer. Hence, `MBEDTLS_SSL_OUT_CONTENT_LEN` must not be smaller than the maximum application packet size used by the application layer protocol.
1. As long as the first two points are obeyed, no further constraints apply to `MBEDTLS_SSL_OUT_CONTENT_LEN` to guarantee that handshake and application data messages can be sent. In particular, you may configure `MBEDTLS_SSL_OUT_CONTENT_LEN` to be smaller than the MTU and MFL settings. However, for unreliable networks, consider choosing a larger value for `MBEDTLS_SSL_OUT_CONTENT_LEN` nonetheless, to allow [datagram packing](#packing-multiple-messages-in-a-single-datagram). Still, it is not sensible to increase `MBEDTLS_SSL_OUT_CONTENT_LEN` beyond the minimum of MTU and MFL, if configured.
1. As long as the first point is obeyed and `MBEDTLS_SSL_IN_CONTENT_LEN` is large enough to hold any incoming handshake message (after reassembly), and if it is known that the server supports the MFL extension, the _client_ may reduce `MBEDTLS_SSL_IN_CONTENT_LEN` to the value of the MFL extension (if used). We don't recommend reducing `MBEDTLS_SSL_IN_CONTENT_LEN` without using the MFL extension, as no other means are currently available to inform the peer about the size limitation. The _server_ usually may not reduce `MBEDTLS_SSL_IN_CONTENT_LEN` based on the value of the MFL extension, unless it knows about the maximum size of messages sent by the client through some other means. This is, again, due to the asymmetry in the MFL extension, and will be solved with the introduction of the Record Size Limit extension mentioned above.

## Configuring Mbed TLS in lossy networks

### Packing multiple messages in a single datagram

In DTLS, Mbed TLS offers packing multiple handshake messages in a single datagram (if space permits). This reduces the likelihood of message reordering, hence the likelihood of retransmissions, and hence the expected time to set up a DTLS connection. This _datagram packing_ feature is enabled by default and is controlled by the API function

```
mbedtls_ssl_set_datagram_packing()
```

Datagram packing should only be disabled for testing purposes, or if the peer does not support it.

### Caching out-of-order messages

DTLS handshake messages must be sent and processed in order, but may get reordered in transit (because UDP doesn't guarantee ordered delivery). Mbed TLS offers to cache future messages until they become relevant, instead of dropping them and enforcing a flight retransmission.

Caching future messages is implemented alongside reassembly of fragmented messages, and the maximum amount of RAM used for both reassembly and caching is controlled by the compile-time option

```
MBEDTLS_SSL_DTLS_MAX_BUFFERING
```

The default value is 32KB.

The configuration of `MBEDTLS_SSL_DTLS_MAX_BUFFERING` is a trade off between memory usage, network load and handshake efficiency:

1. Higher values allow to buffer more messages, thereby reducing the number of retransmission and the time until the connection has been established. Saturation happens when the value is large enough to allow for simultaneous reassembly of all messages within any flight. In this case, retransmission is only necessary on packet loss (in which case it is unavoidable).
1. Lower values reduce the RAM usage, but can lead to future messages being dropped, thereby forcing retransmission, which increases both the network load and the handshake time. When the value is too low to allow reassembly of each handshake message individually, handshakes with peers that need to send large, fragmented messages become impossible.

Numerically, these maximal and minimal sensible values of `MBEDTLS_SSL_DTLS_MAX_BUFFERING` can be approximated as follows:

1. Define `MBEDTLS_SSL_DTLS_MAX_BUFFERING` as twice the value of `MBEDTLS_SSL_IN_CONTENT_LEN`. This should be sufficient to buffer all the messages that require buffering, based on the heuristic that there is usually only a single large message in a flight, say of maximum size `MBEDTLS_SSL_IN_CONTENT_LEN`. The default value of `MBEDTLS_SSL_DTLS_MAX_BUFFERING`, 32KB, is chosen according to this heuristic, with the default value of `MBEDTLS_SSL_IN_CONTENT_LEN` being 16KB.
1. Because `MBEDTLS_SSL_DTLS_MAX_BUFFERING` bounds the size of the reassembly buffer, it must be at least as large as the largest expected incoming handshake message (which was mentioned above as also providing a lower bound for `MBEDTLS_SSL_IN_CONTENT_LEN`), and also account for internal reassembly state overhead, which is usually 12 bytes + 1/8 of the message size. Hence, unless it is known that the peer does not use handshake fragmentation, we recommend not configuring a value lower than `9/8 MBEDTLS_SSL_IN_CONTENT_LEN + 12` for this option.

Finally, note that Mbed TLS dynamically allocates space for caching and reassembly on demand only. In particular, while `MBEDTLS_SSL_DTLS_MAX_BUFFERING` controls the peak of RAM usage, the actual amount of RAM needed for reassembly and caching in an ordinary connection is much less, depending on the reliability of the network. However, an adversary attempting a DoS attack might purposefully trigger maximum RAM usage.

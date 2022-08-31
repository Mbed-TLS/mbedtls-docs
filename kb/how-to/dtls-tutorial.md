# Using DTLS

## Introduction

This tutorial introduces the specifics of using DTLS (as opposed to TLS) with Mbed TLS. It assumes you're familiar with using TLS connections with Mbed TLS, otherwise, we recommend starting with the [Mbed TLS tutorial](mbedtls-tutorial.md).

## Short version

* Register timer callbacks and context with `mbedtls_ssl_set_timer_cb()`.
  * Suitable callbacks for blocking I/O are provided in `timing.c`.
    * For event-based I/O, you need to write your own callbacks based on your event framework.
* Server-side, register cookie callbacks with `mbedtls_ssl_conf_dtls_cookie()`.
   * An implementation is provided in `ssl_cookie.c` and requires context set up with `mbedtls_ssl_cookie_setup()`.

If you prefer to begin with code right away, you can skip to our `dtls_client.c` and `dtls_server.c` examples in the `programs/ssl` directory. However, this article provides more background information, so we recommend reading it in order to make more informed choices.

## Protocol differences and additional settings

TLS usually runs on top of TCP and provides the same guarantees as TCP, in addition to authentication, integrity, and confidentiality.

Like TCP, it delivers a **stream** of bytes in order and does **not** preserve packet boundaries. DTLS usually runs on top of UDP, and once the handshake is finished, provides the same guarantees as UDP as well as authentication, integrity, and confidentiality.

Just like UDP, it delivers **datagrams** of bytes. Some datagrams may be lost or re-ordered, but unlike UDP, DTLS can detect and discard duplicated datagrams if needed. In Mbed TLS, this is controlled by the compile-time flag **MBEDTLS_SSL_DTLS_ANTI_REPLAY** and the run-time setting `mbedtls_ssl_conf_dtls_anti_replay()`, both enabled by default.

With TLS, when a record is received that does not pass the integrity check, the connection is immediately terminated. This denies attackers an opportunity to do more than one guess at the message authentication key, without introducing any new DoS vectors (injecting bad records is just as hard as injecting a TCP RST to tear down the connection).

However, with DTLS over UDP, injecting bad records is very easy (an attacker only needs to know the source and destination IP and port), so the DTLS standard, [section 4.1.2.7](https://tools.ietf.org/html/rfc6347#section-4.1.2.7) recommends not to tear down the connection.

In Mbed TLS, it is possible to set a limit to the number of bad records before the connection is torn down; this is controlled by the compile-time flag **MBEDTLS_SSL_DTLS_BADMAC_LIMIT** (enabled by default) and the run-time setting `mbedtls_ssl_conf_dtls_badmac_limit()` (unlimited by default).

## Retransmission: timer callbacks

The (D)TLS handshake is a lock-step procedure: messages need to arrive in a certain order and cannot be skipped.

To achieve this on top of UDP, DTLS has its own retransmission mechanism, which needs timers. In Mbed TLS, the SSL module accepts a pair of callbacks for timer functions, which can be set using `mbedtls_ssl_set_timer_cb()`. Example callbacks (for Unix and Windows) are provided in `timing.c`, namely `mbedtls_timing_set_delay()` and `mbedtls_timing_get_delay()`, that are suitable for use with blocking I/O.

The callbacks have the following interface:
```
  void mbedtls_timing_set_delay( void *data, uint32_t int_ms, uint32_t fin_ms );
  int mbedtls_timing_get_delay( void *data );
```
In both cases, `data` is a context shared by the callbacks. The **setting** function accepts two delays: an **intermediate** and a **final** one, and the **getting** function tells the caller which of these delays are expired, if any (see the documentation of [`mbedtls_ssl_set_timer_cb()`](/api/ssl_8h.html#a335ee78886daf7f8fb369fa925b3cca8) for details). The final delay is used to indicate when retransmission should happen, while the intermediate delay is an internal implementation detail whose semantic may evolve in future versions.

The interface was designed to allow a variety of implementation strategies, two of which two are:

* Timestamps.
    * The setting function records a timestamp and the values of the delay in the context, and the getting function compares the stored timestamp with the current time.

This is the strategy used by the example callbacks in `timing.c`. It is suitable when you know the application will call `mbedtls_ssl_handshake()` repeatedly until it returns `0` or a fatal error, which is usually the case when using blocking I/O.

* Timers and events.
    * The setting function ensures (for example using a hardware timer or a system call) that a timeout handler will be called when one of the delays expires. This timeout handler needs to at least record the information about which delay expired so that the getting function can return the proper value. For the intermediate delay, this is all you need to do (the information **may** be used internally **if** another event, such as an incoming packet, causes `mbedtls_ssl_handshake()` to be called again before the final delay expires).

For the final delay however, if you are using an event-driven style of programming, the timeout handler needs to generate an event that will cause `mbedtls_ssl_handshake()` to be called again. Our DTLS handshake code will then internally call the `get_delay()` function, notice the delays are expired, and take the appropriate action (either retransmit the last flight of messages or give up on the handshake and return a timeout error).

<span class="notes">**Note:** You need to make sure that calling `set_delay()` while a timer is already running cancels it (more precisely, that no event will be generated when the final delay expires). In particular, after a call like `set_delay(0, 0)`, no timer should be running any more. Said otherwise, there should be at most one running timer at any given time.</span>

<span class="notes">**Note:** If you have multiple concurrent connections, you need to make sure each has its own independent set of timers, and that, when a timeout event is generated for one connection, `mbedtls_ssl_handshake()` is called with the appropriate `ssl_context` for that connection (the `data` argument for the callbacks can be used to store the required information). You also need to avoid making multiple calls to `mbedtls_ssl_handshake()` with the same `ssl_context` at the same time.</span>

With event-based I/O, **don't** use read timeouts by calling `mbedtls_ssl_conf_read_timeout()` with a non-zero value, for two reasons:

* It's unnecessary, as you only call `mbedtls_ssl_read()` when data is ready to be read.
* It makes your timeout handler more complex, as it would have to know whether the timeout happened during handshake or read in order to schedule the appropriate function.

## Retransmission: timeout values

The retransmission delay starts with a minimum value, then doubles on each retransmission until its maximum value is reached, in which case a handshake timeout is reported to the application. The minimum and maximum can be set using `mbedtls_ssl_conf_handshake_timeout()` (default: 1 to 60 seconds).

See [the documentation of this function](https://github.com/Mbed-TLS/mbedtls/blob/edb1a483971c836e84e95d7b73ee39bd6b450675/include/mbedtls/ssl.h#L1300) for the meaning of those values if you need to tune them according to the characteristics of your network in order to achieve optimal performance/reliability. Even if your timeout values are perfectly tuned, your application should still be prepared to see failing handshakes and react appropriately.

<span class="notes">**Note:**: There might seem to be a parallel between `mbedtls_ssl_conf_handshake_timeout()` and `set_delay()` as they both accept two durations as arguments, but this is not the case. The **final delay** will take various values from `min` to `max`, doubling every time, while the **intermediate delay** is an internal implementation detail.</span>

## Server-side only: Cookies for client verification

1. The client starts by sending a `ClientHello` message.

1. The server replies with a series of messages that can be long. These typically include the server's certificate chain.

Without specific protection, this would make it easy for a malicious client to use DTLS servers as amplifiers in DDoS attacks. Since it is trivial to fake the source address of a UDP packet, malicious clients could send a few bytes of `ClientHello` to innocent DTLS servers pretending to be a third machine (the victim) and the innocent DTLS servers would then send (and retransmit) kilobytes of data to the victim, unknowingly DDoSing it.

The DTLS standard has provisions against this misuse, in the form of a cookie exchange (`ClientHello verify`) that ensures verification of the client address. Mbed TLS implements this in a stateless way, in order to avoid DoS vectors against your own server, as recommended by the standard.

This mechanism uses secret server-side keys, in order to prevent an attacker from generating valid cookies. As usual, the SSL layer only expects callbacks so that you can provide your own implementation if desired, and a default implementation is provided, in `ssl_cookie.c`.

1. The keys are stored in an `mbedtls_ssl_cookie_ctx` that you need to declare or allocate.

1. Initialize with `mbedtls_ssl_cookie_init()` and `mbedtls_ssl_cookie_setup()`.

1. Register the context and callbacks with `mbedtls_ssl_conf_dtls_cookies()`.
  * If you are in a threaded environment, this should happen in the main thread during initialization.

1. Then, for each client that attempts to connect, you need to call `mbedtls_ssl_set_client_transport_id()` with the client address that will be verified (generally an IPv4 or IPv6 address).

Optionally, if you log handshake errors, you might want to treat **MBEDTLS_ERR_SSL_HELLO_VERIFY_REQUIRED** in a special way for logging, as it is expected to happen for half of the handshakes. However, it still means you should destroy or reset `mbedtls_ssl_context` and start the next handshake with a fresh context (remember, we don't want to keep state for unverified clients).

## Defaults

The cookie callbacks that are registered by default always fail. The rationale is as follows:

* You cannot register working callbacks by default since you cannot create and setup the cookie context in an automated way (it needs to be shared among SSL contexts).
* You do not want to silently disable the feature by default, as that would mean insecure defaults.
* Failing callbacks force you to notice something needs to be done.

You can, **if you are sure that amplification attacks against third parties are not an issue** in your particular deployment, disable `ClientHello` verification at run-time:

* Register `NULL` callbacks.
* Alternatively, at compilation: Undefine **MBEDTLS_SSL_DTLS_HELLO_VERIFY** in `mbedtls_config.h`.

<!---",dtls-tutorial,"Article on the DTLS implementation inside Mbed TLS",,"dtls, tutorial",published,"2015-07-24 08:51:00",2,17496,"2016-02-17 17:31:00","Manuel PÃgouriÃ-Gonnard"--->

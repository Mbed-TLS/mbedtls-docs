# How to put TLS keys into an external cryptoprocessor

## Protecting a server's private key

Protect your server's long-term private key: if the key is leaked, attackers can impersonate the server.

One way to do this is to put the private key in an **external cryptoprocessor**. This is a separate environment that holds the server's private key. The external cryptoprocessor performs operations such as decryption or signature on behalf of the server, but doesn't allow the server to access the key itself. A typical example of an external cryptoprocessor is a hardware security module (HSM), which is a hardened device dedicated to holding keys that can't be extracted from the HSM and performing cryptographic operations with those keys. An external cryptoprocessor could also be, for example, a smartcard or a separate virtual environment.

If an attacker breaches the server, they can use the external cryptoprocessor only as long as they have access to the server. If the private key is stored directly on the server, then the attacker can copy the key and keep using it. However, if the key is in an external cryptoprocessor, then once the attacker loses access to the external cryptoprocessor, they lose access to the key. This isolates the damage. Furthermore, if the external cryptoprocessor keeps a key use log, the attacker cannot erase those logs.

To place the private key in an external cryptoprocessor, instead of the server, override the code that uses the private key with your own code that calls the external cryptoprocessor. You can do this by registering your code as callbacks in the TLS configuration object. When these callbacks are present, Mbed TLS doesn't need to have access to the private key.

## Configuring Mbed TLS to support private key operation callbacks

<span class="notes">**Note:** Private key operation callbacks are available with Mbed TLS version 2.11 onwards.</span>

This feature is only available for server-side asymmetric cryptography. In Mbed TLS version 2.11, it is not available for clients or Pre-shared Keys.

Support for private key operation callbacks in TLS is turned off by default. To activate it, build the library with the option `MBEDTLS_SSL_ASYNC_PRIVATE` turned on in the configuration. You can use the following command in the Mbed TLS build tree:
```
scripts/config.pl set MBEDTLS_SSL_ASYNC_PRIVATE
```
Alternatively, ensure that the file `include/mbedtls/config.h` contains the following line (a commented-out version of this line is in the default configuration):
```
#define MBEDTLS_SSL_ASYNC_PRIVATE
```

Note that this changes the application binary interface (ABI) of the TLS library (`libmbedtls.so` or `mbedtls.dll`) so you need to rebuild any library that depends on it. The `mbedcrypto` and `mbedx509` libraries are not affected.

## Overview of private key operation callbacks in TLS

Private key operation callbacks allow you to offload operations on a server's private key to an external cryptoprocessor. When a callback is registered, the cryptographic operations involving the private key are performed by the callback instead of Mbed TLS's own cryptographic code. It is up to the callback to make calls to the external cryptoprocessor.

The interface has four callback functions:

* [`f_async_sign_start`](/api/ssl_8h.html#ad57308aa77db11dbc3551fd92deb2520) receives the data to sign and must initiate the signature operation.
* [`f_async_decrypt_start`](/api/ssl_8h.html#ac18191035f2598e3311d24a3ae40a0fa) receives the data to decrypt and must initiate the decryption operation.
* [`f_async_resume`](/api/ssl_8h.html#a6a67de0c00f4aff4500ece33645a96cd) is called after `f_async_sign_start` or `f_async_decrypt_start`, and must return the signature or the decrypted data.
* [`f_async_cancel`](/api/ssl_8h.html#a084ed94ac531cfde7dcd0d0c05d392bd) is called if the TLS connection is closed after a call to `f_async_sign_start` or `f_async_decrypt_start`, and before `f_async_resume` has returned the result.

The interface defines separate `start` and `resume` functions, to allow **asynchronous** calls to the external cryptoprocessor. For example, the `start` functions may send the request to the external cryptoprocessor and return without waiting for a response, and the `resume` function would read the response when it is available. In the sections below, we show how to [use the callbacks in the synchronous case](#using-private-key-operation-callbacks-synchronously), then how to [run a non-blocking server with asynchronous callbacks](#using-private-key-operation-callbacks-asynchonously).

To declare the callbacks, call the function [`mbedtls_ssl_conf_async_private_cb`](/api/ssl_8h.html#a0675aed5a2b2b9ff219a62ed28b50819):
```
mbedtls_ssl_conf_async_private_cb( ssl->config,
                                   f_async_sign_start,
                                   f_async_decrypt_start,
                                   f_async_resume,
                                   f_async_cancel,
                                   config_data );
```

If you don't use any decryption-based cipher suite, or if the decryption keys are on the server, you can set `f_async_decrypt_start` to `NULL`. In this case, the TLS stack doesn't try to use an external cryptoprocessor for decryption. Likewise, you can set `f_async_sign_start` to `NULL`, and the TLS stack doesn't call the external cryptoprocessor to sign anything. You can also pass `NULL` for `f_async_cancel` if you don't have any data to clean up when a TLS connection is closed during the cryptographic operation.

If you need to return an error from the callbacks, you should use an [`MBEDTLS_PK_xxx`](/api/pk_8h.html#define-members) error code. This is because the callbacks simulate calls to the `pk` module. Do not use `MBEDTLS_SSL_xxx` error codes except as directed in the callback documentation.

## Cryptographic data formats

The `start` callbacks take a `cert` argument, which is a pointer to the server certificate used for the TLS connection. If the server has multiple private keys and associated certificates (for example, because it has a key of each supported type), the callback code must use `cert` to determine which private key to use for signing or decrypting. You can access the public key as `cert->pk`.

In simple cases, the pointer `cert` is one of the pointers passed to `mbedtls_ssl_conf_own_cert` when configuring the TLS connection. However, if you also use other callbacks, this may not apply. For example, if you register an SNI callback with `mbedtls_ssl_conf_sni()`, then this callback determines what certificate object the asynchronous callbacks receive.

Please refer to the documentation on [signature](/api/ssl_8h.html#ad57308aa77db11dbc3551fd92deb2520) and [decryption](/api/ssl_8h.html#ac18191035f2598e3311d24a3ae40a0fa) callbacks for information about the input and output formats for cryptographic operations.

## Using private key operation callbacks synchronously

In `f_async_sign_start` or `f_async_decrypt_start`, make the required calculation, store the result somewhere, and return `0`. The TLS stack first calls the appropriate `start` function, then calls the resume callback. In the resume callback, copy the result to the output buffer.

You can call [`mbedtls_ssl_set_async_operation_data`](/api/ssl_8h.html#ac57fb2abf2a5cd821d0ec8c3d6c59daf) and [`mbedtls_ssl_get_async_operation_data`](/api/ssl_8h.html#a7e424db2d8ccc9f0d5fe4ed0a9a5bab2) to store a pointer in the TLS context, in order to remember it between the start and resume calls.

You can define callbacks that use an external cryptoprocessor synchronously:

```
struct buffer {
    size_t size;
    unsigned char data[];
};

int f_async_sign_start( mbedtls_ssl_context *ssl,
                        mbedtls_x509_crt *cert,
                        mbedtls_md_type_t md_alg,
                        const unsigned char *hash,
                        size_t hash_len )
{
    struct buffer *buf = mbedtls_calloc( 1, sizeof(struct buffer) + MAX_SIGNATURE_SIZE );
    if( buf == NULL )
        return( MBEDTLS_ERR_PK_ALLOC_FAILED );
    /* Omitted: calculate the signature and write it to buf->data and
       its size to buf->size. */
    mbedtls_ssl_set_async_operation_data( ssl, buf );
    return( 0 );
}

int f_async_resume( mbedtls_ssl_context *ssl,
                    unsigned char *output,
                    size_t *output_len,
                    size_t output_size )
{
    struct buffer *buf = mbedtls_ssl_get_async_operation_data( ssl );
    if( buf->size > output_size )
        return( MBEDTLS_ERR_PK_BUFFER_TOO_SMALL );
    memcpy( output, &buf->data, buf->size );
    mbedtls_free( buf );
    return( 0 );
}

void f_async_cancel( mbedtls_ssl_context *ssl )
{
    struct buffer *buf = mbedtls_ssl_get_async_operation_data( ssl );
    mbedtls_free( buf );
}
```

## Using private key operation callbacks asynchonously

Private key operation callbacks are split in two steps: `start` and `resume`. This allows the server to remain non-blocking even if calls to the external cryptoprocessor are blocking. You can use the start callback to send a request to the external cryptoprocessor and use the resume callback to retrieve the external cryptoprocessor's response. This way, the private key operation is executed asynchronously, without blocking the calling thread on the server.

When the TLS stack calls a callback, the thread executing the callback is blocked until the callback returns. To unblock the thread if the requested operation is not finished, a callback can return the special error code `MBEDTLS_ERR_SSL_ASYNC_IN_PROGRESS`. This code indicates that the operation is still in progress. The TLS stack reports this error code to the application, so high-level functions such as `mbedtls_ssl_step()` return `MBEDTLS_ERR_SSL_ASYNC_IN_PROGRESS`. On the next function call on this SSL connection, the TLS stack calls the resume callback.

In your application, if an `mbedtls_ssl_xxx` function returns `MBEDTLS_ERR_SSL_ASYNC_IN_PROGRESS`, call the same function with the same arguments when the external cryptoprocessor's response is ready. You can call it at any time, and the TLS stack calls the resume callback. The resume callback might itself return `MBEDTLS_ERR_SSL_ASYNC_IN_PROGRESS` if the result of the operation is still not ready.

In a TLS connection, the private key is used during the handshake phase. After the initial handshake at the beginning of the connection, the private key is usually not used anymore, therefore later functions such as `mbedtls_ssl_read()` and `mbedtls_ssl_write()` do not return `MBEDTLS_ERR_SSL_ASYNC_IN_PROGRESS`. However, if renegotiation is enabled, most functions can trigger a new handshake, which results in a callback returning `MBEDTLS_ERR_SSL_ASYNC_IN_PROGRESS`.

The following code sample illustrates how to define callbacks that use an external cryptoprocessor asynchronously:

```
int f_async_sign_start( mbedtls_ssl_context *ssl,
                        mbedtls_x509_crt *cert,
                        mbedtls_md_type_t md_alg,
                        const unsigned char *hash,
                        size_t hash_len )
{
    /* Create an HSM request */
    request_handle_t *request = new_signing_request( cert, md_alg, hash, hash_len );
    if( request == NULL )
        return( MBEDTLS_ERR_PK_ALLOC_FAILED );
    /* Enqueue the request. Do not wait for it to complete. */
    enqueue_request_for_hsm( request );
    /* Remember the request and return without blocking. */
    request->origin = ssl;
    mbedtls_ssl_set_async_operation_data( ssl, request_handle );
    return( MBEDTLS_ERR_SSL_ASYNC_IN_PROGRESS );
}

int f_async_resume( mbedtls_ssl_context *ssl,
                    unsigned char *output,
                    size_t *output_len,
                    size_t output_size )
{
    request_handle_t *request = mbedtls_ssl_get_async_operation_data( ssl );
    if( response_is_available( request ) )
    {
        return( read_response( request, output, output_len, output_size ) );
    }
    else
    {
        /* No response available. Try again later. */
        return( MBEDTLS_ERR_SSL_ASYNC_IN_PROGRESS );
    }
}

void f_async_cancel( mbedtls_ssl_context *ssl )
{
    request_handle_t *request = mbedtls_ssl_get_async_operation_data( ssl );
    cancel_request( request );
}

/* Example simplified structure of application code using poll(2) */
{
    struct pollfd poll_fds[NUM_POLL_FDS];
    /* Omitted: set up poll_fds */
    poll( poll_fds, NUM_POLL_FDS, 0 );
    for( i = 0; i < NUM_POLL_FDS; i++ )
    {
        int fd = poll_fds[i].fd;
        if( fd == hsm_fd )
        {
            /* Read a response from the HSM and resume the associated
               SSL connection. */
            hsm_response = read_hsm_response();
            mbedtls_ssl_handshake_step( hsm_response->request->origin );
        }
    }
}
```

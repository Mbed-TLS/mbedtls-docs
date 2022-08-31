# Nonblocking ECC

ECC operations are expensive. They're the most expensive operations in a typical TLS handshake, which includes many of them. On small boards, for example, based on a Cortex M0 core, a TLS handshake can spend several seconds on ECC operations. In a threaded environment, such as Mbed OS, this is not a problem because other threads can execute concurrently. In nonthreaded environments, blocking for several seconds on an operation is not acceptable if the system needs to attend to other tasks in a timely fashion. In order to support that case, Mbed TLS provides a restartable version of `ECC` operations, and all operations that depend on them (such as TLS handshakes), through the configuration option `MBEDTLS_ECP_RESTARTABLE` in the configuration header (`mbedtls/mbedtls_config.h`). Restartable functions enable collaborative multitasking by returning after a configurable amount of computations, so that you can attend to other tasks. They then continue the operation, and so on, until it completes. The `ECP`, `ECDSA`, `ECDH`, `PK`, `X.509` and `SSL` modules support this feature. Curve25519 does not support this feature at this time.

Continue reading to learn about the workflow of the restartable ECC feature, starting with the broad concept followed by specific examples.

## Enabling the restartable ECC feature, generic flow

* At configuration time, define `MBEDTLS_ECP_RESTARTABLE` in `mbedtls/mbedtls_config.h`. See [How do I configure Mbed TLS](../compiling-and-building/how-do-i-configure-mbedtls.md) for more information.
* Set the maximal number of operations that you want to run in a row with the `ECP` module, using `mbedtls_ecp_set_max_ops()`.
* Allocate the restart context, and initialize it by calling `mbedtls_xxx_restart_init()`.
* `ECP`, `ECDSA`, `PK` and `X.509` need an explicit restart context, and `ECDH` and `SSL` don't, though `ECDH` requires an additional call to `mbedtls_ecdh_enable_restart()`.
* Call the `mbedtls_xxx_xxxx()` or `mbedtls_xxx_xxxx_restartable()` operation. As long as it returns the error `MBEDTLS_ERR_ECP_IN_PROGRESS` or `MBEDTLS_ERR_SSL_CRYPTO_IN_PROGRESS` for TLS functions, you can call it again, potentially after taking care of other system operations. It is the caller's responsibility to either call again with the same parameters until it returns 0 or an error code, or to free the restart context if the caller wishes to abort the operation.

**Note**: We strictly require all input parameters and the restart context to be the same on successive calls for the same operation. Output parameters do not need to be the same, though you must not use them until the function finally returns 0.

**Note**: Sometimes, functions need to block for a minimum number of operations and will do so even if `max_ops` is set to a lower value. That minimum depends on the curve size. You can lower it by decreasing the value of `MBEDTLS_ECP_WINDOW_SIZE`.

## Restartable ECP flow

* Define `mbedtls_ecp_restart_ctx` and call `mbedtls_ecp_restart_init()` with the defined context.
* Set maximal number of operations with `mbedtls_ecp_set_max_ops()`.
* Call `mbedtls_ecp_xxx_restartable()`, as long as the return code is `MBEDTLS_ERR_ECP_IN_PROGRESS`.

For example:

```
    mbedtls_ecp_restart_ctx ctx;
    mbedtls_ecp_restart_init( &ctx );
    mbedtls_ecp_set_max_ops( max_ops );

    do {
        ret = mbedtls_ecp_mul_restartable( &grp, &R, &dA, &grp.G, NULL, NULL, &ctx );
        /* Here you can attend to other tasks */
    } while( ret == MBEDTLS_ERR_ECP_IN_PROGRESS );
    if( ret != 0 )
    {
        /* Handle your error here*/
    }
    mbedtls_ecp_restart_free( &ctx );
```

## Restartable ECDSA flow

* Define `mbedtls_ecdsa_restart_ctx`, and call `mbedtls_ecdsa_restart_init()` with the defined context.
* Set maximal number of operations with `mbedtls_ecp_set_max_ops()`.
* Call `mbedtls_ecdsa_xxx_restartable()`, as long as the return code is `MBEDTLS_ERR_ECP_IN_PROGRESS`.
* Free the restartable context with `mbedtls_ecdsa_restart_free()`.

For example:

```
    mbedtls_ecdsa_context ctx;
    mbedtls_ecdsa_restart_ctx rs_ctx;
    mbedtls_ecdsa_init( &ctx );
    mbedtls_ecdsa_restart_init( &rs_ctx );
    mbedtls_ecp_set_max_ops( max_ops );

    do {
        ret = mbedtls_ecdsa_read_signature_restartable( &ctx,
                      hash, hash_len, sig, sig_len, &rs_ctx );
        /* Here you can attend to other tasks */
    } while( ret == MBEDTLS_ERR_ECP_IN_PROGRESS );
    if( ret != 0 )
    {
        /* Handle your error here*/
    }
    mbedtls_ecdsa_restart_free( &rs_ctx );
    mbedtls_ecdsa_free( &ctx );
```

## Restartable ECDH flow

* Set maximal number of operations with `mbedtls_ecp_set_max_ops()`.
* Enable support for restarting with `mbedtls_ecdh_enable_restart()`.
* Call the ecdh operation as long as the return code is `MBEDTLS_ERR_ECP_IN_PROGRESS`.

For example:
    
```
    mbedtls_ecdh_context srv;
    mbedtls_ecdh_init( &srv );
    mbedtls_ecdh_enable_restart( &srv );
    mbedtls_ecp_set_max_ops( max_ops );

    do {
        ret = mbedtls_ecdh_make_params( &srv, &len, buf, sizeof( buf ),
                                        rnd_buffer_rand, &rnd_info_A );
        /* Here you can attend to other tasks */
    } while( ret == MBEDTLS_ERR_ECP_IN_PROGRESS );
    if( ret != 0 )
    {
        /* Handle your error here*/
    }
    mbedtls_ecdh_free( &srv );
```

## Restartable PK flow

* Define `mbedtls_pk_restart_ctx` and call `mbedtls_pk_restart_init()` with the defined context.
* Set maximal number of operations with `mbedtls_ecp_set_max_ops()`.
* Call `mbedtls_pk_xxx_restartable()`, as long as the return code is `MBEDTLS_ERR_ECP_IN_PROGRESS`.
* Free the restartable context with `mbedtls_pk_restart_free()`.

**Note**: Call these functions for ECDSA only. If `PK` is `RSA`, then set `mbedtls_pk_restart_ctx` to NULL.

For example:

```
    mbedtls_pk_restart_ctx ctx;

    mbedtls_pk_restart_init( &ctx );
    mbedtls_ecp_set_max_ops( max_ops );

    do {
        ret = mbedtls_pk_verify_restartable(  &pk, digest, hash_result, 0,
                    result_str, mbedtls_pk_get_len( &pk ), &ctx  );
        /* Here you can attend to other tasks */
    } while( ret == MBEDTLS_ERR_ECP_IN_PROGRESS );
    if( ret != 0 )
    {
        /* Handle your error here*/
    }
    mbedtls_pk_restart_free( &ctx );
```

## Restartable X.509 flow

*  Define `mbedtls_x509_crt_restart_ctx` and call `mbedtls_x509_crt_restart_init()` with the defined context.
*  Set maximal number of operations with `mbedtls_ecp_set_max_ops()`.
*  Call `mbedtls_x509_crt_xxx_restartable()`, as long as the return code is `MBEDTLS_ERR_ECP_IN_PROGRESS`.
*  Free the restartable context with `mbedtls_x509_crt_restart_free()`.

For example:

```
    mbedtls_x509_crt_restart_ctx ctx;

    mbedtls_x509_crt_restart_init( &ctx );
    mbedtls_ecp_set_max_ops( max_ops );

    do {
        ret = mbedtls_x509_crt_verify_restartable(  &crt, &ca, NULL,
                &mbedtls_x509_crt_profile_default, NULL, &flags,
                NULL, NULL, &rs_ctx );
        /* Here you can attend to other tasks */
    } while( ret == MBEDTLS_ERR_ECP_IN_PROGRESS );
    if( ret != 0 )
    {
        /* Handle your error here*/
    }
    mbedtls_x509_crt_restart_free( &ctx );
```

## Restartable SSL flow

* Set maximal number of operations with `mbedtls_ecp_set_max_ops()`.
* Call the SSL handshake operation, as long as it returns `MBEDTLS_ERR_SSL_CRYPTO_IN_PROGRESS` (in addition to `MBEDTLS_ERR_SSL_WANT_READ` and `MBEDTLS_ERR_SSL_WANT_WRITE`).

For example:

```
    mbedtls_ecp_set_max_ops( max_ops );

    do {
        ret = mbedtls_ssl_handshake( &ssl );
        /* Here you can attend to other tasks */
    } while( ret == MBEDTLS_ERR_SSL_WANT_READ ||
             ret == MBEDTLS_ERR_SSL_WANT_WRITE ||
             ret == MBEDTLS_ERR_SSL_CRYPTO_IN_PROGRESS );
    if( ret != 0 )
    {
        /* Handle your error here*/
    }
```

The restartable feature is done automatically, as long as:

1. You define `MBEDTLS_ECP_RESTARTABLE` in `mbedtls/mbedtls_config.h`.
1. The TLS protocol is TLS 1.2 and higher.
1. The negotiated key exchange is `MBEDTLS_KEY_EXCHANGE_ECDHE_ECDSA`.
1. You call `mbedtls_ecp_set_max_ops()`.
1. **The restartable SSL feature is supported for TLS client only**.

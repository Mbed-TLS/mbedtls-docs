<h2 id="tls-prf">TLS PRF key derivation</h2>

[RFC 5246](https://tools.ietf.org/html/rfc5246) defines the pseudorandom function (PRF) as follows:
>In addition, a construction is required to do expansion of secrets
   into blocks of data for the purposes of key generation or validation.
   This pseudorandom function (PRF) takes as input a secret, a seed, and
   an identifying label and produces an output of arbitrary length.

The TLS PRF is a function that generates key material, which security protocols can use to derive a key for ciphering data. Many security protocols that rely on TLS for authentication, such as [DTLS-SRTP](https://tools.ietf.org/html/rfc5764) and [EAP-TLS](https://tools.ietf.org/html/rfc5216), use the TLS-defined PRF and other TLS handshake data (the master key and the handshake random bytes) to derive their own key material, using their own defined string label.

### Exporting key material using Mbed TLS

The Mbed TLS `mbedtls_ssl_tls_prf()` API uses the `tls_prf` function, which you set as an input parameter. You must set the `tls_prf` function to one of the following options:

```
  typedef enum
  {
     MBEDTLS_SSL_TLS_PRF_NONE,
     MBEDTLS_SSL_TLS_PRF_SSL3,
     MBEDTLS_SSL_TLS_PRF_TLS1,
     MBEDTLS_SSL_TLS_PRF_SHA384,
     MBEDTLS_SSL_TLS_PRF_SHA256
  }
  mbedtls_tls_prf_types;
```

This function also receives the secret to derive the key material from. The secret is usually the TLS handshake master key, and the random bytes generated in the TLS handshake.

The following section explains how to export the handshake-generated secret information.

### Exporting the TLS handshake secret keys

<span class="notes">**Note:** Exporting the secret information can affect the security of your application! You should not expose this information outside of your application. Clear the information after use with `mbedtls_platform_zeroize()`!</span>

With the configuration option `MBEDTLS_SSL_EXPORT_KEYS` enabled, the keys generated in the TLS handshake are exported to a callback you define and set.

The prototype of the callback is:

```
  typedef int mbedtls_ssl_export_keys_ext_t( void *p_expkey,
                                         const unsigned char *ms,
                                         const unsigned char *kb,
                                         size_t maclen,
                                         size_t keylen,
                                         size_t ivlen,
                                         unsigned char client_random[32],
                                         unsigned char server_random[32],
                                         mbedtls_tls_prf_types tls_prf_type );
```

Set the callback function in your SSL configuration structure by calling `mbedtls_ssl_conf_export_keys_ext_cb` before you start the TLS handshake.

<span class="notes">**Note:** There is another callback function, called `mbedtls_ssl_export_keys_t`, that the TLS library calls during the handshake; however, it doesn't export the random bytes and the tls-prf function used in the handshake. We recommend not to use `mbedtls_ssl_export_keys_t` because it will probably be deprecated in the future.</span>

After you extract the required information in your callback to your given context (`p_expkey`), you can use it to call `mbedtls_ssl_tls_prf()`, which is described in the previous section, or for other purposes.

### Example of tls-prf key derivation - EAP-TLS use case

Following is an example of the process described before, deriving the eap-tls key material, as described in [RFC 5216 section 2.3](https://tools.ietf.org/html/rfc5216#section-2.3).

#### Defining the callback-specific context:

```
  typedef struct eap_tls_keys
  {
      unsigned char master_secret[48];
      unsigned char randbytes[64];
      mbedtls_tls_prf_types tls_prf_type;
  } eap_tls_keys;
```

#### Defining the key export callback

```
  static int eap_tls_key_derivation ( void *p_expkey,
                                  const unsigned char *ms,
                                  const unsigned char *kb,
                                  size_t maclen,
                                  size_t keylen,
                                  size_t ivlen,
                                  unsigned char client_random[32],
                                  unsigned char server_random[32],
                                  mbedtls_tls_prf_types tls_prf_type )
  {
      eap_tls_keys *keys = (eap_tls_keys *)p_expkey;

      ( ( void ) kb );
      ( ( void ) maclen );
      ( ( void ) keylen );
      ( ( void ) ivlen );
      memcpy( keys->master_secret, ms, sizeof( keys->master_secret ) );
      memcpy( keys->randbytes, client_random, 32 );
      memcpy( keys->randbytes + 32, server_random, 32 );
      keys->tls_prf_type = tls_prf_type;

      return( 0 );
  }
```

#### The main application

* Variable declarations:

    ```
    #if defined(MBEDTLS_SSL_EXPORT_KEYS)
        unsigned char eap_tls_keymaterial[16];
        unsigned char eap_tls_iv[8];
        const char* eap_tls_label = "client EAP encryption";
        eap_tls_keys eap_tls_keying;
    #endif
    ```

* Initialize the structures:

    ```
    #if defined(MBEDTLS_SSL_EXPORT_KEYS)
        mbedtls_ssl_conf_export_keys_ext_cb( &conf, eap_tls_key_derivation,
                                             &eap_tls_keying );
    #endif
    ```

* Perform TLS handshake.
* After a successful TLS handshake, derive the key material:
    ```
    #if defined(MBEDTLS_SSL_EXPORT_KEYS)
    {
        size_t j = 0;

        if( ( ret = mbedtls_ssl_tls_prf( eap_tls_keying.tls_prf_type,
                                         eap_tls_keying.master_secret,
                                         sizeof( eap_tls_keying.master_secret ),
                                         eap_tls_label,
                                         eap_tls_keying.randbytes,
                                         sizeof( eap_tls_keying.randbytes ),
                                         eap_tls_keymaterial,
                                         sizeof( eap_tls_keymaterial ) ) )
                                         != 0 )
        {
            mbedtls_printf( " failed\n  ! mbedtls_ssl_tls_prf returned -0x%x\n\n",
                            -ret );
            goto exit;
        }

        mbedtls_printf( "    EAP-TLS key material is:" );
        for( j = 0; j < sizeof( eap_tls_keymaterial ); j++ )
        {
            if( j % 8 == 0 )
                mbedtls_printf( "\n    " );
            mbedtls_printf( "%02x ", eap_tls_keymaterial[j] );
        }
        mbedtls_printf( "\n" );

        if( ( ret = mbedtls_ssl_tls_prf( eap_tls_keying.tls_prf_type, NULL, 0,
                                         eap_tls_label,
                                         eap_tls_keying.randbytes,
                                         sizeof( eap_tls_keying.randbytes ),
                                         eap_tls_iv,
                                         sizeof( eap_tls_iv ) ) ) != 0 )
         {
             mbedtls_printf( " failed\n  ! mbedtls_ssl_tls_prf returned -0x%x\n\n",
                             -ret );
             goto exit;
         }

        mbedtls_printf( "    EAP-TLS IV is:" );
        for( j = 0; j < sizeof( eap_tls_iv ); j++ )
        {
            if( j % 8 == 0 )
                mbedtls_printf( "\n    " );
            mbedtls_printf( "%02x ", eap_tls_iv[j] );
        }
        mbedtls_printf( "\n" );
    }
    #endif /* MBEDTLS_SSL_EXPORT_KEYS */
    ```

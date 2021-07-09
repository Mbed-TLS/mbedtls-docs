# PolarSSL Security Advisory 2011-01

**Title** |  Possible man in the middle in Diffie Hellman key exchange
---|---
**CVE** |  CVE-2011-1923
**Date** |  25th of February 2011
**Affects** |  PolarSSL library 0.14.0 and earlier and PolarSSL 0.99-pre1
**Not affected** |  Instances not using ciphersuites that are based on Diffie-
Hellman key-exchange
**Impact** |  Possible man in the middle
**Exploit** |  Withheld
**Solution** |  Upgrade to PolarSSL 0.14.2 or PolarSSL 0.99-pre3
**Workaround** |  Disable ciphersuites using Diffie-Hellman key exchange,
enable full authentication or apply patch provided.
**Credits** |  Larry Highsmith, [Subreption LLS](http://www.subreption.com/)

By posing as a man in the middle and modifying packets as the secure
communication is set-up it is possible for an attacker to force the
calculation of a fully predictable Diffie Hellman secret.

The cipher suites that may be affected (depending on other variables) are:

  * SSL_EDH_RSA_DES_168_SHA
  * SSL_EDH_RSA_AES_128_SHA
  * SSL_EDH_RSA_AES_256_SHA
  * SSL_EDH_RSA_CAMELLIA_128_SHA
  * SSL_EDH_RSA_CAMELLIA_256_SHA

In case full authentication (client and server certificates) is used, no man
in the middle attack seems possible.

The patch for PolarSSL version 0.14.0 is as follows:



    Index: dhm.c
    ===================================================================
    --- dhm.c       (revision 950)
    +++ dhm.c       (working copy)
    @@ -63,6 +63,35 @@
     }

     /*
    + * Verify sanity of public parameter with regards to P
    + *
    + * Public parameter should be: 2 <= public_param <= P - 2
    + *
    + * For more information on the attack, see:
    + *  <http://www.cl.cam.ac.uk/~rja14/Papers/psandqs.pdf>
    + *  <http://web.nvd.nist.gov/view/vuln/detail>?vulnId=CVE-2005-2643
    + */
    +static int dhm_check_range( const mpi *public_param, const mpi *P )
    +{
    +    mpi L, U;
    +    int ret = POLARSSL_ERR_DHM_BAD_INPUT_DATA;
    +
    +    mpi_init( &L, &U, NULL );
    +    mpi_lset( &L, 2 );
    +    mpi_sub_int( &U, P, 2 );
    +
    +    if( mpi_cmp_mpi( public_param, &L ) >= 0 &&
    +        mpi_cmp_mpi( public_param, &U ) <= 0 )
    +    {
    +        ret = 0;
    +    }
    +
    +    mpi_free( &L, &U, NULL );
    +
    +    return( ret );
    +}
    +
    +/*
      * Parse the ServerKeyExchange parameters
      */
     int dhm_read_params( dhm_context *ctx,
    @@ -78,6 +107,9 @@
             ( ret = dhm_read_bignum( &ctx->GY, p, end ) ) != 0 )
             return( ret );

    +    if( ( ret = dhm_check_range( &ctx->GY, &ctx->P ) ) != 0 )
    +        return( ret );
    +
         ctx->len = mpi_size( &ctx->P );

         if( end - *p < 2 )
    @@ -122,6 +154,9 @@
         MPI_CHK( mpi_exp_mod( &ctx->GX, &ctx->G, &ctx->X,
                               &ctx->P , &ctx->RP ) );

    +    if( ( ret = dhm_check_range( &ctx->GX, &ctx->P ) ) != 0 )
    +        return( ret );
    +
         /*
          * export P, G, GX
          */
    @@ -199,6 +233,9 @@
         MPI_CHK( mpi_exp_mod( &ctx->GX, &ctx->G, &ctx->X,
                               &ctx->P , &ctx->RP ) );

    +    if( ( ret = dhm_check_range( &ctx->GX, &ctx->P ) ) != 0 )
    +        return( ret );
    +
         MPI_CHK( mpi_write_binary( &ctx->GX, output, olen ) );

     cleanup:
    @@ -223,6 +260,9 @@
         MPI_CHK( mpi_exp_mod( &ctx->K, &ctx->GY, &ctx->X,
                               &ctx->P, &ctx->RP ) );

    +    if( ( ret = dhm_check_range( &ctx->GY, &ctx->P ) ) != 0 )
    +        return( ret );
    +
         *olen = mpi_size( &ctx->K );

         MPI_CHK( mpi_write_binary( &ctx->K, output, *olen ) );


### Like this?

**Section:**
Security Advisories

**Author:**
Paul Bakker

**Published:**
Oct 14, 2012

**Last updated:**
Jul 12, 2013
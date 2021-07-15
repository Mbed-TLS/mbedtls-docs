# PolarSSL Security Advisory 2012-01

**Title** |  Weak Diffie-Hellman and RSA key generation
---|---
**CVE** |  CVE-2012-2130
**Date** |  23th of April 2012
**Affects** |  PolarSSL 0.99-pre4 up to and including PolarSSL 1.1.1
**Not affected** |  Instances not using Diffie-Hellman key exchange and not
using prime or RSA key generation
**Impact** |  Weak prime generation and key negotiation resulting in possible
breach of confidentiality and integrity
**Exploit** |  Withheld
**Solution** |  Upgrade to PolarSSL 1.1.2
**Workaround** |  Disable ciphersuites using Diffie-Hellman key exchange or
apply patch provided. Re-generate primes or RSA keys created with affected
versions of PolarSSL.
**Credits** |  Ruslan Yushchenko

During code migration a bug was introduced in PolarSSL 0.99-pre4. As a result
the generation of Diffie Hellman value X is weak on the client and server.
Only a part of the value X is filled with random data, instead of the whole
value. (Determined by the server Diffie Hellman parameters). In addition, MPI
primes are only generated within a limited subspace of the full prime space.
Again only a part of the prime is filled with random data, instead of the
whole value.

## Impact

When a weak X is generated the resulting Diffie Hellman key exchange is
weaker. This makes it easier for an attacker to brute force the private value
and thus the master secret. When the master secret is known, an attacker is
able to modify and read all data in the secure channel.

MPI primes generated with mpi_gen_prime() are less secure. If rsa_gen_key()
was used to generate RSA keys with PolarSSL, these keys are less secure as
well. This only affects keys / primes generated within affected versions of
PolarSSL, not keys generated in older versions or imported keys.

## Resolution

PolarSSL version 1.1.2 contains a fix for the bug and generates full-size
values of X and primes.

If you generated primes or RSA keys from within PolarSSL, re-generate and
replace those primes / keys.

## Workaround

For the Diffie-Hellman side of the issue: Either patch or disable affected
ciphersuites as a workaround. For the RSA side of the issue: Patch and re-
generate primes and RSA keys created within PolarSSL.

Disable all DHE ciphersuites in either the server or the client, so that only
RSA key exchange is used. In PolarSSL this is done by modifying the list that
is sent to ssl_set_ciphersuites().

**Note:** The RSA only suites are considered less secure because only random
from one side is used. Please keep this in mind when choosing this option.

## Advice

We advise everyone affected by this issue to upgrade, patch or disable the
ciphersuites as soon as possible.

## Patch

The patch for PolarSSL version 1.1.1 is as follows:



    Index: library/dhm.c
    ===================================================================
    --- library/dhm.c
    +++ library/dhm.c
    @@ -130,19 +130,21 @@
                          int (*f_rng)(void *, unsigned char *, size_t),
                          void *p_rng )
     {
    -    int ret, n;
    +    int ret;
         size_t n1, n2, n3;
         unsigned char *p;

         /*
          * Generate X as large as possible ( < P )
          */
    -    n = x_size / sizeof( t_uint ) + 1;
    +    do
    +    {
    +        mpi_fill_random( &ctx->X, x_size, f_rng, p_rng );

    -    mpi_fill_random( &ctx->X, n, f_rng, p_rng );
    -
    -    while( mpi_cmp_mpi( &ctx->X, &ctx->P ) >= 0 )
    +        while( mpi_cmp_mpi( &ctx->X, &ctx->P ) >= 0 )
                mpi_shift_r( &ctx->X, 1 );
    +    }
    +    while( dhm_check_range( &ctx->X, &ctx->P ) != 0 );

         /*
          * Calculate GX = G^X mod P
    @@ -207,7 +209,7 @@
                          int (*f_rng)(void *, unsigned char *, size_t),
                          void *p_rng )
     {
    -    int ret, n;
    +    int ret;

         if( ctx == NULL || olen < 1 || olen > ctx->len )
             return( POLARSSL_ERR_DHM_BAD_INPUT_DATA );
    @@ -215,12 +217,14 @@
         /*
          * generate X and calculate GX = G^X mod P
          */
    -    n = x_size / sizeof( t_uint ) + 1;
    +    do
    +    {
    +        mpi_fill_random( &ctx->X, x_size, f_rng, p_rng );

    -    mpi_fill_random( &ctx->X, n, f_rng, p_rng );
    -
    -    while( mpi_cmp_mpi( &ctx->X, &ctx->P ) >= 0 )
    +        while( mpi_cmp_mpi( &ctx->X, &ctx->P ) >= 0 )
                mpi_shift_r( &ctx->X, 1 );
    +    }
    +    while( dhm_check_range( &ctx->X, &ctx->P ) != 0 );

         MPI_CHK( mpi_exp_mod( &ctx->GX, &ctx->G, &ctx->X,
                               &ctx->P , &ctx->RP ) );
    Index: library/bignum.c
    ===================================================================
    --- library/bignum.c
    +++ library/bignum.c
    @@ -1813,7 +1813,7 @@
             /*
              * pick a random A, 1 < A < |X| - 1
              */
    -        MPI_CHK( mpi_fill_random( &A, X->n, f_rng, p_rng ) );
    +        MPI_CHK( mpi_fill_random( &A, X->n * ciL, f_rng, p_rng ) );

             if( mpi_cmp_mpi( &A, &W ) >= 0 )
             {
    @@ -1885,7 +1885,7 @@

         n = BITS_TO_LIMBS( nbits );

    -    MPI_CHK( mpi_fill_random( X, n, f_rng, p_rng ) );
    +    MPI_CHK( mpi_fill_random( X, n * ciL, f_rng, p_rng ) );

         k = mpi_msb( X );
         if( k < nbits ) MPI_CHK( mpi_shift_l( X, nbits - k ) );

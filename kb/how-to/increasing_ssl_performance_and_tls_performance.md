# Increasing SSL and TLS performance

## Situation

If you use a specific cipher suite, like **TLS-ECDHE-ECDSA-WITH-AES-128-CBC-SHA256** on your embedded platform, when you benchmark the individual cipher and hash speeds, the performance may be:

* AES-128-CBC: 321 Kb/s
* SHA256-HMAC: 441 Kb/s

You expect a reasonable performance speed for your SSL connection as well. However, when you benchmark the sent and received SSL/TLS data, the performance is only about 9 Kb/s.

## Explanation

The overhead of the SSL debug module should be negligible when `mbedtls_debug_set_threshold( 0 );` is called. You may still want to [disable **MBEDTLS_DEBUG_C** in `mbedtls_config.h`](/kb/compiling-and-building/how-do-i-configure-mbedtls.md) in order to reduce the footprint and get the last few percent of performance improvement.

<!---increasing_ssl_performance_and_tls_performance
,"Small article on increasing the performance of your SSL connection or TLS connection with Mbed TLS",,"performance, debug, speed, optimizations",published,"2014-01-23 15:21:00",2,4163,"2015-07-24 11:52:00","Paul Bakker"--->

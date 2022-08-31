# How to tune Elliptic Curves resource usage

Like most parts of Mbed TLS, the implementation of elliptic curve operations can be tuned using various [compilation flags](../compiling-and-building/how-do-i-configure-mbedtls.md). This page explains the two parameters that control trade-offs between performance and footprint in more detail than our general documentation on [reducing footprint](reduce-polarssl-memory-and-storage-footprint.md).

## Performance and RAM figures

Since this page discusses performance-footprint trade-offs, it's useful to have some performance figures. For convenience, the figures quoted in this article were collected with Mbed TLS 2.2 on a machine with a 64-bit CPU. You can reproduce those results on your machine using [scripts/ecc-heap.sh](https://github.com/Mbed-TLS/mbedtls/blob/development/scripts/ecc-heap.sh) from the Mbed TLS sources.

The RAM figures only include heap usage, not the stack. This is a limitation of the measurement script. However, these should still be useful, as most memory used by elliptic curve operations will be on the heap. Remember, however, that RAM figures may be slightly lower on a 32-bit machine.

## Which curves?

This page refers to "short Weierstrass" form curves. This includes NIST, Brainpool, and "Koblitz" curves such as the one used by Bitcoin—in short, all except newer curves like Curve25519 and Curve448.

On the reference machine, Curve25519 performed 358 ECDHE/s (ephemeral Elliptic Curve Diffie-Hellman key exchanges per second) using around 1500 bytes on the heap.

## MBEDTLS_ECP_WINDOW_SIZE

The main operation on elliptic curves is multiplication of a point by an integer, which is performed using additions and doubling. This is similar to fast exponentiation algorithms you may be familiar with. It is possible to boost performance by pre-computing some well-chosen multiples of the input point just before you multiply it by the chosen integer. This is the [comb method](https://eprint.iacr.org/2004/342.pdf).)

RAM usage increases with the number of multiples you compute and store before performing the actual multiplication. However, while pre-computing a few multiples gives better performance than pre-computing none, you don't want to compute too many either. The optimal size of the pre-computation table depends on the size of the curve.

By default, our multiplication function will select the table size that gives the best performance for the curve used. However, you might want to set an upper bound for the table size: this is what `MBEDTLS_ECP_WINDOW_SIZE` does. More specifically the value of this macro is the log of the maximum number of points that will be precomputed.

For example, for NIST P-256, the performance and RAM figures for various values of this parameter (with fixed point optimization disabled, see next section) are as follows:

|Window Size|2|3|4|5|6|
| --- | --- | --- | --- | --- | --- |    
|ECDHE/s|44|50|53|53|53|
|Heap bytes|2064|2448|3592|3624|3680|

As you can see, when moving from 2 to 4, performance increases with RAM usage; larger values aren't helpful for performance. The code selects 4 as the effective value, and doesn't change RAM usage as much.

## `MBEDTLS_ECP_FIXED_POINT_OPTIM`

The first paragraph of the previous section said some multiples are precomputed just before computation, suggesting that they are discarded once the operation is done, and computed again for the next operation. This is true, but incomplete.

Elliptic curves each come with a standard "base point" (also know as generator, and usually denoted by the letter `G`), for when the protocol requires a point known by all parties. For example, in ECDHE, one party generates a secret exponent `a`, computes `aG`, send the result to its peer, receives the peer's public share `Q` then computes the shared secret `aQ`.

Notice that for the first part (but not the second), the point to be multiplied is known in advance: `G`. When you first multiply a `G` by an integer, you pre-compute well-chosen multiples of `G` as usual. After that step, you may want to store those multiples in order to speed up subsequent multiplications of `G` by other integers. Keeping this information, however, uses RAM. There is a performance-memory trade-off.

* Set `MBEDTLS_ECP_FIXED_POINT_OPTIM` to 1 in order to keep the table, and 0 to discard it.

For example, the performance and RAM figures for NIST P-256 without and with fixed point optimization (with max window size set to 4, see previous section) are as follows:


||0|1|
|---|---|---|
|ECDHE/s|53|76|
|Heap bytes|3592|5360|

### Conclusion

The ECC implementation in Mbed TLS uses some memory-performance trade-offs. The defaults values are chosen with performance in mind, but you can adjust them to reduce RAM usage for the trade-off that best fits your particular needs.

It should be noted that newer curves like Curve25519, with a simpler implementation that doesn't use any trade-offs, manage to deliver superior performance while using less RAM compared to NIST curves.

<!---",how-do-i-tune-elliptic-curves-resource-usage,"How-to guide on reducing resource usage of elliptic curves with Mbed TLS",,"elliptic curves, resources, configuration",published,"2016-02-10 12:59:00",2,3399,"2016-02-22 16:19:00","Manuel PÃ©gouriÃ©-Gonnard"--->

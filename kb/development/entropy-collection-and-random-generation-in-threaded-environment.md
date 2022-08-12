# Entropy collection, random generation with threads

## Entropy collection and random generation

Random generators, such as the [CTR-DRBG module](/ctr-drbg-source-code), require a source of entropy to kick-start and refresh their own internal entropy state. Mbed TLS includes the [Entropy collection module](/entropy-source-code) to provide a central pool of entropy to extract entropy from. In a single-threaded application, both the entropy pool and the random generator exist within the same thread context. In case of a multi-threaded application, you can either use a central entropy pool and/or random generator or thread-specific versions.

## How does entropy collection work

The entropy collector works by gathering entropy from multiple sources and integrating them into its internal entropy state. Each time entropy is collected the internal state gets better. Unless additional entropy sources have been added to the default entropy collector sources, mostly OS dependent random sources are used. Each time the entropy collector gathers entropy from the system, the entropy gets extracted and reduced.

## Random generators and entropy

The random generators themselves, like CTR-DRBG, do not require new entropy every time they are called. Instead, they expand the available entropy to produce random without compromising the original entropy and being secure as long as not too much random is generated from one state. Therefore, the random generators occasionally gather entropy from the entropy collector to refresh their state.

## Advice for threaded environments

Regarding entropy, our advice is to use a central entropy collector. Initialize once. This makes sure that the entropy collector gets the best entropy from its sources as it does not have to share with sibling entropy collectors. For more details, see [Thread Safety and Multi Threading](/kb/development/thread-safety-and-multi-threading.md).

You have two options:

* For each thread, use a separate CTR-DRBG or HMAC-DRBG random generator using a thread-specific value (like the thread ID) for the custom personalization string. Provide the DRBG with `mbedtls_entropy_func()` as its entropy callback. This ensures that the random generators between the different threads have the least amount of correlation possible and can thus be considered as independent as possible.
 
* Use a central CTR-DRBG or HMAC-DRBG context initialized once in the main thread, and share in across threads. The DRBG modules are thread-safe, as they contain locks within the contexts, which are used within the modules if threading is enabled, see [Thread Safety and Multi Threading](/kb/development/thread-safety-and-multi-threading.md).

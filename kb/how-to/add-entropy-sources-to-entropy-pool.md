# Why to add an entropy source

Good entropy is the fundamental basis for good cryptography and SSL or TLS. If your entropy is weak or predictable, a strong adversary can break your security.

Therefore, you want to have at least one, but preferably multiple sources of good or reasonable entropy.

For that purpose, Arm Mbed TLS provides the [entropy collector](https://tls.mbed.org/entropy-source-code). The entropy collector takes entropy from multiple sources and combines it into a single entropy source for use.

## Default entropy sources

In the default Mbed TLS, the entropy collector tries to use what the platform you run can provide. For Linux and UNIX-like systems, this is **/dev/urandom**. For Windows, this is `CryptGenRandom` of the **CryptoAPI**. These are considered strong entropy sources.

If you have **MBEDTLS_TIMING_C** enabled, the entropy collector also adds the `mbedtls_timing_hardclock()` value. This is only a little entropy, but every bit helps.

If you have **MBEDTLS_HAVEGE_C** enabled, Mbed TLS also uses the HAVEGE RNG. 

<span class="notes">**Note:** The HAVEGE random generator is considered reasonable but not good. Please do not base your full entropy on this.</span>

## Adding own sources

When you run Mbed TLS on a different platform, such as an embedded platform, you have to add platform-specific or application-specific entropy sources.

To add a source to the entropy collector, you can use `mbedtls_entropy_add_source()`. It requires you to provide a callback (`f_source`) that you can call whenever the entropy pool tries to gather entropy, the data (`p_source`) that you need with your callback and a `threshold`. This threshold indicates the minimum number of bytes the entropy pool should wait on from this callback before releasing entropy. Choose this value wisely. Choosing a value that is higher than your callback can provide will block entropy collection.

Starting with the 2.0 branch, you also need to indicate if this source is strong or not. For example, **/dev/urandom** and `CryptGenRandom()` are strong. Hardware RNG is a strong source if your platform has it, but the `mbedtls_timing_hardclock()` value and HAVEGE are weak. The entropy module refuses to deliver entropy unless it has at least one strong source.

## Entropy source failed

When collecting entropy for a request, the entropy pool does a maximum of 256 polls to each entropy source to retrieve entropy from them. If the **threshold** value for a source is higher than the entropy it can deliver in those 256 polls, you **will** receive an error!

## Limited sources

If you have an entropy source that only provides some limited entropy, but not on every poll, it can be wise to select a *threshold* value of **0**. A zero-threshold does not cause the entropy pool to return an error if it cannot provide any entropy in 256 calls.

## Seed files

In addition to platform specific sources, such as timing of network packets, keyboard input and so on, you can also use a seed file to produce entropy for your system. The advantage of a seed file is that you can generate it on a high-entropy system and then update and use it on your low-entropy system. 

<span class="notes">**Note:** You must make sure the seed file is unique for each device.</span>

<!---add-entropy-sources-to-entropy-pool
,"Good entropy is the fundamental basis for good cryptography and SSL or TLS. This article shows how to add nonstandard sources to the Mbed TLS entropy collector",,"entropy, entropy pool, entropy collection, windows, unix, random, entropy source, security",published,"2013-09-10 11:55:00",2,10679,"2015-07-24 11:48:00","Paul Bakker"--->

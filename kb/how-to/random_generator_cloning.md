Random generator state cloning
==============================

This document discusses random generator state cloning in TF-PSA-Crypto and Mbed TLS: how it can happen, what problem it causes and how to solve it.

## What is cloning?

**Cloning** means that the state of the application has been copied, and there are multiple instances of the same application that initially have the same state. In this section, we discuss some common cases where cloning can happen. This is not an exhaustive list.

### Process forking

On Unix-like systems, a process (application instance) can be cloned with the [`fork()` system call](https://en.wikipedia.org/wiki/Fork_(system_call)), or with similar methods such as `clone()` on Linux. Often, `fork()` is only used to run a separate program (the child calls `execve()`), in which case any RNG state in the child is wiped before it is used. However, applications that use `fork()` with an active RNG that is used in the child process must pay attention to the RNG state.

### Virtual machine cloning

Virtual machine (VM) technology often allows freezing the state of a VM, then resuming it multiple times. This may be done, for example, to deploy it quickly to multiple hardware instances (concurrent clones), or to respond quickly to similar requests (serial clones).

When the system inside the VM resumes after cloning, the operating system running inside the VM must reseed its random generator. Additionally, any application that has its own random generator instance must also reseed.

Some environments broadcast VM cloning events. For example, some hypervisors gives each VM instance a unique [ACPI Virtual Machine Generation ID](https://download.microsoft.com/download/3/1/C/31CFC307-98CA-4CA5-914C-D9772691E214/VirtualMachineGenerationID.docx), and guest operating systems can respond to the ACPI `VM_GEN_COUNTER` event.
<!-- Linux had a proposal for propagating this event to userspace (https://lwn.net/Articles/887207/) but it has not gone through as of 6.18.0. -->

There is no cloning concern if a VM instance is merely migrated, i.e. only one copy of the VM instance is made and the original is destroyed.

### Resuming from hibernation

Some systems can hibernate, i.e. the system state is saved to persistent storage, then the system resumes later. This is fine if resuming destroys the hibernation image. However, in some environments, it is possible to resume multiple times from the same hibernation image. In such environments, the operating system must reseed its random generator after resuming from hibernation. Additionally, any application that has its own random generator instance must also reseed.

### Why is cloning a problem?

A cryptographic random generator consists of two parts: a seeding process which requires a non-deterministic source, and an algorithmic part which produces cryptographically strong random output from the seed.

If the state of a random generator is cloned, both instances will produce the same output until the random generator reseeds. This can be very bad for security since both instances will produce the same keys, the same nonces, etc. An adversary could even interact with one instance to obtain random generator outputs that are public (e.g. a protocol nonce), and use that knowledge to attack the other instance (e.g. a victim's session key).

As a consequence, if the application state is cloned, the random generator must not be used until each instance has a unique state, preferably obtained by reseeding from an entropy source.

## Random generator objects in Mbed TLS and TF-PSA-Crypto

### PSA random generator

Since TF-PSA-Crypto 1.0.0 and Mbed TLS 4.0.0, all random generation uses the random generator provided by the PSA subsystem. In previous versions, by default, the PSA subsystem is only used for PSA API calls and parts of TLS 1.3. When `MBEDTLS_USE_PSA_CRYPTO` is enabled, the PSA random generator is also used in parts of the PK, X.509 and TLS subsystems.

### Legacy random generators

Up to Mbed TLS 3.x, random generator objects are constructed as follows:

1. Instantiate an `mbedtls_entropy_context` object.
2. Instantiate a DRBG object (`mbedtls_ctr_drbg_context` or `mbedtls_hmac_drbg_context`).
3. Call the DRBG seed function (`mbedtls_ctr_drbg_seed()` or `mbedtls_hmac_drbg_seed()`), passing `mbedtls_entropy_func` as the entropy callback and the entropy object as the entropy context.

These objects are known as legacy random generators. They are passed explicitly to Mbed TLS functions, and used everywhere that doesn't use the [PSA random generator](#psa-random-generator).

## Protecting a program that calls `fork()`

### Automatic fork protection for PSA in modern library versions

In Mbed TLS 3.6.6 and later 3.6.x version, in TF-PSA-Crypto 1.1.0 and later versions, and in Mbed TLS 4.1.0 and later versions, the library automatically protects the [PSA random generator](#psa-random-generator) from the `fork()` system call on Unix-like platforms, except in a few edge cases discussed below. So applications using `fork()` and using only PSA APIs do not need to do anything, as long as they use a sufficiently recent library version.

Since TF-PSA-Crypto 1.1.0 (and Mbed TLS 3.6.6 for the 3.6 long-time support branch), the library uses an approach that is similar to the one [introduced in OpenSSL 0.9.5](https://github.com/openssl/openssl/commit/c1e744b9125a883450c2239ec55ea606c618a5c0) and in use since [OpenSSL 3.0.0](https://github.com/openssl/openssl/blob/openssl-3.6.0/providers/implementations/rands/drbg.c#L673): force a reseed if a process ID change is detected. This protection generally ensures that the parent and the child process will have unique RNG states. There are rare edge cases where forking can happen without a PID change, such as:

- If the child forks another process before invoking the random generator, but after the original process has died. In this case, it is rare but possible for the grandchild to have the same PID as the original process.
- When using the Linux `clone()` system call with the `CLONE_NEWPID` flag to put the child process in its own PID namespace, and the original process has PID 1.
- When the child is moved to a new or existing PID namespace before any call to the PSA random generator, and the PID in the child's namespace might match the PID of the original process.
- When using the Linux `clone3()` system call with a `set_tid` array to force the PID of the new process.

If your application might be concerned by these edge cases, you will need to treat forking as an external cloning event, as discussed in “[Protecting an application on a cloned system](#protecting-an-application-on-a-cloned-system)”.

### Protecting the PSA random generator with older library versions

TF-PSA-Crypto 1.0.0, Mbed TLS 4.0.0, and versions of Mbed TLS up to 3.6.5, do not protect the [PSA random generator](#psa-random-generator) against `fork()`. (If you obtain Mbed TLS from an operating system distribution package, it may have backported the fix — consult the package documentation.)

Here are some workarounds that you can use if your application uses PSA (either directly, or indirectly via TLS 1.3, or indirectly when `MBEDTLS_USE_PSA_CRYPTO` is enabled).

* If you instantiate the PSA subsystem with `psa_crypto_init()` only in the child process, i.e. if you never call `fork()` after `psa_crypto_init()`, then each child process gets an independent PSA random generator, and there is no problem.
* If a child does not use crypto APIs (for example, if a child only calls a few system functions and then `execve()`), the temporary existence of the PSA random generator in the child is irrelevant, and you do not need any special precautions.
* If you need the PSA subsystem in both the parent and the child, call `mbedtls_psa_crypto_free()` before forking and `psa_crypto_init()` after forking. Note that this destroys all keys in the parent except persistent keys.
* If you configure the library for prediction resistance (see “[Automatic reseeding through prediction resistance](#automatic-reseeding-through-prediction-resistance)”), your application is protected.

### Handling random generator objects in a forking program

If your application instantiates a [legacy random generator](#legacy-random-generators) in a parent process and uses them in a child created by `fork()`, you must reseed the random generator after forking, before using it. Call `mbedtls_ctr_drbg_reseed()` or `mbedtls_hmac_drbg_reseed()` in both the parent process and the child process, before using the random generator.

Note that additional considerations apply in configurations where the only entropy source is a nonvolatile seed. See “[Cloning with only a nonvolatile seed](#cloning-with-only-a-nonvolatile-seed)”.

## Protecting an application on a cloned system

This section discusses how to protect the random generator in an application that runs on a cloned system, for example in a cloned virtual machine or as part of a hibernation image that can be resumed multiple times.

To give each instance of the application a distinct random generator state, you need to reseed the random generator after cloning. This section discusses how to do it.

Note that additional considerations apply in configurations where the only entropy source is a nonvolatile seed. See “[Cloning with only a nonvolatile seed](#cloning-with-only-a-nonvolatile-seed)”.

### Reseeding the PSA random generator with modern library versions

In Mbed TLS 3.6.6 and later 3.6.x version, in TF-PSA-Crypto 1.1.0 and later versions, and in Mbed TLS 4.1.0 and later versions, the API includes functions to protect the [PSA random generator](#psa-random-generator) from cloning events. You can use one of the following methods:

* [`psa_random_reseed()`](https://mbed-tls.readthedocs.io/projects/api/en/development/api/group/group__psa__rng.html#ga89ab88e6bf0f001e8392f001145c4ef6) reseeds the random generator immediately. Call this function after cloning, before any use of the random generator.
* [`psa_random_deplete()`](https://mbed-tls.readthedocs.io/projects/api/en/development/api/group/group__psa__rng.html#gaf3195d46644616a257c41e2018ae4ed0) forces the random generator to reseed the next time it is used. Call this function before cloning, and ensure that the random generator is not used until after cloning.
* [`psa_random_set_prediction_resistance()`](https://mbed-tls.readthedocs.io/projects/api/en/development/api/group/group__psa__rng.html#ga16531bdabd1335c75e80167a7e086a68) enables or disables prediction resistance. When prediction resistance is enabled, the random generator reseeds on every use. Enable prediction resistance before cloning, and if desired, disable it after calling the random generator at least once after cloning.

### Protecting the PSA random generator with older library versions

TF-PSA-Crypto 1.0.0, Mbed TLS 4.0.0, and versions of Mbed TLS up to 3.6.5, do not offer APIs to control the reseeding of the [PSA random generator](#psa-random-generator). (If you obtain Mbed TLS from an operating system distribution package, it may have backported these functions — consult the package documentation.)

Here are some workarounds that you can use if your application uses PSA (either directly, or indirectly via TLS 1.3, or indirectly when `MBEDTLS_USE_PSA_CRYPTO` is enabled).

* The simplest approach, if doable, is to deinstantiate the PSA subsystem with `mbedtls_psa_crypto_free()` before cloning, and reinstantiate it with `psa_crypto_init()` after cloning. Note that this destroys all keys in the parent except persistent keys.
* If you configure the library for prediction resistance (see “[Automatic reseeding through prediction resistance](#automatic-reseeding-through-prediction-resistance)”), your application is protected.

### Reseeding a legacy random generator

If your application instantiates a [legacy random generator](#legacy-random-generators) and is cloned, call `mbedtls_ctr_drbg_reseed()` or `mbedtls_hmac_drbg_reseed()` after cloning, before using the random generator.

Note that additional considerations apply in configurations where the only entropy source is a nonvolatile seed. See “[Cloning with only a nonvolatile seed](#cloning-with-only-a-nonvolatile-seed)”.

### Operating system random generator after virtual machine cloning

By default, on Windows and Unix-like platforms, Mbed TLS and TF-PSA-Crypto rely on the operating system's random generator (`getrandom()`, `/dev/urandom`, `BCryptGenRandom()`, etc.). If your application runs as part of a [virtual machine which is cloned](#virtual-machine-cloning), beware that the operating system's random generator may itself be cloned, and your application may start running before the operating system has reseeded. Reseeding inside the library before the operating system would not provide any security.

## Automatic reseeding through prediction resistance

If the random generator has prediction resistance, it will automatically reseed every time it is used, so cloning does not require any special handling. You can enable prediction resistance in any of the following ways:

* Since TF-PSA-Crypto 1.0, you can enable prediction resistance at compile time by setting the reseed internal `MBEDTLS_PSA_RNG_RESEED_INTERVAL` to 1.
* Since TF-PSA-Crypto 1.1.0, you can enable prediction resistance at run time by calling `psa_random_set_prediction_resistance()`. This function is also available for the PSA random generator in Mbed TLS 3.6.x since version 3.6.6.
* In Mbed TLS 3.x, you can enable prediction resistance at compile time by setting the reseed interval (`MBEDTLS_CTR_DRBG_RESEED_INTERVAL` or `MBEDTLS_HMAC_DRBG_RESEED_INTERVAL`) to 1.
* In the Mbed TLS legacy API up to Mbed TLS 3.x, you can enable prediction resistance by calling `mbedtls_ctr_drbg_set_prediction_resistance()` or `mbedtls_hmac_drbg_set_prediction_resistance()` either when setting up the DRBG context, or on an active DRBG context.

Note that prediction resistance requires an actual entropy source. If the system only has a nonvolatile seed, as discussed in [“Reseeding with only a nonvolatile seed”](#reseeding-with-only-a-nonvolatile-seed), then prediction resistance in the DRBG is not sufficient in general to handle cloning securely.

## Cloning with only a nonvolatile seed

### What is a nonvolatile seed?

A [nonvolatile seed](https://mbed-tls.readthedocs.io/en/latest/kb/how-to/how_to_integrate_nv_seed/) (NV seed) is a file that contains entropy which is generated during the provisioning of a device, and is updated on each boot. This is a fallback mechanism for devices that lack an actual entropy source. Note that although the nonvolatile seed is considered an entropy source in the API documentation, it does not have the same security properties. Thus applications that are secure in configurations with an actual entropy source may be insecure in configurations where only a nonvolatile seed is available.

In Mbed TLS 2.x or 3.x, a configuration uses only a nonvolatile seed if `MBEDTLS_ENTROPY_NV_SEED` and `MBEDTLS_NO_PLATFORM_ENTROPY` are enabled, but `MBEDTLS_ENTROPY_HARDWARE_ALT` is not enabled. Since TF-PSA-Crypto 1.0.0, a configuration without actual entropy sources must enable `MBEDTLS_ENTROPY_NO_SOURCES_OK`.

### Sharing the nonvolatile seed

The nonvolatile seed is stored in a file. This file is updated during the initial seeding of the [PSA random generator](#psa-random-generator), and during the initial seeding of any entropy object used for a [legacy random generator](#legacy-random-generators). Note that the seed file is not modified when reseeding.

Thus, merely reseeding is not sufficient to protect the random generator when using only a nonvolatile seed.

### Nonvolatile seed and forking

In an application that calls `fork()`, the parent and the child read the same seed file. Hence, reseeding the random generator in both processes would merely move both of them to the same new state. To avoid this, use different personalization strings when reseeding (`additional` parameter to `mbedtls_ctr_drbg_reseed()`, `additional` parameter to `mbedtls_hmac_drbg_reseed()`, or `perso` parameter to `psa_random_reseed()`).

If you only reseed in the child process but not in the parent parent process, or vice versa, then the two processes do end up in different states. However, beware that a compromise of the non-reseeded process may allow the attacker to find out the random generator state in the reseeded process. Also, identical reseeding sequences would lead to identical states: in particular, reseeding only in the child process after `fork()` is insecure in general, since multiple children may end up with the same state.

### Cloning a system with a nonvolatile seed

If the whole system is cloned including the seed file, you can give each instance its own random generator state by reseeding the random generator with distinct values for the personalization string (`additional` parameter to `mbedtls_ctr_drbg_reseed()`, `additional` parameter to `mbedtls_hmac_drbg_reseed()`, or `perso` parameter to `psa_random_reseed()`). For example:

* If each clone has a globally unique identifier, include that identifier in the additional data when reseeding in the clone. Note that the identifier must be unique in both time and space. For example, a process ID is insufficient since most operating systems reuse process ID values after a while.
* If the original instance produces a single clone at a time, systematically reseed before creating the next clone.

# Race condition in AESNI support detection

**Title** | Race condition in AESNI support detection
--------- | ----------------------------------------------------------
**CVE** | CVE-2025-52496
**Date** | 30 June 2025
**Affects** | All versions of Mbed TLS up to 3.6.3
**Not affected** | Mbed TLS 3.6.4 and later
**Impact** | AES key disclosure and GCM forgeries through side channel
**Severity** | MEDIUM
**Credits** | Bug reported by Solar Designer

## Vulnerability

On x86 or amd64 processors that have the AESNI instruction, Mbed TLS can use this instruction for AES encryption and decryption. Likewise, Mbed TLS can use the CLMUL instruction for GCM tag calculations. Without these instructions, the library uses a portable, table-based implementation of the algorithms. The library function `mbedtls_aesni_has_support()` detects the presence of AESNI and CLMUL. The first time this function is called, it queries the processor features. The function caches the result in a global variable `c` for subsequent calls, and uses another global variable `done` to indicate that the result in `c` has been filled. The simplified code looks like this:

```
static int done = 0;
static unsigned c = 0;
if (!done) {
    c = cpuid(...); // query processor features
    done = 1;
}
```

Depending on compiler optimizations in `mbedtls_aesni_has_support()`, the compiled program may execute a store instruction for the variable `done` before the store of `c`. Hence the following race condition may be possible in a multithreaded program:

1. Thread 1 starts an AES or GCM operation, and calls `mbedtls_aesni_has_support()`. That is the first invocation of the function. It incorrectly updates `done` before it has updated `c`.
2. Thread 2 starts an AES or GCM operation, and calls `mbedtls_aesni_has_support()`. That invocation reads `done` which tells it that `c` contains the detection result. But `c` still contains the startup default value 0, which indicates that the feature is not present. Therefore the AES or GCM operation in thread 2 will use the portable, table-based implementation.
3. Thread 1 updates `c`. It and subsequent callers will use the actual hardware capabilities.

This is a security vulnerability because the portable, table-based implementations of AES and GCM are vulnerable to timing-based side channel attacks.

On its own, the vulnerability is unlikely to be exploitable, since the window of vulnerability is very small. However, if the attacker can block thread 1 from progressing, the window of vulnerability may be large.

## Impact

On x86 or amd64 processors, an adversary may be able to extract AES keys from multithreaded programs. The same attack may also allow GCM forgeries. The adversary needs both of the following capabilities:

* Ability to detect which memory addresses a victim thread accesses. Local unprivileged attackers typically have this ability through cache timing measurements.
* Ability to suspend the execution of a victim thread. Even powerful local attackers usually do not have this ability. However it may be possible in some scenarios, such the normal operating system attacking an SGX enclave.

## Affected versions

All versions of Mbed TLS up to and including 3.6.3 are affected.

## Resolution

Affected users should upgrade to Mbed TLS 3.6.4.

## Work-around

Users who do not need their code to work on processors without AESNI and CLMUL instructions can compile Mbed TLS with the configuration option `MBEDTLS_AES_USE_HARDWARE_ONLY` enabled. This option disables the table-based implementations of AES and GCM, leaving only the hardware-accelerated implementations.

As soon as one call to `mbedtls_aesni_has_support()` has completed in a program instance, subsequent calls will use the correct value. Therefore a program is not vulnerable if one thread performs an AES operation before any other thread starts an AES operation. Single-threaded programs are not affected.

The race condition is only present if the compiler orders the variable updates in a problematic way. We have observed that GCC up to 6.x tends to produce vulnerable binaries at higher optimization levels (`-Os`, `-O2` and above). We have not observed vulnerable binaries with GCC 7.x and above, or with Clang, but this may vary between versions, optimization levels and programs. GCC 10.x and above are safe thanks to a memory barrier in its `__cpuid` intrinsic.

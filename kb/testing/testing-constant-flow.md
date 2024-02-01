# Tools for testing constant-flow code

Code that manipulates secret values (private keys, etc.) needs to be constant-flow (often called constant-time, though the requirements are actually stricter than "the total running time is a constant"), that is contain no branches that depend on secret values, and no memory accesses at addresses depending on a secret value, in order to avoid leaking the secret value through side channels.

Ideally, this should not only be enforced by code review, but also tested or checked by tools. This pages list some available options.

## Dynamic analyzers

### ctgrind (obsolete)

Listed for historical reference. This was a dynamic library and patch to valgrind, built on the following fundamental observation by its author, Adam Langley:

> This would mean keeping track of every bit in memory to know if it's secret or not, likewise for all the CPU registers. Preferably at the bit level. The tool would also have to know that adding secret and non-secret data results in secret data etc. That suggests that it would be quite a complex tool.
> But memcheck already does this! In order to keep track of uninitialised data it shadows every bit of memory and will warn you if you use uninitialised data in a branch or to index a memory access. So if we could tell memcheck to treat our secret data as uninitialised, everything should just work.

https://github.com/agl/ctgrind

The project is now obsolete thanks to the options below, which are built on the same idea: (ab)use existing tools checking for use of undefined memory.

### Valgrind's memcheck

It turns out patching valgrind and using a helper library is not necessary, as everything we need is already provided by memcheck: after including `valgrind/memcheck.h` we can use the macros `VALGRIND_MAKE_MEM_UNDEFINED(addr, len)` and `VALGRIND_MAKE_MEM_DEFINED(addr, len)` to mark data as secret (undefined) or no longer secret (defined).

These macros have been available under that name since [3.2.0 (7 June 2006)](https://www.valgrind.org/docs/manual/dist.news.old.html).

References:
- https://valgrind.org/docs/manual/mc-manual.html
- https://github.com/mozilla-b2g/valgrind/blob/master/memcheck/memcheck.h

Pros:
- valgrind/memcheck is already used in our CI
- large number of [supported architectures/platforms](https://valgrind.org/info/platforms.html)
- works with any compiler
- works with inline asm
- already used by other projects such as [in BoringSSL](https://boringssl.googlesource.com/boringssl/+/a6a049a6fb51a052347611d41583a0622bc89d60)

Cons:
- just like normal use of valgrind's memcheck, slows down execution by about 20-30x.
- preliminary testing (by Manuel on a personal project) suggests there may be issues with relative ordering of calls to the macros and use of the values in some uses cases (for example, doing a simple sanity check before marking the value as secret flags the sanity check as accessing undefined memory).

Note: since 2.24.0 we're using this: see `MBEDTLS_TEST_CONSTANT_FLOW_VALGRIND` in `config.h`; components `test_valgrind_constant_flow` and `test_valgrind_constant_flow_psa` in `all.sh`; and `tests/suites/test_suite_constant_time`.

### MemSan

Works in a very similar way to valgrind's memcheck: compiling with `clang -fsanitize=memory`, after including `sanitizer/msan_interface.h`, the two following functions (and a couple more) can be used to mark memory areas as secret/undefined or public/defined.
```
  /* Make memory region fully initialized (without changing its contents). */
  void __msan_unpoison(const volatile void *a, size_t size);

  /* Tell MSan about newly allocated memory (ex.: custom allocator).
     Memory will be marked uninitialized, with origin at the call site. */
  void __msan_allocated_memory(const volatile void* data, size_t size);
```

References:
- https://clang.llvm.org/docs/MemorySanitizer.html
- https://github.com/google/sanitizers/wiki/MemorySanitizer
- https://github.com/llvm-mirror/compiler-rt/blob/master/include/sanitizer/msan_interface.h

Pros:
- clang/memsan is already used in our CI
- much faster than valgrind/memcheck (only 2-3x slowdown, so about 10x faster than using valgrind)

Cons:
- only works with clang on Linux, FreeBSD, NetBSD
- being compile-time instrumentation, limited with respect to inline assembly
- for the same reason, misses branches in toolchain-provided functions (for example long multiplication, see [this paper](https://core.ac.uk/download/pdf/188281541.pdf)) which valgrind would see
- has an annoying bug where it [misses secret-dependent memory accesses via libc functions](https://github.com/google/sanitizers/issues/1296)

Note: since 2.24.0 we're using this: see `MBEDTLS_TEST_CONSTANT_FLOW_MEMSAN` in `config.h`; components `test_memsan_constant_flow` and ``test_memsan_constant_flow_psa` in `all.sh`; and `tests/suites/test_suite_constant_time`.

### Custom tools

From looking at papers, it seems that various researchers are using various custom tools for finding leaks in cryptographic software. However it is unclear if those are publicly available, and being developed by academics mainly for their own use, it's also unclear how easy they would be to deploy on our CI infrastructure.

## Static analyzers and formal guarantees

In recent years there seems to be more interest from the programming languages community in eliminating side-channel attacks by providing some form of formal guarantee of safety. These methods usually involve making a new (or modifying a) language/compiler that can detect the incorrect usage of secrets.

References:
- http://cuda.dcc.ufmg.br/flowtracker/
- https://ranjitjhala.github.io/static/fact_dsl.pdf
- https://eprint.iacr.org/2019/1393.pdf#section.4 (section IV, useful summary of recent ideas)

Pros:
- Often provides some guarantee of safety
- Can sometimes transform more readable unsafe code into safe code.

Cons:
- May involve rewriting sections of constant-time code
- Still potential for safe code but unsafe binaries

## Empirical methods

There appears to be some empirical testing tools available for testing constant time code. Tools such as [dudect](https://github.com/oreparaz/dudect#dudect-dude-is-my-code-constant-time) work by running the program with different inputs and trying to detect statistically different execution times. While these tools may not provide formal guarantees of safety against side-channel attacks it could be a useful, and easy to implement, metric for constant time code.

## Compiler support

In my (Manuel) ideal world, we would have some way to tell the compiler "please try hard not introduce branches in this region of the code, and fail loudly if you can't", but I don't think that's available anywhere yet.

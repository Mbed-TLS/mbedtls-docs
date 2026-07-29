# Writing a proof-of-concept for a vulnerability

This document provides some guidelines on writing a proof-of-concept (PoC) when reporting a vulnerability in TF-PSA-Crypto or Mbed TLS.

## What is a proof-of-concept (PoC)?

A PoC for a security issue is an artifact that demonstrates a vulnerability. It can take different forms, typically an input file, a small program, or a test case. It should illustrate how an attacker can cause a security property to be violated in a victim program.

A PoC does not need to be a full exploit. It only needs to produce observable evidence that a security property is violated.

## Is a PoC needed?

The TF-PSA-Crypto and Mbed TLS security team do not require a PoC in security vulnerability reports. However, they can be useful to understand precisely what the vulnerability claim is, to assess the correctness of the claim, and to validate a fix.

The Intigriti bounty program requires a PoC.

## Requirements on a PoC

This section discusses requirements on a PoC. We have found that submissions based on LLM (large language models, “AI”) often fail to distinguish an attacker from the victim, or target internal interfaces in the victim, and that leads to unfounded claims. Please pay careful attention to these requirements in any LLM-assisted report.

### Separate the victim from the attacker

The PoC should make it clear what part is the victim and what part is the attacker. The attacker tries to cause something bad to happen. The victim suffers consequences from the bad thing, such as incorrect operation, leaking secret data, etc.

In some types of vulnerability, the victim is a correct program and the attacker only needs to supply a data file that is passed as input to this program. For example, to demonstrate a parser bug, the PoC generally consists of a small victim program (possibly one of the sample programs provided with the library), and the attacker is instantiated through a specially crafted input file.

In some types of vulnerabilities, especially bugs in the TLS protocol, the attacker needs to have a more active role. In such cases, it is often helpful to split the PoC into a victim program and an attacker program. The attacker does not have to use Mbed TLS, although if it does, this can help us understand what the attacker is doing. For example, for a vulnerability that lets a client attack a TLS server, the preferred PoC consists of an attacker TLS client, combined with one of the sample or test TLS servers provided with Mbed TLS.

### Correct API use in the victim

The victim program must only use documented APIs, and must use them correctly according to the library documentation and according to the use of the C language. In particular:

* Only use functions declared in a public header (headers installed by `make install` or `cmake --install`). Private functions might not check for invalid inputs if they are only meant to be called from higher-level functions that check the inputs first.
* Do not access private fields of structures (do not define `MBEDTLS_ALLOW_PRIVATE_ACCESS`, and do not access `foo.private_xxx` explicitly). Private fields may not have the meaning that you expect, and modifying them has undefined behavior.
* Obey the rules of the C language: if the application code violates these rules, the behavior of the library is undefined. This includes rules given in function documentation: for example, if a function requires a “pointer to N bytes”, and the function crashes when you pass a null pointer, that's a programmer error, not a library bug.

Any violation of these rules disqualifies the PoC.

## Structure of a PoC

This section discusses the preferred structure of a PoC. These are guidelines, not requirements. You do not have to follow them, but they make our life easier.

Note that LLM tend to be fairly good at picking up the structure of our test code, including finding poorly documented auxiliary functions. However, without proper guidance, LLM tend to use internal functions. Internal functions should not be used in victim code, since their behavior is not part of the library's contract.

### PoC using a sample program

For parser bugs, an input that causes a sample program to crash is sufficient as a PoC. You do not need to write your own program if one already exists.

### PoC as a unit test

For TF-PSA-Crypto and Mbed TLS maintainers, the ideal form of a PoC is a non-regression test for the bug. This means a new test case in `tests/suites/test_suite_*.data` which either fails at a clearly valid assertion, or causes memory corruption inside the library. Note that if the bug causes memory corruption, you should not try to detect it in the code: instead, rely on compile-time or run-time instrumentation such as AddressSanitizer (ASan) or Valgrind.

Depending on how close the existing test functions come to reaching the bug, you might either:

* add a new test case for an existing function;
* or add an assertion to the existing code;
* or write a new test function.

If you write a new test function, it is helpful if you can provide a variant of the test that passes, to help locate the cause of the bug.

Note that unit tests have easy access to internal interfaces of individual library modules. A violation of an internal contract does not demonstrate a vulnerability. A violation of a public contract, reached by using internal functions, does not demonstrate a vulnerability either. To demonstrate a vulnerability, make sure that the victim code only uses public interfaces.

### PoC using SSL test programs

For TLS bugs, depending on the way the vulnerability can be triggered, it may be more convenient to use the test programs `programs/ssl/ssl_client2` and `programs/ssl/ssl_server2`. For bugs involving non-nominal DTLS traffic, `programs/test/udp_proxy` can be useful. These programs are normally invoked via `tests/ssl-opt.sh`. A test case in `tests/ssl-opt.sh` is a convenient way to demonstrate a TLS bug. Our tooling is set up to either run `ssl_client2` against `ssl_server2`, or run one of them against an OpenSSL or GnuTLS peer.

Note that if the bug causes memory corruption, you should not try to detect it in the code: instead, rely on compile-time or run-time instrumentation such as AddressSanitizer (ASan) or Valgrind.

Note that `ssl_client2` and `ssl_server2` have access to internal functions that can create malformed traffic or put the SSL context in unexpected states. When demonstrating a vulnerability, the attacker side may use whatever is convenient to construct malformed traffic. On the other hand, the victim side must not rely on calls to internal functions, since that would fail to demonstrate a security impact. If the vulnerability affects a client or server in the default runtime configuration, you may use `programs/ssl/ssl_client1` or `programs/ssl/ssl_server` as the victim.

## Considerations for particular classes of vulnerabilities

### PoC for memory corruption

If the vulnerability is a memory corruption (buffer overflow, use-after-free, double free, etc.), then the PoC only needs to reach the stage where the memory is corrupted. It is not useful to demonstrate concrete effects beyond that.

Our preferred tool for analyzing memory corruption is AddressSanitizer (ASan). If a program causes ASan to crash from correct use of the library, that is a good PoC.

### Side channels

Leakage through side channels is often difficult to reproduce and often requires complicated analysis. If you are writing an academic paper about a side channel attack, you do not need to share your tooling. We may be interested on a personal basis, but it is usually not practically useful for our triage and fixing.

# Spectre and Meltdown

## Introduction

Spectre and Meltdown are security flaws, recently and independently discovered by
researchers at Google Project Zero and other organizations [[1]] [[2]] [[3]].
The originality of the Meltdown and Spectre attacks is that they exploit
security vulnerabilities in the microarchitecture of modern microprocessors,
even if the microprocessors have been implemented correctly against their own
architecture. What this means is that an attacker could recover sensitive data
by taking advantage of information leaks present in the hardware, even if the
processor preserves the correct behavior from the programmer's point of view.

In this article, we provide a brief description of these attacks, analyze
their impact on Mbed TLS and provide mitigations.

## Background on Computer Architecture

Spectre and Meltdown exploit vulnerabilities in the hardware and some
knowledge of processor optimization techniques is necessary for understanding
the attacks. The following section provides this background
information, but can be safely skipped if you are already familiar with these concepts.

### Architecture vs Microarchitecture

Most software developers are familiar with the concept of an architecture, which
refers to the contract between a programmer and the underlying hardware in a
system. The architecture includes the Instruction Set Architecture (ISA) and
other important information, such as the memory consistency and input/output
models. However, there are usually many different implementations (or
microarchitectures) of an architecture. For example, the Arm Cortex-A53 and
Cortex-A57 processors are different microarchitectures of the ARMv8-A
architecture. While programmers can monitor aspects of the architecture, they 
cannot directly observe many aspects of a microarchitecture, such as caching, speculative
execution and branch prediction. These will be discussed below.

### Out-of-Order and Speculative Execution

In many architectures, such as Arm and x86, we expect processors to execute
instructions in sequential order as they appear in the execution path.  In
practice, however, advanced processors only give the illusion of sequential
execution. Internally, out-of-order execution techniques are used to reorder
operations whenever possible, to maximize the utilization of execution units,
and ultimately, the throughput of the processor.

It is common for out-of-order processors to also support speculative execution.
If the processor encounters a branch instruction, then before it can be fully
resolved, the processor guesses what execution path will be taken and
speculatively processes instructions along that path. When the branch is fully
resolved, the processor either continues executing as normal, if the guess was
correct, or reverts to the correct architectural state just after the execution
of the branch. However, side effects of the incorrect execution path remain
observable in the microarchitectural state, as this is not fully reverted, and this makes 
the Meltdown and Spectre attacks possible.

### Branch Prediction

Speculative execution requires the processor to guess the outcome of branch
instructions. Accurate predictions are desirable, as they improve
performance, and branch prediction techniques are used to increase said
accuracy.

In a simple scenario, branch predictors always predict the same outcome. For
example, if they always predict that branches to lower and higher addresses are
taken and not taken respectively, this may improve the performance of loops.
However, high-end processors typically have complex prediction schemes and
special purpose hardware that constitutes a significant portion of the
processor core. The following two components of branch predictors are the most
relevant for understanding the Meltdown and Spectre attacks:

* Branch Target Buffer (BTB): When the branch is indirect (there is more than
  one possible target address), it is necessary to maintain a BTB, a buffer
  that maps the source to target address of branch instructions.
* Branch History: The target of a branch instruction can change depending on a
  condition. In this case, the processor records the conditional outcomes of
  the last N executions of the branch, and uses this information to make an
  educated guess about the resolution of the condition when the instruction is
  executed again.

### Address Spaces

Virtual memory is a technique that is widely used in modern computers for a
variety of reasons. One of its aims is to isolate processes from each other,
that is, to give the illusion that every process is executing on its own
address space and unable to directly access another process's memory.

Virtual memory is generally divided in 4KB pages, and virtual
addresses are translated to physical ones with the help of a page table (often
by a hardware memory management unit). As the supervisor of the system, the
kernel performs operations on behalf of user processes, as well as many other
managerial operations. For performance reasons, it is common to map kernel
addresses into the user process's virtual address space. In turn, a subset of
the kernel addresses maps to physical memory. However, pages have associated
access permissions stored in the page table to restrict the process's access,
and the kernel manages these permissions.

### The Memory Hierarchy

Due to the disparity in speed between the memory and the processor, computer
architects use various types of memory devices within a single system. This
structure of the memory subsystem is known as the "memory hierarchy," where the
memory technologies that are fastest, most expensive and with less capacity
(e.g registers and caches) are closer to the processor, while slower, cheaper
and larger memories (e.g DRAM, flash, disk) are further away.

When the processor accesses an address, the memory closer to the processor is
searched first. If the data is not found there, then the next component further
down the memory hierarchy is searched, and so on, until the data is found.
However, the access latency of memory devices increases dramatically as each
level down the hierarchy is accessed. For example, according to the
Performance Analysis Guide [[9]], in an Intel Core i7 processor, the latency of
accessing the L3 cache is as low as ~40 cycles, while accessing local DRAM costs
~60 nanoseconds (or ~200 cycles with a 3.4GHz clock). It is partly this
disparity that techniques, such as speculative execution, aim to mitigate. For
example, while a branch based on a memory access is resolved, the processor
might be speculatively executing tens of instructions in the meantime.

As previously discussed, when a branch prediction is incorrect, the processor
will revert to its last correct architectural state (just after executing the
mispredicted branch). However, side effects of the invalid state can still be
observed in the microarchitecture, potentially leaking sensitive data. The
Meltdown and Spectre attacks rely on the state of the cache not being rolled
back when a misprediction occurs. Well understood cache timing side-channel
attacks can be used to recover the leaked data to an architecturally valid
state (e.g a general-purpose register), as applications cannot directly observe
changes in the microarchitectural state of the cache.

## Basic Building Blocks of the Attack

This section describes the main building blocks of the Spectre and Meltdown
attacks.

### Transient Instructions

Transient instructions are those that would never be executed in a program's
strict execution path, but are executed early by an out-of-order pipeline. For
example, consider the following instruction sequence:

```
1 if (a < length)
2     b = mem[a]
3 else
4     b = 0
```

If, on reaching this fragment of code, the processor is unable to resolve the
branch in line 1, it might speculate that the correct execution path is the
statement in line 2, which could cause a buffer over-read if `a >= length`.
However, when the branch condition is resolved, the processor will recover from
this incorrect state and start executing from line 4.

While the architectural effects of transient instructions are rolled back, the
microarchitectural state of the processor is changed in noticeable ways,
potentially leaking data to an architectural state. For example, in the case of
the trivial code above, a new line could have been inserted in the cache.  This
can be checked by simply measuring the time of the next memory access and
comparing it to the access time of a location that is known to be in the cache.

### Covert Channel

The covert channel is a means to transfer leaked information by transient
instructions from the microarchitectural state to an architectural one. In the
case of both Meltdown and Spectre, the covert channel is constructed using well
known cache timing side-channels. For example, the Flush+Reload timing
side-channel attack detects whether a memory location is cached [[1]].

The covert channel can be thought of as having sender and receiver ends. The
sender has access to an array, and the receiver simply needs to be aware of the
array's location. For example, consider a program with the following array:

```
uint8_t probe[256 * <cache_line_size>]
```

To send a byte of data `b` using the covert channel, the sender executes a
memory load of the form `probe[b * <cache_line_size>]`. This will load exactly
1 cache line out of 256 (assuming that it was not already cached). Then, at the
receiving end, the attacker simply uses the Flush+Reload technique on each of
the 256 possible cache lines to check which one is loaded, thus retrieving the
byte value `b`. Note that the array is of length:

```
2^n * <cache_line_size>
```

where `n` is the number of bits transferred per exchange and
`<cache_line_size>` is the size (in bytes) of a cache line.

## Spectre

Spectre bypasses the process's memory isolation mechanisms. It exploits
information leaks by taking advantage of the branch predictor and out-of-order
execution to recover secret information via microarchitectural covert channels.
The remainder of this section describes two variants of this attack.

### Variant 1: Bounds Check Bypass

As discussed above, branch predictors often maintain the history of executed
branches to make an educated guess about the next resolution of a branch before
the condition itself is evaluated. Variant 1 of the Spectre attack relies on
training the branch predictor to incorrectly speculate on a branch, so that
data is leaked via the covert channel. For example, consider the following
fragment of code from the Spectre paper [[2]]:

    1 if (x < array1_size)
    2     y = array2[array1[x] * 256];

If, upon reaching line 1, the value of `array1_size` is not cached, then the
processor might speculate incorrectly when `x >= array1_size` and execute line
2. Before the misprediction is confirmed, the loads from `array1` and `array2`
succeed. Later, the processor rolls back its architectural state, but changes
to the cache still linger. Thus, the attacker simply needs to run the receiving
end of the covert channel to recover the secret value of the byte `array1[x]`.

### Variant 2: Branch Target Injection

Indirect branches are those that have more than two destination addresses. As
discussed above, branch predictors are equipped with a Branch Target
Buffer (BTB) that maps the branch source to target addresses. Variant 2 of the
Spectre attack relies on training the branch predictor to predict an incorrect
target address. Before the correct target address is resolved, transient
instructions are executed leaking secret information via a covert channel.

For this attack to work, the attacker must first identify two pieces of code
in the victim's source code:

1. A sequence of instructions that uses registers, whose values can be
   manipulated by the attacker. These are typically functions that receive user
   inputs. Furthermore, the code must have an indirect branch.
2. A sequence of instructions that uses the registers from (1), so that
   sensitive data is leaked. The start of this sequence will be the target
   address of the misprediction.

The attacker must also train the branch predictor to map the source to the
chosen destination address in the BTB. Note that, due to the lack of isolation
between processes in the BTB, it is feasible to train the branch predictor from
a different unprivileged process to the one being attacked. The attacker then
needs to stimulate the victim into executing the code path in point (1) above.
Finally, the attacker uses the covert channel to recover the data.

## Meltdown (Variant 3: Rogue Data Cache Load)

The Meltdown attack exploits microarchitectural data leaks in the processor's
out-of-order execution machinery. To mount the attack, the attacker needs a covert channel
where the sender end triggers a cache load at an address constructed using a
value from kernel memory. The code sequence provided in the Meltdown paper is
as follows [[1]]:

```
1 ; rcx = kernel address
2 ; rbx = probe array
3 retry:
4 mov al, byte [rcx]
5 shl rax, 0xc
6 jz retry
7 mov rbx, qword [rbx + rax]
```

In this code, the register `rcx` holds a kernel address, which is then used to
load a byte of kernel memory into the least significant byte of the `rax`
register in line 4. In line 5, the kernel data byte in `rax` is used to
construct an index into the `probe` array by performing a 12 bit shift left
(equivalent to multiplying by 4096 bytes, the page size), and the result is
written back to `rax`. Finally, a load from the `probe` array at the index in
`rax` is executed in line 7. Due to out-of-order execution, it is likely that
the transient instructions between lines 5-7 are executed before an exception
is raised, as a result of the invalid address in line 4. This small time window,
between the memory being accessed and the exception being raised, is all that is
needed to leak information.

To recover the secret data from the microarchitectural state into an
architectural one, the receiver end of the covert channel simply needs to run
the Flush+Reload cache timing side-channel attack to find out which cache line
from the `probe` array was loaded. The process is repeated to recover more
inaccessible data from an unprivileged process, yet the attacker must have a
mechanism to either catch or suppress the exception raised by the processor.

Unlike Spectre, the Meltdown attack can only recover protected data that is
mapped into the attacker process's memory space.
This means Meltdown can only be used to recover data
from the kernel pages mapped into the user's virtual memory.  However, in many
modern systems, a subset of the kernel addresses map to physical memory, in which
case, Meltdown can recover the contents of most (if not all) of the
physical memory. Given that other processes' data will reside in physical
memory, Meltdown can bypass the memory isolation between processes.

## Impact on Mbed TLS and Mitigations

At this time, there are no reports of Spectre and Meltdown-style
attacks that have been successfully deployed on production systems, although
proof-of-concept attacks have been created by researchers. As a security
library, Mbed TLS could be a prime target for Spectre and Meltdown attacks attempting to
retrieve sensitive information, such as keys, passwords, decrypted data, etc.

It is important to highlight that the attacks discussed only impact processors
that implement out-of-order execution, in the case of Meltdown, and
branch prediction, in the case of Spectre. However, the microarchitecture of processors
varies significantly between vendors and even product lines. Therefore, we
recommend that you consult your vendor's documentation to confirm whether your
hardware is affected. The References section below has links to several
processor vendors' information pages: Arm [[5]], AMD [[8]] and Intel [[7]].

The remainder of this section analyzes the impact of Meltdown and Spectre on
affected systems and provides information on how to mitigate it.

### Spectre: Variants 1

This attack has been demonstrated using a JIT engine within the Linux kernel.
However, in practice, the attacker must manually inspect the victim's code that
is usable for the attack. The code should load a value using an untrusted
offset and use the result to form a second address, so that meaningful
information is leaked [[6]]. The most effective mitigation is to entirely avoid
such sequences of instruction, when possible. Depending on the architecture, 
you might also be able to implement instruction sequences, so
that data is not leaked by speculative execution. For example, in the case of
Arm, this can be achieved by using conditional selection or conditional move
instruction based on the condition that is used to determine the outcome of the
branch [[6]].

When it is not possible to use the above mitigation, the processor can
implement barrier instructions that prevent the speculation from taking place.
In the case of Intel x86, the Spectre paper suggests that the lfence and mfence
instructions prevent the attack [[2]]. It is also possible to use tools, such
as compilers, to insert these instructions where they are relevant. For example,
compiler support is being introduced into GCC and LLVM to mitigate this variant 
(for more information refer to [[10]]).

In the case of Mbed TLS, we have not yet found usable pieces of code for the
Spectre variant 1 of the attack.

### Spectre: Variant 2

As with Variant 1, the attacker must manually inspect the victim's code to
find usable pieces of transient instructions that can be connected in a
return-oriented programming fashion to leak information via the processor's
microarchitecture. The attacker must also train the branch predictor to predict
the wrong destination address for the selected branch instructions. This can be
achieved by a separate, unprivileged process, as access to the branch
predictor is generally not filtered. For the training to succeed, some
understanding of the branch prediction algorithm is required.  While this is a
closely guarded secret by many processor vendors, researchers have reverse
engineered enough information to successfully mount the attack.

Security updates for the major operating systems have been issued, and even
microcode updates for specific hardware have been released. Yet, these mitigations 
might only be partial, as in some cases, microarchitectural changes are required. 
From a software point of view, there are no definitive solutions to mitigating 
this attack. This is partially because branch predictors vary
significantly across architectures and even product lines. For example, Arm
recommends invalidating branch predictors when switching from privileged to
unprivileged processes, whenever possible, or disabling branch prediction
altogether [[6]]. However, both of these solutions are likely have a significant
impact on performance, and this feature is not always present in the underlying
system. We recommended consulting the vendor's documentation directly for
information specific to your processor. In some cases, it may be possible to
avoid indirect branches, but this is largely unfeasible, as these
branches are constructed by the compiler, and important steps in the toolchain,
such as linking, heavily depend on the capabilities of indirect branches.

### Meltdown: Variant 3

In many affected systems, the attackers can use Meltdown to read (but not
modify) the full contents held in physical RAM, including data that belongs to
other privileged or unprivileged processes. In the case of a system running
Mbed TLS, either as a client or as a server, the attacker can retrieve
confidential information in main memory, such as the TLS session keys. It
is also possible for the attacker to stimulate another application to load pages stored
in lower layers of the memory hierarchy (e.g the swap partition in a hard
drive) into the main memory, and then run the Meltdown attack to recover the
information. Once the attacker has recovered the confidential information, they
can use it in any way they please. For example, an attacker can use recovered
TLS sessions keys to spy on an open TLS connection, or AES keys to decrypt a
file. The attack is also independent of any software vulnerabilities, so that
conventional operating system security practices, such as address space
layout randomization, do not prevent Meltdown.

In practice, for Meltdown to work, the attacker must be given remote access 
and permission to execute an unprivileged program in the target computer.
Therefore, we recommended that Mbed TLS users maintain security best
practices, such as avoiding executing applications or code from untrusted
sources. The Meltdown attack also affects paravirtualized environments
(e.g Xen) and containers (e.g Docker), but not fully virtualized environments.
When running Mbed TLS in shared systems, such as is common in web hosting
services, we recommended ensuring that the underlying operating
system/environment has the latest security updates.

All major operating system vendors have released security updates to prevent the attack. 
Broadly speaking, the idea is to only map a small subset of the kernel address space into other processes'
virtual address space, so that the unprivileged processes cannot attempt to
access physical memory and leak its contents through the microarchitecture.
KAISER is a proof-of-concept of this idea, but unfortunately, this can have
a high impact on performance. KAISER enforces strict kernel and user space
isolation, so that user processes cannot access any kernel information, as this
is not held by the hardware [[4]].

## Conclusion

The Meltdown and Spectre attacks are vulnerabilities in architecturally correct
hardware. The attacks rely on processor optimization techniques, such as
out-of-order execution and branch prediction, to leak information through the
microarchitecture while executing transient instructions. They then recover
the data through cache timing side-channel attacks. The attacks do not rely on
vulnerabilies in the software, but there are mitigations that can be implemented 
into the software to prevent them. It is important to highlight that not all 
hardware platforms are affected by these attacks. For more information on which 
processors are vulnerable, refer to your vendor's documentation (see [References](#references)).

Like other attacks on the application code, system, or hardware that is
hosting Mbed TLS as a security library, Mbed TLS cannot fully defend against
these attacks by itself. It is built on the assumption that the underlying
hardware provides some basic building blocks for security, such as process
isolation, which is violated by Meltdown and Spectre. The following is a
comprehensive list of advice and actions that Mbed TLS users can implement to more
effectively prevent these attacks:

* Review the processor vendor's security information to find out if your
  system is affected, and apply the vendor's security guidelines where
  appropriate.
* Maintain up-to-date systems with the latest security updates from the
  operating system vendor, and if necessary, any microcode updates issued by
  the processor vendor.
* Ensure you are using the most recent version of Mbed TLS, and that you can
  update your system as new versions become available.
* Ensure you follow security best practices and guidelines. For example, do not
  run any unstrusted software.
* Identify and patch any source code in your software that may be
  vulnerable to a variant of the Spectre attack. Remember that these attacks
  might not be fully prevented by operating system updates, and changes to
  vulnerable software might be necessary. 
* Check for upcoming compiler and tool updates to defend against Spectre.

## References

[1]: https://meltdownattack.com/meltdown.pdf
[2]: https://spectreattack.com/spectre.pdf
[3]: https://googleprojectzero.blogspot.co.uk/2018/01/reading-privileged-memory-with-side.html
[4]: https://gruss.cc/files/kaiser.pdf
[5]: https://developer.arm.com/support/security-update
[6]: https://developer.arm.com/support/security-update/download-the-whitepaper
[7]: https://security-center.intel.com/advisory.aspx?intelid=INTEL-SA-00088&languageid=en-fr
[8]: https://www.amd.com/en/corporate/speculative-execution
[9]: https://software.intel.com/sites/products/collateral/hpc/vtune/performance_analysis_guide.pdf
[10]: https://developer.arm.com/support/security-update/compiler-support-for-mitigations

[1. Meltdown paper](https://meltdownattack.com/meltdown.pdf)

[2. Spectre paper](https://spectreattack.com/spectre.pdf)

[3. Google Project Zero blog post](https://googleprojectzero.blogspot.co.uk/2018/01/reading-privileged-memory-with-side.html)

[4. KAISER](https://gruss.cc/files/kaiser.pdf)

[5. Arm's Security Update](https://developer.arm.com/support/security-update)

[6. Arm's Cache Speculation Side-channels whitepaper](https://developer.arm.com/support/security-update/download-the-whitepaper)

[7. Intel's Security Advisory](https://security-center.intel.com/advisory.aspx?intelid=INTEL-SA-00088&languageid=en-fr)

[8. AMD's Security Advisory](https://www.amd.com/en/corporate/speculative-execution)

[9. Performance Analysis Guide for Intel Core i7 Processor and Intel Xeon 5500 processor](https://software.intel.com/sites/products/collateral/hpc/vtune/performance_analysis_guide.pdf)

[10. Compiler support for mitigations](https://developer.arm.com/support/security-update/compiler-support-for-mitigations)

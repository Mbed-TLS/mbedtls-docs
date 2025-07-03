# Tips for debugging Mbed TLS

This is a collection of tips for debugging TF-PSA-Crypto or Mbed TLS.
It may also be useful for debugging applications using these projects, but that is not this document's main purpose.

This document assumes some familiarity with the project, e.g. that you already know how to build and test it.

This document is written primarily with Linux in mind. Similar platforms such as macOS will require few adaptations. Windows (except WSL) is out of scope.

## Reverse debugging

### What is reverse debugging?

Also known as back-in-time debugging or time travel debugging.

Reverse debugging allows you to go backward in time when stepping through a program. For example, a reverse single step after returning from a function goes back to the function's `return` statement.

### Tools for reverse debugging

* Gdb supports reverse debugging, but not out of the box, it requires some complex setup.
* LLDB does not support reverse debugging as of 2025.
* Visual Studio (under Windows) supports reverse debugging since 2017.

Reverse debugging works by taking snapshots of a program and recording its inputs and outputs. It may or may not work when the program interacts with its environment in complex ways, since the environment does not roll back when the program does.

### Replay debuggers

A replay debugger records one execution of the program. It then replays this same execution, simulating all inputs and outputs.

#### Replay debugging on Linux with rr

Install the Mozilla Record and Replay framework (rr) from https://rr-project.org/ or e.g. `apt install rr`.​

If needed, give yourself debugging permission:

```
# The Ubuntu default is 4 which is too paranoid.
sudo sysctl kernel.perf_event_paranoid=1.​
# Make this persistent across reboots.
echo 'kernel.perf_event_paranoid = 1' >>/etc/sysctl.d/zz-local.conf​
```

To debug a program​, build it with debugging symbols as usual (`-O0 –g3` or `–Og -g3`).​ Then run it once to save a full trace of the execution:

```
rr record tests/test_suite_ssl
```

Then `rr replay` gives you a gdb interface where reverse execution actually works.​ You can use [`reverse-xxx` commands​](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Reverse-Execution.html) such as:

* `rs` (`reverse-step`) steps into functions​.
* `rn` (`reverse-next`) steps over function calls​.
* `reverse-finish` goes back to where the current function was called​.
* `set exec-direction reverse` changes `step`, `next`, etc. to go backwards. Switch this off with `set exec-direction forward`.

If you use a frontend, configure it to run `rr replay` instead of `gdb myprogram`.​ If the frontend uses gdb's machine interface, use `rr replay -i=mi …` instead of `gdb -i=mi …`.

#### Replay debugging on macOS with warpspeed

Try [warpspeed](https://github.com/kallsyms/warpspeed).

## Open-source tools in popular long-term support distributions

Mbed TLS' minimum tool version requirements are usually set based on the versions shipped in long-term support releases of major operating systems. The table below lists versions of relevant software in distributions that are in support.

[RHEL](https://access.redhat.com/support/policy/updates/errata#Life_Cycle_Dates) 6 is on extended lifecycle support until June 2024. The list of packages is identical to [CentOS 6](http://vault.centos.org/6.10/os/Source/SPackages/), and in RHEL 7 to [CentOS 7](http://vault.centos.org/7.8.2003/os/Source/SPackages/).

Ubuntu 16.04 is on extended security maintenance (ESM) until April 2024. Debian long-time support lasts less long, so the oldest versions of software that are supported in a Debian release are slightly less old than for Ubuntu, therefore we don't need to look at Debian versions.

[pkgs.org](https://pkgs.org/) indexes the software versions in many currently-supported distributions. This includes Ubuntu LTS and CentOS, but not RHEL ELS.

| Software | [Ubuntu 16.04](https://packages.ubuntu.com/xenial/devel/) | [RHEL 6](http://vault.centos.org/6.10/os/Source/SPackages/) | [CentOS 8](https://centos.pkgs.org/8/centos-baseos-x86_64/) + [appstream](https://centos.pkgs.org/8/centos-appstream-x86_64/) | [Ubuntu 18.04](https://packages.ubuntu.com/bionic/devel/) | [RHEL 7](http://vault.centos.org/7.8.2003/os/Source/SPackages/) | [SLES 12](https://scc.suse.com/packages?name=SUSE%20Linux%20Enterprise%20Server&version=12.5&arch=x86_64) | [SLES 15](https://scc.suse.com/packages?name=SUSE%20Linux%20Enterprise%20Server&version=15&arch=x86_64) |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| End-of-life | Apr 2021 | Nov 2020 | Dec 2021 | Apr 2023 | Jun 2024 | Oct 2024 | Jul 2028 |
| Security EOL | Apr 2024 | Jun 2024 | N/A | Apr 2028 | N/C | Oct 2027 | Jul 2031 |
| Clang | 3.8 | N/A | 10.0.1 | 6.0 | N/A | N/A | 5.0.1 |
| CMake | 3.5.1 | 2.8.12.2 | ≥3.18.2 | 3.10.2 | 2.8.12.2 | 3.5.2 | 3.10.2 |
| GCC | 5.3 | 4.4.7 | 8.3 | 7.4 | 4.8.5 | 4.8.5 | 7.5.0 |
| GNU make | 4.1 | 3.81 | 4.2.1 | 4.1 | 3.82 | 4.0 | 4.2.1 |
| Python 3 | 3.5.2 | N/A | 3.6.8 | 3.6.5 | 3.6.8 | 3.4.10 (+3.6) | 3.6.5 |
| Doxygen | 1.8.11 | 1.6.1 | 1.8.14 | 1.8.13 | 1.8.5 | 1.8.6 | 1.8.14 |

# PR Prioritisation

The Mbed TLS core team prioritise PRs to help us spend our review capacity on the items that best help the project.

When PRs are first triaged, a label is applied to help reviewers determine what to work on (and what not to work on). The different classifications are described below.

Please note that if your PR falls into the lower priority categories, we are happy to increase its priority if needed. This might happen through:

- Commenting on the PR to explain why there is an important use-case for it
- Other users commenting to show wider demand for the PR
- Attending the bi-weekly Tech Forum call to discuss the PR
- Advocating for the PR on the project mailing list
- Find others to review your PR

Classifications are done through labels, e.g.: priority-high.

Please note that these are the priorities used by the core team. External contributors are welcome to review PRs according to their own priorities, and such review activity will help highlight PRs which should get attention from the core team.


### priority-high

This classification is used for PRs which are typically one of:

- Security (or other high-priority) bug-fixes
- Items that the Mbed TLS team have planned for delivery in the current quarter

These PRs should receive review promptly.


### priority-medium

This is for PRs which advance the core team's aims for Mbed TLS, but are not needed to meet delivery in the current quarter. These would typically address one of the following areas:

* Security
  * Non-urgent and lower-priority security improvements
* Robustness
  * Non-urgent bug-fixes
  * Test improvements
  * Documentation
* PSA Crypto
  * Provide a reference implementation for PSA Crypto
  * Driver interface for secure elements & crypto processors
* TLS
  * Support latest TLS versions and features - especially client features important for embedded devices
  * DTLS, QUIC
* Embedded applications
  * Improvements to code-size, memory footprint and performance on embedded devices


### priority-low

This is for PRs which are potentially useful or nice to have, but are unlikely to receive review soon. This might include PRs in the following areas:

* New ciphers for which there is low demand
* Minor performance enhancements
* Enhancements that don't suit embedded applications
* Code (especially assembly) for platforms where the team has little experience for review or maintenance, or limited ability to test
  * Note: we currently have the capability to maintain & test aarch32, aarch64, x86 and x86-64 on Ubuntu, FreeBSD and Windows

* Minor quality/test improvements, e.g. clean-up of test infrastructure or build scripts
* Items where the team might not be able to afford the maintenance cost

After at least one year, some items in this category may be closed if a clear need does not emerge with time. This is more likely to happen for larger and more complex PRs.


### priority-scheduled

This is an additional label used for larger PRs (typically priority-medium) which require significant team bandwidth to review. These items will not be reviewed immediately, but they will be scheduled in the project roadmap with time allocated for review.

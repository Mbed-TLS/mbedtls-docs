## Mbed TLS Review Guidelines

### Introduction

This document describes the process of reviewing pull requests (PRs).

### Use of GitHub

When you decide to review a PR, request your review using GitHub's request review button in order to communicate that you are actively reviewing. This helps improve communication with the rest of the community as to who is reviewing what.

The GitHub PR review facilities are used to submit Mbed TLS code reviews. Please refer to the GitHub documentation for more information regarding the review facilities.

Anyone can submit a review, and reviews from the community are very welcome. However, GitHub is set up so that only reviews from specific individuals (the trusted reviewers) will formally count towards the two positive reviews required to merge a PR.

### Review Checklist

When reviewing a PR and leaving comments, make it clear not just what you see as wrong, or in need of clarification, but also what checks you have made and the scope of any testing.

Reviewers should verify the following checklist against the PR and should make clear if they did any additional checks, such as building the code or testing the code, and if so, under what conditions.

To help you get into the right mindset for reviewing, please see [Gilles Peskine's talk: How to be an effective reviewer](<How to be an effective Mbed TLS reviewer.pdf>).

### Suitability

* Is this relevant and useful for the Mbed TLS project?
* Backports
  * Either backports should be provided, or a justification that backports are not needed.
  * No backports for new features, only for bug fixes and test cases.
* Does it fit what was needed?
  * If there's a github issue, does it match the requirements of the issue?

### Quality

* Does it pass CI?
* Documentation
  * Is the change properly documented with Doxygen?
     * Doxygen documentation for all interfaces
  * Comments in the code for tricky parts
  * Separate markdown document if applicable
  * Copyright
    * Files must contain an accurate copyright header ("Copyright The Mbed TLS Contributors")
    * Years are correct
    * License is specified correctly with SPDX
* ChangeLog entry
  * Bugs, features and functional and API changes should be in the ChangeLog
  * Trivial changes and documentation fixes such as typos or minor corrections do not need to be recorded
* Tests
  * Bug fix: are there proper non-regression tests?
  * New feature: are there proper unit tests, and other tests if applicable?
  * Does the PR include new test cases necessary to prove its correctness?
    * Are any new test cases required?
* Sample applications
  * Do sample applications need to be updated?
  * Should there be a new sample application, or an extension to an existing one?
* Code quality
  * Does the PR follow our code style rules (https://tls.mbed.org/kb/development/mbedtls-coding-standards)?
  * Is the code clean and readable?
  * Is the code portable?
  * Is the PR consistent with the principles of the library? (separate, independent object modules)
    * Coupling between modules should be controlled and minimized, as should header dependencies
* Commit quality
  * Commit messages must contain the following information
    * Title of commit
    * Detailed description of commit in commit message
    * On its own line starting with "Fixes ", a comma separated list of GitHub issues that this commit fixes. Repeat the "fixes" keyword for each issue so that GitHub can read the issues. GitHub will close the issue automatically, so if it takes multiple commits to fix an issue, just list "Fixes" on the most recent commit.
  * Example:
 ```
Add tests for rsa_deduce_moduli()

Add tests for the new library function mbedtls_rsa_deduce_moduli() for
deducing the prime factors (P,Q) of an RSA modulus N from knowledge of a
pair (D,E) of public and private exponent:

- Two toy examples that can be checked by hand, one fine and with bad parameters
- Two real world examples, one fine and one with bad parameters

Fixes #416, fixes #417
 ```
* Commit messages must NOT contain the following
  * References to issue trackers other than the public GitHub repository 
* Correctness
  * Check for:
    * Logical correctness
    * Input validation as appropriate
    * Integer/buffer overflow
    * Use of types, casting
    * ... as well as everything else.
* Security
  * Are there any potential security issues? Should they be mitigated?
  * Is the architecture sufficiently defensive?
  * Is the coding sufficiently defensive?
* Compatibility
  * Does this meet our compatibility rules?
  * Does this change the API or ABI?
    * If yes, ensure that is approved, and record it in the ChangeLog
    * All internal functions should be file scope (static)
* Portability
  * Does the change make use of any platform or external library calls (client code, network, file, etc.)?
    * All additional platform/third party calls should be considered for portability and IP
    * Avoid adding interfaces to external code as much as is reasonably possible
* Standards
  * If the PR implements a standard or RFC, has the code been cross referenced against the standard as part of the review?
    * This is an essential step for implementing RFCs or crypto standards.

### Goal

* Does the PR resolve the issue that it's supposed to resolve?

* Are there any other similar cases that need to be reviewed and resolved?

* Does the PR introduce new risk (incompatibility with some existing feature)?

* Is there any follow-on work that needs to be tracked as a Github issue?

### Specific areas of the code

#### Alternative implementations

If the changes concern alternative implementations:
* Is the baseline behavior preserved when the XXX_ALT macro isn't defined?
* Are all required key sizes and other variants provided by the alternative implementation?
* Does the behavior seem sensible, given public knowledge of the accelerator and its HAL?
   * E.g. sha256_update(ctx1); sha256_update(ctx2): check that there's no leak between the two contexts.


### Restricted PRs

For PRs in mbedtls-restricted, to minimise conflicts when merging with the non-restricted branch, these must be as minimal as possible. Reviewers should check for parts of the PR that could be split out and raised as a separate PR on the main repository.

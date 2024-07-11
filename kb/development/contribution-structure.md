# What should go into a contribution?

This document describes how to structure a contribution to Mbed TLS: [where](#repositories-and-branches), [what](#contents-of-a-contribution) and [what structure](#structure-of-a-contribution).

For the process of submitting a contribution, please see the [review process guide for contributors](../../reviews/review-for-contributors.md).

For guidance on the content of contributions, please see the [base contributing guidance](https://github.com/Mbed-TLS/mbedtls/blob/development/CONTRIBUTING.md)

## Repositories and branches

The Mbed TLS project maintains several repositories:

* [`TF-PSA-Crypto`](https://github.com/Mbed-TLS/TF-PSA-Crypto): an upcoming repository for the cryptography library, due for a 1.0 release in 2025. Until the repository is live, all contributions need to go through the `mbedtls` repository.
* [`mbedtls`](https://github.com/Mbed-TLS/mbedtls): the cryptography, X.509 and TLS library. From version 4.0 onwards, due in 2025, the cryptography library will be hosted in the TF-PSA-Crypto repository. Contributions are welcome:
    * On the `development` branch (this is the default), for anything that should go into the next release.
    * On [long-time support branches](https://github.com/Mbed-TLS/mbedtls/blob/development/BRANCHES.md#long-time-support-branches), for bug fixes to those branches.
* [`mbedtls-framework`](https://github.com/Mbed-TLS/mbedtls-framework): version-independent files such as build and test scripts, and test data. This is consumed by the library's build and test scripts in Mbed TLS 3.6.0 and later versions.
* [`mbedtls-test`](https://github.com/Mbed-TLS/mbedtls-test): version-independent scripts for continuous integration. We do not expect external contributions to this repository.
* [`mbedtls-docs`](https://github.com/Mbed-TLS/mbedtls-docs): version-independent documentation, with a lightweight review process. The repository also contains a few tools that may be useful to Mbed TLS contributors. Contributions are welcome, even small incremental improvements.

## Contents of a contribution

This section discusses the expected contents of a contribution to the library repositories. We have relatively high standards, both to ensure a high-quality product and to facilitate review. Nonetheless the guidelines should not be surprising.

This section does not cover contributions to `mbedtls-docs`, which are much more relaxed.

### Documentation

All interfaces should be documented. We use [Doxygen](http://www.doxygen.nl/) comments for C library interfaces (functions, macros, types, etc.).

When documenting a function, please explain the purpose of the function, the role of each argument and the possible return values. Be sure to document any constraints on the arguments. If the function is meant to be used in combination with other functions (e.g. a setup-update-finish sequence), please cross-link the relevant functions.

Test code is more relaxed, but we still expect documentation for test helper functions and for nontrivial functions in test scripts.

When you add test data, please explain how it was produced, either in a comment or in the commit message. If you used an automatic method, please share the automation scripts so that reviewers can reproduce it and confirm that the generated test data was submitted correctly. Some test data is generated from scripts: see [`generate_xxx_tests.py` scripts](https://github.com/Mbed-TLS/mbedtls-framework/tree/main/scripts) and [test data files](https://github.com/Mbed-TLS/mbedtls-framework/blob/main/data_files/Makefile). If the data is randomized, please explain how we can validate that it is correct.

### Tests

#### Tests for new features

All new features should be tested.

See the [test guidelines](../development/test_suites.md) and a [test overview](../generic/what-tests-and-checks-are-run-for-polarssl.md).

#### Non-regression tests

When fixing a bug, please include non-regression tests if at all possible. A non-regression test is a test that fails before applying the bug fix, and passes after the fix is applied.

Here are a few cases where we don't expect a non-regression test:

* We don't have the capacity to test on many platforms, so we don't expect tests for issues that are specific to a particular CPU or operating system. If you're submitting a fix for a bug on a platform that we don't have, please test locally.
* Mbed TLS is very configurable. We test a lot of different configurations, but we often won't add testing for build failures that only happen in relatively rare configurations.
* There are certain errors that we cannot trigger on purpose at the moment: hardware accelerator errors, and memory allocation failures. It is generally acceptable to omit a non-regression test when fixing a bug in the recovery from such an error.

#### Running tests locally

For basic unit tests, you can just compile the project and run `make test`. Note that this only tests the default configuration. The entry point to testing with many different configurations is [`tests/scripts/all.sh`](https://github.com/Mbed-TLS/mbedtls/blob/development/tests/scripts/all.sh).

To run some tests, in particular TLS testing, you will need additional tooling. See the [Testing and CI guide](../testing/testing-ci.md) for more information.

Note that you do not need to run all the tests locally. You should run the tests that are most relevant to your contribution, for example:

* At least `make test` in the default configuration for a C code change.
* (A relevant subset of) `tests/ssl-opt.sh` for changes that affect the TLS protocol.
* Also test in other configurations if your changes are configuration-dependent.
* `scripts/code_style.py --since development` for a C code change.
* `tests/scripts/check-python-files.sh` for a Python code change.

Once there are no obvious failures, it's ok to open a pull request and wait for the results on the CI (continuous integration) servers. The CI runs build and test campaign in over a hundred different configurations, and on a few different platforms.

### Changelog entries

When adding a new feature or fixing a bug, please add a [changelog entry file](https://github.com/Mbed-TLS/mbedtls/blob/development/ChangeLog.d/00README.md).

## Structure of a contribution

Mbed TLS uses the Git version control system. Contributions take the form of a Git branch that contains one or more commits.

### Creating a branch

1. Fork the repository on GitHub.
2. Create a branch in your local repository from the branch you want to target (e.g. `development`). Give that branch a descriptive name (e.g. `fix-widget-empty-vertex-bug`).
3. Work, [commit](#commit-structure), repeat until done.
4. When you're ready, push the local branch to your fork and open a pull request in the target repository. It's ok if the target branch has changed since you created your branch, as long as there are no conflicts.

### Commit structure

The Mbed TLS project attaches significant importance to a good commit structure. If a contribution has commits that are too complex, we may require you to break it down into smaller commits.

A good commit structure has two advantages:

* It makes review easier. We often review commit by commit. It is easier to review multiple commits that each have a clear, documented purpose, than to review a single commit that does many things.
* If we are later puzzled by a piece of code, we can look at the commit structure and gain insight as to why the code is what it is. (We never squash commits.)

As a central rule, **a commit should only do one thing**. What counts as “one thing” is of course subjective, so here are some examples.

* Do not combine refactoring with new features in the same commit. For example, suppose a function `foo()` does A then B, and you want to have a separate function that does the B part with more flexibility. This should be at least two commits: one to split `foo()` into `A()` and `B()` in a commit that does not change the behavior, and one to expand the functionality of `B()`.
* In particular, do not move and change code at the same time. For example, suppose you want to move a `static` function to another module and make it public with a different name. Make one commit to rename the function, and another commit to move the code without changing it.
* If you discover a bug while working on a new feature, make separate commits for the bug fix and for the feature.

“One thing” can be a group of closely-related things. For example:

* If a bug fix is simple and constructing a test is also simple, it's ok to have a single commit that has both the fix and the test. On the other hand, if constructing the test requires refactoring some existing test functions, that should be done in a separate commit beforehand.
* It's ok to have a single commit that fixes multiple minor issues in different places if those issues have a common trigger, for example fixing multiple warnings that come from the same compiler or linker.

Before committing, look at the output of `git diff`. Is it easy to follow what's going on? If not, this should be multiple commits.

### Commit correctness

We do not have formal rules for commit correctness. All commits should at least build in the default configuration on “mainstream” platforms, but this is not enforced. It's ok to have a commit that doesn't build in “exotic” configurations or environments, and a later commit that fixes those builds.

When fixing a bug, you may include a non-regression test in a preceding commit, in the same commit or in a subsequent commit. Each method has its upsides and downsides, and we do not impose any particular order.

Please do not submit commits with missing files or with spurious files. If you forget to add a new file before committing, please amend the corresponding commit. If you accidentally commit a local file, please amend the corresponding commit to not include that file.

### Commit messages

Commit messages should contain a high-level description of what has changed and discuss any implications. For example, when fixing a bug, explain the symptoms of the bug and link to the GitHub issue if there is one. When refactoring, explain the purpose of the refactoring. It should always be clear from the commit message whether the commit is a refactoring that doesn't change the behavior, or a behavior change. ([It shouldn't be both](#commit-structure).)

Commit messages must follow the Git convention of having a line with a short description, then a blank line, then a more detailed description. We recommend [Chris Beams's “How to Write a Git Commit Messages”](https://cbea.ms/git-commit/), except we're ok with 72 characters in the subject line, or even more if it really can't be shortened.

In order for commit messages to be searchable, please make sure that they include all the words that people are likely to search for. Avoid abbreviations and misspellings.

When a commit contains test data, either the content of the commit or the commit message should make it clear how the test data was generated and how to validate it.

When committing, please re-read your commit messages. Does it convey the purpose of the commit to someone who hasn't read the code?

Before pushing, look at `git log --oneline origin/development..HEAD`. Does it give a good idea of what each change is doing?

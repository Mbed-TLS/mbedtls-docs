# Splitting `depends.py` between TF-PSA-Crypto and Mbed TLS

## Introduction

The goal of this document is to design and plan the adaptation of the testing done by `depends.py` to the split between TF-PSA-Crypto and Mbed TLS.

## Project overview

### Role of `depends.py`

The script `tests/scripts/depends.py` is used to test the library in a number of different configurations defined by sets of cryptographic mechanisms (or adjacent features, specifically TLS key exchange types). Its goal is to give confidence that the library behaves correctly when only a subset of cryptographic mechanisms is enabled.

The name “depends” comes from the fact that one of the main things that is validated is that library code has correct `#if defined(...)` guards, and tests have correct `depends_on:` guards. However, the testing addresses other risks, such as buffer sizes that depend on the mechanism, and proper handling of requests to use mechanisms that are disabled.

The parts of the library and tests that it is the most relevant to test are:

* Cryptographic mechanisms, to ensure that e.g. any auxiliary function is enabled when it should, and that static buffer sizes are large enough for all enabled mechanisms.
* Parts of the library that use cryptography in a way that isn't fully generic. This includes many parts of X.509 and TLS because those relate user data with a choice of mechanism.

Note in particular that TF-PSA-Crypto defines how to enumerate interesting configurations, but it is very relevant to test Mbed TLS in these configurations.

### Current state

As of TF-PSA-Crypto 1.1.0 and Mbed TLS 4.1.0, `depends.py` is only present in Mbed TLS, and there is no equivalent in TF-PSA-Crypto. As a consequence, many interesting configurations are untested in TF-PSA-Crypto. Of the test cases that TF-PSA-Crypto 1.1.0 does not run in its `all.sh` ([#740](https://github.com/Mbed-TLS/TF-PSA-Crypto/issues/740)), many are from `test_suite_config` with a certain cryptographic mechanism disabled.

### Excluding 3.6

`depends.py` was the result of unifying several Perl scripts with similar objectives. It was originally written in 2019 and first released in 2022 in Mbed TLS 3.3.0. Since then, the changes we have made to it in Mbed TLS 3.x are:

* Tweak the dependency lists to accommodate new features (e.g. TLS 1.3, new PK options for optional features, Arm crypto acceleration options, SHA3).
* Use `config.py` as a Python module instead of via the command line.
* Minor generic tweaks, e.g. copyright line, compilation flags...

In Mbed TLS 4, we have made additional changes:

* Change from legacy config options to PSA config options, using existing modules to enumarate available PSA mechanisms where relevant.
* Remove features removed in TF-PSA-Crypto 1.0 or Mbed TLS 4.0.
* Adapt the build commands to the changes in Mbed TLS 4.

This indicates that `depends.py` is a mature script: its overall scope has not changed in 7 years, and the bulk of the changes have been related to changes in the configuration options to enumerate or toggle. We have no plans to change anything about `depends.py` in the 3.6 long-time support branch.

Additionally, the changes between 3.6 and 4.0 are not purely data: there is code that enumerates certain cryptographic mechanisms present in the library (e.g. determine the list of hash algorithms by looking for macro definitions in certain headers), and that code is different in 3.6 and 1.0/4.0, but likely to remain stable after 1.0/4.0. Thus only a subset of the code can be shared between 3.6 and 1.1/4.1, but we do not foresee much (if any) new code needed after 1.1/4.1.

As a consequence, Mbed TLS 3.6 is excluded from this project. We will not make the 3.6 branch use any of the code that we are moving to the framework.

### Project objectives

At a high level, we want to extent the test coverage that Mbed TLS achieves with `depends.py` to TF-PSA-Crypto. We do not want to lose the coverage in Mbed TLS itself. Since we are ([excluding 3.6](#excluding-3-6)), the scope of this project is the 1.1/4.1 and development branches of TF-PSA-Crypto/Mbed TLS. Therefore this project's objectives are, in order of importance:

1. Give TF-PSA-Crypto the same kind of coverage that Mbed TLS currently gets through `depends.py` (without losing coverage in Mbed TLS).
2. Have each branch be responsible for its own knowledge. In particular, adding a crypto feature should not require any change in Mbed TLS until Mbed TLS starts using it.
3. Share as much code as possible to minimize the need for synchronization and backports.

## Technical analysis

### `all.sh` components

The entry points for testing based on `depends.py` are `all.sh` components in `tests/scripts/components-configuration-crypto.sh`. Each component has a single shell command (besides `msg`), to run `depends.py` on one domain to test.

The same domains are relevant for TF-PSA-Crypto and Mbed TLS, except that the `kex` domain (key exchanges) is only applicable to Mbed TLS. Therefore we will copy the `all.sh` components to TF-PSA-Crypto, except for the `kex` one.

### Overview of `depends.py`

`depends.py` has the following parts (which are not fully distinguished in the source code):

* General logic to parse the command line, print logs, configure the library, build and run tests, report outcomes, etc.
* A consistency check method `Job._consistency_check`, which references the project's `build_info.h` header, and needs to enumerate the project's public headers.
* Data and logic to enumerate the individual elements of each domain (enumerate hash algorithms in the `hashes` domain, etc.). This logic is entirely based on knowledge of TF-PSA-Crypto, except for the `kex` domain which is about TLS key exchanges and is entirely the responsibility of Mbed TLS.
* Reverse dependencies: a mapping from elements of a domain (config options corresponding to a cryptographic mechanism), to a list of config options that require that element. That is, when `x` is disabled, all the elements of `REVERSE_DEPENDENCIES[x]` must also be disabled. The keys in this mapping are domain elements and therefore crypto options (except in the `kex` domain, which does not have any reverse dependencies). Most of the values in this mapping are crypto options, but there are a few X.509 and TLS options as well.
* `EXCLUSIVE_GROUPS` is similar to `REVERSE_DEPENDENCIES` in that it defines configuration tweaks, with keys that are crypto options and values that are crypto or TLS options.
* Code to construct domains, based on a combination of source code parsing and ad hoc data.

### What goes where?

* Knowledge of the `kex` (key exchange domain), and of X.509/TLS options to associate with individual cryptographic mechanisms, must go in Mbed TLS. This knowledge may evolve in the `development` branch, and is likely to never change in an TLS branch.
* Knowledge of crypto domains and of crypto options to associate with individual cryptographic mechanisms, must go into TF-PSA-Crypto. This knowledge may evolve in the `development` branch, and is likely to never change in an TLS branch. Note that this knowledge is consumed by both TF-PSA-Crypto and Mbed TLS.
* Knowledge of how to build the library can go in each project, but can also go into the framework as long as we fully switch to CMake (the script currently uses `legacy.make`).
* Generic code should go into the framework.

This leads us to the following file architecture:

* Framework: `scripts/mbedtls_framework/depends_engine.py`: general logic, including logic that enumerates cryptographic mechanisms and key exchanges by parsing source code.
* TF-PSA-Crypto: `scripts/project_knowledge/tf_psa_crypto_depends_info.py`: data about this branch of TF-PSA-Crypto, which is consumed both by TF-PSA-Crypto and by the consuming branch of Mbed TLS.
  Note that this is similar to `tests/scripts/tf_psa_crypto_test_case_info.py`: it's mostly data (but not necessarily pure data: it can run some functions) which is defined by TF-PSA-Crypto but consumed by Mbed TLS.
* TF-PSA-Crypto: `tests/scripts/depends.py`: TF-PSA-Crypto entry point, and project-specific data that is not consumed by Mbed TLS.
* Mbed TLS: `tests/scripts/depends.py`: Mbed TLS entry point and project-specific data, including the X.509/TLS part of reverse dependencies and exclusive groups.

## Actions

### Export TF-PSA-Crypto knowledge to Mbed TLS

Create a directory where TF-PSA-Crypto can put Python code that can be used by both TF-PSA-Crypto and Mbed TLS. This directory is intended for _project knowledge_, i.e. data that describes TF-PSA-Crypto in a form that Mbed TLS can consume.

We do not put `tf-psa-crypto/scripts` or `tf-psa-crypto/tests/scripts` on the Python import path in Mbed TLS because file names in these directories are likely to clash with file names in the corresponding directories of Mbed TLS, and this could cause confusion as to which module gets loaded.

To avoid any confusion between Mbed TLS knowledge modules and TF-PSA-Crypto knowledge modules when they're accessed from Mbed TLS, modules in the TF-PSA-Crypto project knowledge directory should have a name that start with `tf_psa_crypto_`.

In TF-PSA-Crypto:

* Create a directory `scripts/project_knowledge` containing `__init__.py` with just a comment explaining the directory's purpose.
* Move `tests/scripts/tf_psa_crypto_test_case_info.py` to `scripts/project_knowledge/tf_psa_crypto_test_case_info.py`.
* Re-create `tests/scripts/tf_psa_crypto_test_case_info.py` containing a temporary stub that re-exports `project_knowledge.tf_psa_crypto_test_case_info.INTERNAL_TEST_CASES`.

In Mbed TLS:

* Add `tf-psa-crypto/scripts/project_knowledge` to the various places with a Python search path (`.mypy.ini`, `.pylintrc`, `scripts/framework_scripts_path.py`, `tests/scripts/scripts_path.py`).

Note: we will wait a few weeks between the creation of `scripts/project_knowledge/tf_psa_crypto_test_case_info.py` and starting to use it in Mbed TLS, for the sake of existing TF-PSA-Crypto branches under development (they still need to pass the CI with Mbed TLS's `development` branch).

Identical backports in 1.1/4.1.

Prerequisites: none.

### Switch to CMake

In Mbed TLS `development`, change `tests/scripts/depends.py` so that it always uses CMake, never `legacy.make`.

Remove command line options that are no longer needed (we no longer need this flexibility): `--config`, `--crypto-config`, `--directory`, `--make-command`.

Do each build in a subdirectory of the source tree.

Use a custom config file in the build tree. Don't modify the source tree config file.

TODO: what about `Job._consistency_check`?

No backport.

Prerequisites: none, but likely conflicts with [Refactor in place](#refactor-in-place).

### Refactor in place

In Mbed TLS `development`, refactor `tests/scripts/depends.py` to prepare it for the repository split. In this task, we break the script into pieces, but keep all the pieces in the same directory. This is a refactoring task involving some changes to the code structure as well as moving code around.

The main goal of this task is to isolate the bulk of the logic from the data, so that the same logic can be used with different branches (1.1/4.1, `development`) and different projects (TF-PSA-Crypto, Mbed TLS).

Additionally, some code will need to be customized for each project, e.g. code that contains build commands or that puts all the data together. Such code must be in customizable members or methods of a class that each project can override.

* In `turn_off_dependencies`, use an extra parameter instead of referencing the constant `REVERSE_DEPENDENCIES`. In `ExclusiveDomain.__init__` and  `ComplementaryDomain.__init__`, take an extra parameter and pass it down.
* In `handle_exclusive_groups`, use an extra parameter instead of referencing the constant `EXCLUSIVE_GROUPS`. In `ExclusiveDomain.__init__`, take an extra parameter and pass it down.
* Make `REVERSE_DEPENDENCIES` and `EXCLUSIVE_GROUPS` members of the class `DomainData`, defaulting empty.
* Split the definitions of `REVERSE_DEPENDENCIES` and `EXCLUSIVE_GROUPS` into two parts: the purely crypto part (which will go into TF-PSA-Crypto) and the X.509/TLS part (which will stay in Mbed TLS).
* Derive a class `MbedTLSDomainData` from `DomainData`, which sets `REVERSE_DEPENDENCIES` and `EXCLUSIVE_GROUPS` to the desired values obtained by combining the TF-PSA-Crypto and Mbed TLS data.
* Derive a class `TFPSACryptoDomainData` from `DomainData`, which sets `REVERSE_DEPENDENCIES` and `EXCLUSIVE_GROUPS` to just the TF-PSA-Crypto data.
* Move the construction of the `kex` domain to the `MbedTLSDomainData` constructor.
* Pass a `DomainData` derived class (not object), and `conf`, as parameter to `main`. In the `name == '__main__'` block, pass the Mbed TLS parameters.

Manual validation: run `python -c main(TFPSACryptoDomainData, config.TFPSACryptoConfig())` in TF-PSA-Crypto and check that it works as intended.

No backport.

Prerequisites: none, but likely conflicts with [Switch to CMake](#switch-to-cmake).

### Split across repositories

* Use [`mbedtls-move-to-framework`](https://github.com/Mbed-TLS/mbedtls-docs/pull/145) to copy the history of `depends.py` from Mbed TLS to the framework. Move the file to `scripts/mbedtls_framework/depends_engine.py`.
* In the framework, remove the project-specific parts of `depends_engine.py` and the call to `main()`. Make it non-executable.
* In TF-PSA-Crypto, create `scripts/project_knowledge/tf_psa_crypto_depends_info.py` which contains the crypto-specific data from `depends.py`.
* In TF-PSA-Crypto, create `depends.py` which imports `mbedtls_framework.depends_engine`, imports the crypto-specific data from `project_knowledge.tf_psa_crypto_depends_info`, and contains the derived class and `main` call for crypto.
* In TF-PSA-Crypto, add `all.sh` jobs that call `depends.py`. (Same as Mbed TLS except for `kex`.)

In Mbed TLS, prepare a revised `depends.py` that just:

* Imports `mbedtls_framework.depends_engine`.
* Imports `tf_psa_crypto_depends_info.py`.
* Contains the Mbed TLS-specific knowledge.
* Contains the Mbed TLS derived classes.

Validate this on the CI, but wait a few weeks to merge it, so that Mbed TLS keeps working with slightly older TF-PSA-Crypto branches.

Prerequisites: [Export TF-PSA-Crypto knowledge to Mbed TLS](#export-tf-psa-crypto-knowledge-to-mbed-tls), [Switch to CMake](#switch-to-cmake), [Refactor in place](#refactor-in-place).

### Cleanup

* In TF-PSA-Crypto, remove the temporary redirection `tests/scripts/tf_psa_crypto_test_case_info.py`.
* In Mbed TLS, in `tests/scripts/analyze_outcomes.py`, import `tf_psa_crypto_test_case_info.py` and remove the hacks to load the old script dynamically.

Prerequisites: all of the above, and wait a little so that Mbed TLS keeps working with slightly older TF-PSA-Crypto branches.

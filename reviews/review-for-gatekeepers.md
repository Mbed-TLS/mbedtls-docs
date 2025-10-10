# Gatekeeper Responsibilities

Gatekeepers are the [gatekeepers team on GitHub](https://github.com/orgs/Mbed-TLS/teams/gatekeepers).

## TL;DR

A pull request is ready for merge if the following three conditions are true:

- The merge button is green.
- Nothing looks out of place.
- The backports are also ready for merge.

## Merging Process Overview

All updates to a maintained branch should be done by merging a pull request.
Manually merging and pushing is forbidden: if a manual merge is necessary, do it through a pull
request. Exceptions should be reserved for emergency and should be discussed with the team as soon
as practical.

The gatekeeping process is therefore:

1. Check that the pull request is ready for merge.
    - [Sanity checks](#sanity-checks)
    - [IP status](#ip-status)
    - [Review status](#review-status)
    - [CI status](#ci-status)
    - [PR checklist](#pr-checklist)
2. Click the "Merge" button on GitHub.
    - GitHub may style the “Merge” button in green, gray or red depending on the state of the pull
request. This is only an approximation of the mergeability rules. A pull request can be ready for
merge even with a red button and might not be ready even if the button is green.
3. [Update issues](#updating-issues) if needed.

## Sanity Checks

- Is the objective of the pull request something we actually want?
- Does the pull request look like it's doing what it purports to do?
    - This is not the time for an in-depth review, just a superficial check.
- Does the pull request touch all the areas that you'd expect based on the objective? (documentation,
tests, sample programs, build scripts, …)
    - Watch out for missing documentation updates.
- Platform support (OS, compiler, etc.): is there a risk of introducing incompatibilities?
    - Beware of PRs that add support for a newer platform, but break older platforms.
    - Long-time support branches are subject to especially strict scrutiny.

## IP Status

**TL;DR:** don't bypass DCO.

All contributions made since 2020-02-18 should include a "Signed-off-by" line in every commit
message, asserting that the submitter has the right to contribute under the project's licensing
rules ([Developer Certificate of
Origin](https://github.com/Mbed-TLS/mbedtls/blob/development/dco.txt)).

If the [DCO check](https://github.com/apps/dco) passes, we are allowed to accept the contribution. If the DCO check fails, we are
not allowed to accept the contribution unless it falls under one of the exceptions for pre-2020
contributions.

### Pre-2020 contributions

- Commits by an Arm employee are always acceptable. Pull requests by an Arm employee made before
  this date would have had the label Mbed TLS team or Arm Contribution.
- Commits made by people who were not Arm employees are acceptable if the contributor (or their
  employer) had signed a contributor license agreement (CLA)

A contribution where a commit lacks a DCO is only acceptable if it is from Arm or covered by a CLA.
If in doubt, consult a gatekeeper who was there before 2020.

## Review Status

Necessary conditions before merging:

- Check that the review threshold indicated by GitHub is met ("Changes approved" — "2 approving
reviews by reviewers with write access").
    - The approval must be on the latest version. This is enforced by GitHub (updating the pull request
dismisses approvals).

### Notes in Rare Cases

- Split review: occasionally the reviewers may approve with reservations, for example stating that
they took over from someone else during rework. In such cases, the gatekeeper should ensure that the
whole content of the pull request has had two approvals.
- Commits by a reviewer: if the pull request includes commits by one of the reviewers, two reviewers
who are not the committer must review them.

### Review status on mbedtls-docs

As an exception, one approving review by a reviewer with write access is enough.

## CI Status

Necessary conditions before merging:

- Check that all the required CI statuses are green (passed).
    - If some tests are inconclusive due infrastructure problems or random failures (e.g. timeouts),
    run the CI again.
        - Known infrastructure problems are tracked in the [mbedtls-test](https://github.com/Mbed-TLS/mbedtls-test.git) repository.
        - Known random failures are tracked in the library repositories (search for the keyword
          "intermittent")
        - If the issue at hand is a new one (no corresponding issue yet) raise an issue for
          tracking. Make sure to use the word "intermittent" in the description.
- Check that the "Interface stability" test status is green (passed).

### CI Status Bypass

Exceptions to the necessary conditions above:
- If a job passed on Jenkins but didn't post its status to GitHub due to a network glitch, it's OK to
merge.
- If the sole failure is the "Interface stability" test, but this is a false positive, it's OK to merge. False
positives include:
    - ABI (not API) changes are acceptable on development. The corresponding SO version will need to be
    updated before the next release.
    - Changes in parts of the API that are documented as private are acceptable. Typical case: changes of
    fields in structures that are documented as opaque, but are exposed to the C compiler to let it know
    the structure size and optimize getter/setter functions.

### CI status on mbedtls-test

As an exception, mbedtls-test does not have automatic CI runs. Instead, we run a manual selection of
CI jobs based on the impact of the changes. The PR description, or subsequent comments, should list what
testing has been done.

## PR Checklist

PRs to the main repositories have a checklist at the end of the template. The purpose of which is to
support the gatekeeping process. In particular to supply useful information for checking:

- Changelog
- Backports
- Dependencies
- tests

### Changelog Status

Is a [changelog entry](https://github.com/Mbed-TLS/mbedtls/blob/development/ChangeLog.d/00README.md#user-content-what-requires-a-changelog-entry) needed? If so, is it present? If not, is the justification listed in the PR checklist? Is it acceptable?

### Backport status

See [When to
backport?](https://github.com/Mbed-TLS/mbedtls/blob/development/CONTRIBUTING.md#long-term-support-branches)

Unless there's some particular urgency, we merge fixes to all applicable branches at the same time.

**Pull request to development:**

- If backports are present, are they ready for merge? Are they linked in the checklist?
- If there is no backport, is the justification listed in the checklist? Is it acceptable?
- If a backport is missing, or is present but not yet approved, make sure the PR is labeled "needs-backports".

**Pull request to an LTS branch:**

- Is it a backport? Is the main PR linked in the checklist?
    - Edit the PR description if necessary.
    - The title of a backport PR should be something like “Backport 3.6: Fix frobnication of spherical
keys”.
- If the PR is only for the LTS, is the justification listed in the checklist? Is it acceptable?
(e.g. a bug that isn't present in development). Check check the backport link or justification for
the other LTS branches (if any).

Note that `mbedtls-3.6` is an LTS released before the repo split and changes from TF-PSA-Crypto
might need to be backported to it.

### Dependency Status

- PRs often have prerequisites that need to be merged in submodules or parent repositories. Are these
PRs linked in the PR checklist? Have all of them been merged?
- Are there any other prerequisites mentioned in the PR description? Have they been all merged?

### Test Status

- Have tests been provided? Is this captured in the checklist?
- If there are no tests, is a justification provided in the checklist? Is it acceptable?

Watch out for new features without tests, or bug fixes without a non-regression test, or new configuration
options whose interactions with others should be tested.

## Updating issues

### PR for development

GitHub will automatically close an issue when merging:

- a pull request containing a [closing
  keyword](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword) such as “Fix #1234”;
- or a commit whose message contains a closing keyword.

This only applies when merging to development. Sometimes the PR description doesn't contain the
issue number in a format that's automatically detected; in such cases, close it manually.

**Multiple PRs**: Often we have multiple PRs for a single issue, which we still link to the issue (which we do for readability: facilitates locating the PRs from the issue). If the PR is not the last one belonging to the given issue, we need to re-open the issue after merging the PR as it is not completed yet.

### PR for LTS only

If an issue concerns an LTS branch only and not development, GitHub won't close it even if there's a
closing keyword. So for LTS-only pull requests, check if there's an issue to close.

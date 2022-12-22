# Switching to the new code style

In January 2023, Mbed TLS switched to a new coding style, which is now enforced by continuous integration tests. This document explains how to adapt ongoing work. Please read this document if you started work on a branch of Mbed TLS that has the old coding style, and you want to contribute this work to Mbed TLS or you are already doing so.

This concerns both maintained branches of Mbed TLS: `development` and `mbedtls-2.28`.

## Coding style overview

The following table summarizes the old and new coding style (before/after January 2023).

| Aspect | Old | New |
| ------ | --- | --- |
| Indentation | 4 spaces | 4 spaces |
| Indentation of `case` | one level deeper than `switch` | one level deeper than `switch` |
| Maximum line length | 80 preferred | 80 preferred |
| **Spacing inside parentheses** | always except `define` and casts: `if( f( x ) )` | **never**: `if (f(x))` |
| Spacing inside square brackets | no: `a[i]` | no: `a[i]` |
| **Spacing before opening parenthesis** | no: `if( f( x ) )` | **after keyword or binary operator**: `if (f(x))` |
| Spacing before opening square bracket | no: `a[i]` | no: `a[i]` |
| Spacing after unary prefix operator | optional: `!c` or `! c` | **no**: `!c` |
| Spacing around binary operator | yes: `( x + y ) * z` | yes: `(x + y) * z` |
| Parentheses around return value | mandatory: `return( x );` | **generally not**: `return x;` |
| **Single-line if/loop body** | separate line, braces optional | separate line, **braces mandatory** |
| Opening brace | on its own line | **on the same line** except for functions |

For a more detailed description of the coding style, please refer to the [coding standards](../development/mbedtls-coding-standards.md).

## Migrating existing work: the theory

If you started working on a branch of Mbed TLS with the old code style, any part of the code that has been both modified in your branch and restyled in the main branch will lead to a merge conflict. To avoid that, you must migrate your work to the new style.

It is not enough to rewrite the final state of your work to the new format, because that will still be a merge conflict (between just restyling, and semantically meaningful work followed by restyling). You must rebase-and-restyle your branch. This document explains how and when.

The Mbed TLS project provides a script [`scripts/code_style_rewrite_branch.py`](https://github.com/Mbed-TLS/mbedtls/blob/development/scripts/code_style_rewrite_branch.py) which takes a Git branch with work done in the old code style, and migrates it to the new code style. Suppose your work is in a branch `mywork`, and it's intended to be submitted to some target branch (such as `development`). The migration works in two phases:

1. First identify the new commits, and attach them to the commit preceding the code style switch. This is an ordinary Git rebase (`git rebase code-style-switch-commit~ mywork`).
2. Iterate over the commits from the `mywork` branch after it forks from the target branch. For each commit, construct a new commit whose content is the restyled content of the old commit, and form a chain starting at the code style switch commit.

Using diagrams in the same form as the Git manual, the original situation is:

```
      A---B---C mywork
     /
D---E---F---G---H target
            ^
            |
            "Switch to the new code style"
```

The first phase attaches `mywork` just before the code style switch commit G:

```
          A'---B'---C' mywork
         /
D---E---F---G---H target
            ^
            |
            "Switch to the new code style"
```

In the second phase, the migration successively constructs a new branch with restyled commits. First the migration restyles the content of A' to obtain A'':

```
            A'---B'---C' mywork
           /
          /   A'' new/mywork
         /   /
D---E---F---G---H target
            ^
            |
            "Switch to the new code style"
```

The process continues with B' and so on:

```
            A'---B'---C' mywork
           /
          /   A''---B'' new/mywork
         /   /
D---E---F---G---H target
            ^
            |
            "Switch to the new code style"
```

Once the migration reaches the end of the branch, it renames the new branch to the original name:

```
            A'---B'---C' old/mywork
           /
          /   A''---B''---C'' mywork
         /   /
D---E---F---G---H target
            ^
            |
            "Switch to the new code style"
```

The branch `mywork` can now be pushed to a pull request.

## When to migrate

If you have not yet made a pull request, you can migrate your work at any time.

If you have opened a pull request but review has not yet started on it, please migrate your branch to the new code style before review starts.

If there is an ongoing review of a pull request, please communicate with the reviewer(s) to decide on a good time. Rebasing a branch during review is disruptive, because comments end up detached from the code they're about, so it's generally best not to do it. Typically the best time to migrate the branch is after the reviewer(s) have approved.

## How to migrate

### Requirements

Please have the following tools and files available:

* Git 2.17.0 or newer.
* Uncrustify 0.75.1. Please note that older or newer versions are likely not to give the desired result.
* Python 3.6 or newer.
* A Git worktree containing the branch of Mbed TLS you want to migrate.
* A local copy of [`scripts/code_style_rewrite_branch.py`](https://github.com/Mbed-TLS/mbedtls/blob/development/scripts/code_style_rewrite_branch.py) (preferably the most recent version from `development`, since it may have received bug fixes).

### Simple migration

Prerequisites:

* You have the tools and files listed under [“Requirements”](#requirements) above.
* You have a Git branch `mywork` which branched from `development` before the code style switch. (For work on Mbed TLS 2.28, replace `development` by `mbedtls-2.28` throughout these instructions.)
* The current directory is a Git working directory with `mywork` checked out, and with a remote called `upstream` pointing to [the official Mbed TLS repository](https://github.com/Mbed-TLS/mbedtls).

Run the following command in a terminal, from the Git working directory with `mywork` checked out:

```sh
python3 /path/to/code_style_rewrite_branch.py mywork upstream/development
```

If all goes well, you have successfully migrated `mywork`. You can force-push it to your work of Mbed TLS (`git push --force-with-lease origin mywork`).

A backup of the old branch is available under the name `old-code-style/mywork`.

If all did not go well, please read the error messages.

### Trial migration

The following procedure does not modify any existing Git working directory and does not rewrite any existing branch name. It explains how to migrate a branch `mywork` which branched from `development` before the code style switch. (For work on Mbed TLS 2.28, replace `development` by `mbedtls-2.28` throughout these instructions.). The result of the migration will be placed into a branch called `new-code-style/mywork` (it must not exist yet).

Run the following commands from any Git working directory with a remote called `upstream` pointing to [the official Mbed TLS repository](https://github.com/Mbed-TLS/mbedtls).

```
git branch --detach new-code-style/mywork mywork
python3 /path/to/code_style_rewrite_branch.py new-code-style/mywork upstream/development
```

If all goes well, the branch `new-code-style/mywork` contains the migrated content of `mywork`.

If all did not go well, please read the error messages.

## Known limitations

TODO

## Troubleshooting

TODO

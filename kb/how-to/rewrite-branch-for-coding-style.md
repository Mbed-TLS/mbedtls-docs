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

## When to migrate

If you have not yet made a pull request, you can migrate your work at any time.

If you have opened a pull request but review has not yet started on it, please migrate your branch to the new code style before review starts.

If there is an ongoing review of a pull request, please communicate with the reviewer(s) to decide on a good time. Rebasing a branch during review is disruptive, because comments end up detached from the code they're about, so it's generally best not to do it. Typically the best time to migrate the branch is after the reviewer(s) have approved.

## How to migrate

### Requirements

Please have the following tools and files available:

* Git 2.17.0 or newer.
* [Uncrustify](https://github.com/uncrustify/uncrustify) 0.75.1. Please note that older or newer versions are likely not to give the desired result.
* Python 3.6 or newer.
* A Git worktree containing the branch of Mbed TLS you want to migrate.
* A local copy of [the branch rewriting script `mbedtls-rewrite-branch-style`](https://github.com/Mbed-TLS/mbedtls-docs/raw/main/tools/bin/mbedtls-rewrite-branch-style). Preferably use the most recent version, since it may have received bug fixes. You can check out the [`mbedtls-docs` repository](https://github.com/Mbed-TLS/mbedtls-docs).

### Simple migration

Prerequisites:

* You have the tools and files listed under [“Requirements”](#requirements) above.
* You have a Git branch `mywork` which branched from `development` before the code style switch. (For work on Mbed TLS 2.28, replace `development` by `mbedtls-2.28` throughout these instructions.)
* The current directory is a Git working directory with `mywork` checked out, and with a remote called `upstream` pointing to [the official Mbed TLS repository](https://github.com/Mbed-TLS/mbedtls).

Run the following command in a terminal, from the Git working directory with `mywork` checked out:

```sh
python3 ~/Downloads/mbedtls-rewrite-branch-style
```

If all goes well, you have successfully migrated `mywork`. You can force-push it to your fork of Mbed TLS (`git push --force-with-lease origin mywork`).

A backup of the old branch is available under the name `old-code-style/mywork`.

If all does not go well, please consult the [known limitations](#known-limitations) and the [troubleshooting section](#troubleshooting) section.

### Trial migration

The following procedure does not modify any existing Git working directory and does not rewrite any existing branch name. It explains how to migrate a branch `mywork` which branched from `development` before the code style switch. (For work on Mbed TLS 2.28, replace `development` by `mbedtls-2.28` throughout these instructions.). The result of the migration will be placed into a branch called `new-code-style/mywork` (it must not exist yet).

Run the following commands from any Git working directory. Adjust `~/Downloads` to the path containing the rewrite script, and `upstream` to the name of a Git remote pointing to [the official Mbed TLS repository](https://github.com/Mbed-TLS/mbedtls).

```sh
python3 ~/Downloads/mbedtls-rewrite-branch-style --onto upstream/development --new-branch-name new-code-style/mywork mywork
```

If all goes well, the branch `new-code-style/mywork` contains the migrated content of `mywork`.

If all does not go well, please consult the [known limitations](#known-limitations) and the [troubleshooting section](#troubleshooting) section.

## Known limitations

### Syntactically invalid commits

The automatic rewriting script can fail if an intermediate commit contains syntactically incorrect C code, for example unbalanced braces. If the script fails in an `uncrustify` command, this is the most likely reason.

Workaround: first do a manual rebase where you fix the syntax of the problematic commit.

Here is an example transcript with the end of the `--verbose` output showing this problem:
```
...
Applying efef9ffbba73433323137d22d7c675e9ceb0291c onto cb0ca794a4a7bea9db82659b6d4ae8b3e43ef9ee
efef9ffbba73433323137d22d7c675e9ceb0291c has been cherry-picked as c8a5ca2a1dbd3d4a0bf08b0216d8224bca8993fe
efef9ffbba73433323137d22d7c675e9ceb0291c has been amended to 8ae5bf5f1b7441d27d4b0c616d44f7ecba0691a7
Will restyle: library/x509_crt.c
Pass #0 of uncrustify
do_source_file(1507): Parsing: library/x509_crt.c as language C
parse_cleanup(528): pc->orig_line is 845, orig_col is 1, Text() is '}', type is BRACE_CLOSE
process_return(2180): temp->level is ZERO, cannot be decremented, at line 844, column 11
Traceback (most recent call last):
  File "../../bin/mbedtls-rewrite-branch-style", line 591, in <module>
    sys.exit(main())
  File "../../bin/mbedtls-rewrite-branch-style", line 575, in main
    branch_rewriter.rewrite(args.branch, update_existing_branch)
  File "../../bin/mbedtls-rewrite-branch-style", line 280, in rewrite
    self.do_rewrite(branch)
  File "../../bin/mbedtls-rewrite-branch-style", line 528, in do_rewrite
    self.restyle_commit_onto_current(new_commit)
  File "../../bin/mbedtls-rewrite-branch-style", line 496, in restyle_commit_onto_current
    self.restyle_files(files_to_restyle)
  File "../../bin/mbedtls-rewrite-branch-style", line 466, in restyle_files
    subprocess.check_call([self.UNCRUSTIFY_EXE,
  File "/usr/lib/python3.8/subprocess.py", line 364, in check_call
    raise CalledProcessError(retcode, cmd)
subprocess.CalledProcessError: Command '['uncrustify', '-c', '.uncrustify.cfg', '--no-backup', 'library/x509_crt.c']' returned non-zero exit status 70.
```
Look for the last “Applying ...” line in the transcript. Run `git show -s efef9ffbba73433323137d22d7c675e9ceb0291c` to list the commit date and commit message. Find this commit in your working branch (use `git log`); it will have a different commit ID because the commit ID in the transcript is after a rebase. In this example, the original commit with the same commit message was `93e4f76a3e9ca2d2448525657b3e0f7b3c6ed863`. To rewrite this commit, do an interactive rebase and ask to `93e4f76a3e9ca2d2448525657b3e0f7b3c6ed863`, keeping other commits intact. The last line of the transcript shows which file has the syntax error, and the previous messages give a hint as to where the error is. In the example above, the file is `library/x509_crt.c` and the error was detected at line 844. The actual problem turns out to be a missing `*/` a few lines above.

### Branches with merges

The rewrite script was written for simple cases of branches that fork from an official branch of Mbed TLS, and do not contain additional merges. If a branch contains merges, the script will fail.

Workaround: manually rebase on top of the last commit before the style change. If there are no merges left in your branch, you can use the script to do the rest of the work. Otherwise you'll need to do a manual merge instead of rewriting your branch.

## Troubleshooting

### If something goes wrong

If all did not go well, please re-run the script with the `--verbose` option and read the output to see what went wrong. If you can't figure it out, please post on the [mbed-tls mailing list](https://lists.trustedfirmware.org/mailman3/lists/mbed-tls.lists.trustedfirmware.org/) or raise an issue on the [mbedtls-docs repository](https://github.com/Mbed-TLS/mbedtls-docs/issues), including a link to the problematic branch and the **complete output from `mbedtls-rewrite-branch-style --verbose`**.

### Cleaning up after an error run

The script works in a temporary worktree following the pattern `tmp-%s-%d` where `%s` is the name of the branch being rewritten. If there is an error, this worktree is left behind. Use the command `git worktree list` to list existing worktrees. The following command shows output reduced worktrees that are probably from the branch rewriting script:
```console
$ git worktree list | grep /tmp-
/home/me/work/tmp-mybranch-1234
```
Use `git worktree remove -f /home/me/work/tmp-mybranch-1234` to remove the worktree.

### Wrong version of uncrustify

If you see the message
```
Unsupported version of uncrustify. This script needs 0.75.1.
```
please install the requested version of uncrustify. Unfortunately, different versions give different outputs, so everyone needs to use the same version.

If you have multiple versions of uncrustify installed, please make sure that the requested version comes first in the command search path (`$PATH` or `%PATH%`).

### Backup branch out of date

By default, the script backs up the old state of the branch under a name beginning with `old-code-style/`. If you run the rewrite script on a branch, then do more work on that branch, then run the rewrite script again, the script will fail with an error:
```
fatal: A branch named 'old-code-style/mybranch' already exists.
```
Please remove the old backup branch manually, then run the script again.

## Migrating existing work: the theory

If you started working on a branch of Mbed TLS with the old code style, any part of the code that has been both modified in your branch and restyled in the main branch will lead to a merge conflict. To avoid that, you must migrate your work to the new style.

It is not enough to rewrite the final state of your work to the new format, because that will still be a merge conflict (between just restyling, and semantically meaningful work followed by restyling). You must rebase-and-restyle your branch. This document explains how and when.

The Mbed TLS project provides a script [`mbedtls-rewrite-branch-style`](https://github.com/Mbed-TLS/mbedtls-docs/raw/main/tools/bin/mbedtls-rewrite-branch-style) which takes a Git branch with work done in the old code style, and migrates it to the new code style. Suppose your work is in a branch `mywork`, and it's intended to be submitted to some target branch (such as `development`). The migration works in two phases:

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

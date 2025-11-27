#!/usr/bin/env python3
"""Generate code indexes (TAGS, ...) for Mbed TLS or TF-PSA-Crypto.

Unless --all is specified, only generate indexes for which the relevant
program is available.
"""

#pylint: disable=invalid-name
# (only applies to the name of this file)
#pylint: enable=invalid-name

# Copyright The Mbed TLS Contributors
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later

import abc
import argparse
import os
import pathlib
import re
import shlex
import subprocess
import tempfile
import typing
from typing import Dict, List, Optional


class SourceTree:
    """Information about the source tree."""

    GIT_LS = ['git', 'ls-files', '-z', '--recurse-submodules']

    C_FILES_PATTERNS = [
        '**/*.[ch]',
        '**/*.function',
        '**/data_files/*.fmt',
        '**/driver_templates/*.jinja',
    ]

    def _git_ls(self, patterns: List[str]) -> List[str]:
        """List files checked into Git, including submodules."""
        raw = subprocess.check_output(self.GIT_LS + patterns,
                                      encoding='utf-8',
                                      cwd=self.dir)
        return raw.split('\0')[:-1]

    INCLUDE_FROM_HEADER_RE = re.compile(r'(.*/include)/.*')
    @classmethod
    def _include_from_header(cls, path: str) -> str:
        m = cls.INCLUDE_FROM_HEADER_RE.match(path)
        if m:
            return m.group(1)
        return os.path.dirname(path)

    def __init__(self, dir: str = os.curdir) -> None:
        # pylint: disable=redefined-builtin
        self.dir = pathlib.Path(dir)
        self.all_c_sources = self._git_ls(self.C_FILES_PATTERNS)
        all_headers = self._git_ls(['**/*.h'])
        self.all_include_dirs =sorted(frozenset(
            self._include_from_header(path)
            for path in all_headers))

    @property
    def all_c_files(self) -> List[str]:
        """The list of C source files (including headers).

        This includes submodules and templates from which C files are generated.
        """
        return self.all_c_sources

    @property
    def include_path(self) -> List[str]:
        """Return directories for the C compiler include path."""
        return self.all_include_dirs


class Indexer(abc.ABC):
    """Base abstract class for indexers."""

    # The program to run.
    _program : str

    @classmethod
    def name(cls) -> str:
        """The target name for this indexer."""
        return cls._program

    def __init__(self,
                 source_tree: SourceTree,
                 trace: bool = False,
                 verbose: bool = False,
                 commands: Optional[Dict[str, str]] = None) -> None:
        self.src = source_tree
        self.trace = trace
        self.verbose = verbose
        self.command = (commands.get(self._program, self._program)
                        if commands else self._program)

    @staticmethod
    def has_program(program: str) -> bool:
        # pylint: disable=redefined-builtin
        """Whether the given program is available in the command search path."""
        for dir in os.getenv('PATH', '').split(':'):
            if (pathlib.Path(dir) / program).exists():
                return True
        return False

    @classmethod
    def available(cls,
                 commands: Optional[Dict[str, str]] = None) -> bool:
        """Check whether the required tools are available.

        This method should not print any output.
        """
        return cls.has_program((commands.get(cls._program, cls._program)
                                if commands else cls._program))

    def _call(self, cmd: List[str]) -> None:
        """Call the specified program with arguments."""
        if self.trace:
            print(' '.join(['+'] + [shlex.quote(word) for word in cmd]))
        subprocess.check_call(cmd, cwd=self.src.dir)

    @classmethod
    @abc.abstractmethod
    def output_files(cls) -> List[str]:
        """The index file(s) created by run()."""
        raise NotImplementedError

    @abc.abstractmethod
    def run(self) -> None:
        """Run the program to generate the index."""
        raise NotImplementedError


class CscopeIndexer(Indexer):
    """Generate an index for cscope."""

    _program = 'cscope'

    @classmethod
    def output_files(cls) -> List[str]:
        return ['cscope.in.out', 'cscope.out', 'cscope.po.out']

    def run(self) -> None:
        """Generate the cscope index files."""
        self._call(['cscope', '-bq', '-u'] +
                   ['-I' + dir for dir in self.src.include_path] +
                   self.src.all_c_files)


class TagsIndexer(Indexer):
    """Abstract Indexer class for ctags and etags."""

    def _command_line(self, output_file: str) -> List[str]:
        """The command line to run, with implementation-dependent options."""
        cmd = [self.command]
        output_option = '-f'
        try:
            # Try to do what's best for exuberant-ctags and for the
            # tools bundled with emacs.
            help_text = subprocess.check_output([self.command, '--help'],
                                                encoding='utf-8')
            if '\n-o ' in help_text and not '\n-f ' in help_text:
                output_option = '-o'
            if '--langmap' in help_text:
                cmd.append('--langmap=c:+.h.function')
            elif '--langage' in help_text:
                cmd.append('--language=c')
            if '--no-line-directives' in help_text:
                cmd.append('--no-line-directives')
            elif '--line-directives=' in help_text:
                cmd.append('--line-directives=no')
        except subprocess.CalledProcessError:
            # --help didn't work. Assume a basic, classic ctags.
            pass
        cmd.append(output_option)
        cmd.append(output_file)
        return cmd + self.src.all_c_files

    def run(self) -> None:
        """Generate tags or TAGS."""
        self._call(self._command_line(str(self.src.dir / self.output_files()[0])))


class CtagsIndexer(TagsIndexer):
    """Generate tags for vi with ctags."""

    _program = 'ctags'

    @classmethod
    def output_files(cls) -> List[str]:
        return ['tags']


class EtagsIndexer(TagsIndexer):
    """Generate TAGS for emacs with etags."""

    _program = 'etags'

    @classmethod
    def output_files(cls) -> List[str]:
        return ['TAGS']


class GlobalIndexer(TagsIndexer):
    """Generate indexes for Global."""

    _program = 'gtags'

    @classmethod
    def output_files(cls) -> List[str]:
        return ['GPATH', 'GTAGS', 'GRTAGS']

    def run(self) -> None:
        """Generate GTAGS and friends for global."""
        with tempfile.NamedTemporaryFile(delete_on_close=False,
                                         mode='w+',
                                         encoding='ascii') as conf_file:
            with tempfile.NamedTemporaryFile(delete_on_close=False,
                                             mode='w+',
                                             encoding='utf-8') as list_file:
                conf_file.write(r'''
default:\
    :langmap=c\:.c.h.function:\

'''.lstrip('\n'))
                conf_file.close()
                list_file.write('\n'.join(self.src.all_c_files + ['']))
                list_file.close()
                self._call([self.command, '--gtagsconf', conf_file.name,
                            '--file', list_file.name])


ALL_INDEXERS = [
    CscopeIndexer,
    CtagsIndexer,
    EtagsIndexer,
    GlobalIndexer,
] #type: List[typing.Type[Indexer]]


def main() -> None:
    """Command line entry point."""
    parser = argparse.ArgumentParser()
    for program in sorted(cls._program for cls in ALL_INDEXERS):
        parser.add_argument('--command-' + program,
                            metavar='PROGRAM',
                            help='Alternative command instead of ' + program)
    parser.add_argument('--directory', '-d', metavar='DIR',
                        default=os.curdir,
                        help='Project root directory (default: current directory)')
    parser.add_argument('--list', '-l',
                        action='store_true',
                        help='List available targets and exit')
    parser.add_argument('--list-all', '-L',
                        action='store_true',
                        help='List all targets without checking tool availability')
    parser.add_argument('--trace',
                        action='store_true',
                        help='Print commands that are executed')
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='Print a lot of information')
    parser.add_argument('targets', nargs='*', metavar='TARGET',
                        help='Targets to generate (default: all available)')
    args = parser.parse_args()
    source_tree = SourceTree(dir=args.directory)
    alternative_programs = {}
    for cls in ALL_INDEXERS:
        command = getattr(args, 'command_' + cls._program, None)
        if command:
            alternative_programs[cls._program] = command
    if args.targets:
        indexer_dict = {cls.name(): cls for cls in ALL_INDEXERS}
        for cls in ALL_INDEXERS:
            for target in cls.output_files():
                indexer_dict.setdefault(target, cls)
        wanted_classes = [indexer_dict[target] for target in args.targets]
    elif args.list_all:
        wanted_classes = ALL_INDEXERS
    else:
        wanted_classes = [cls for cls in ALL_INDEXERS
                          if cls.available(commands=alternative_programs)]
    if args.list or args.list_all:
        for cls in wanted_classes:
            print(cls.name())
        return
    indexers = [cls(source_tree,
                    trace=args.trace,
                    verbose=args.verbose,
                    commands=alternative_programs)
                for cls in wanted_classes]
    for indexer in indexers:
        if args.verbose:
            print('Running', indexer.name(), '...')
        indexer.run()
        if args.verbose:
            print('Wrote', *indexer.output_files())

if __name__ == '__main__':
    main()

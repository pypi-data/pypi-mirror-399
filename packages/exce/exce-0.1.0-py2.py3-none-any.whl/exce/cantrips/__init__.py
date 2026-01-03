"""Cantrips - basic magic to bootstrap the nicer stuff"""

import sys, os, errno, autopep8, json
from IPython.core.magic import Magics, magics_class, cell_magic
from IPython import get_ipython

def path_parents(path):
    """Iterate over the parent directories of path."""
    head, tail = os.path.split(path)
    while tail:
        yield head
        head, tail = os.path.split(head)


def common_root(*names):
    """Find a root directory with 'name' for the current working directory."""
    python_match = set(path_parents(os.path.abspath(sys.executable)))

    head, tail = os.path.split(os.path.abspath(os.getcwd()))
    p = None

    while len(tail) > 0:
        p = os.path.join(head, *names) 
        if (p in python_match
            or os.path.isdir(os.path.join(head, '.git'))
            or os.path.exists(os.path.join(head, 'pyproject.toml'))):

            if os.path.isdir(p):
                return p

            break

        head, tail = os.path.split(head)

    raise FileNotFoundError(
        errno.ENOENT, 
        os.strerror(errno.ENOENT), 
        p
    )


def parse_filepath_from_magic_line(line):

    *libpath, module = line.split(' ')
    module_parts = module.split('.')

    while libpath and libpath[-1] == module_parts[0]:
        module_parts.pop(0)

    return os.path.join(common_root(*libpath), os.path.join(*module_parts) ) + '.py'


@magics_class
class CantripsMagic(Magics):

    @cell_magic
    def set_exportfile(self, line, cell=None):
        """Magic to export code from .qmd cells to python .py files"""

        self.filepath = parse_filepath_from_magic_line(line)
        print(f"Export file set to: {self.filepath}")

        with open(self.filepath, 'w') as f:
            f.write("# This file is generated - do not edit\n")
            if cell is not None:
                f.write(cell)

        if cell is not None:
            self.shell.run_cell(cell)

    @cell_magic
    def export(self, line, cell):
        line_args = line.split(' ')
        if len(line_args) > 0:
            if line_args[0] == '-f':
                if len(line_args) > 2:
                    cell = autopep8.fix_code(cell, options=json.loads(' '.join(line_args[1:]))) #options=json.loads(line_args[1]))
                else:
                    cell = autopep8.fix_code(cell)
            else:
                print(f"Unknown args: {line_args}")

        with open(self.filepath, 'a') as f:
            f.write(f"# {line}")
            f.write(cell)

        self.shell.set_next_input(f"%%export {line}\n{cell}", replace=False)
        self.shell.run_cell(cell)

def load_ipython_extension(ipython):
    ipython.register_magics(CantripsMagic)

__all__ = ['load_ipython_extension', 'CantripsMagic']


from __future__ import absolute_import, print_function

import sys


def main():
    import libcst.tool

    args = [
        "-x",
        "--no-format",
        "pyside_migrate.enum_codemod.MigrateEnumsCommand",
    ] + sys.argv[1:]
    print(args)
    sys.exit(libcst.tool._codemod_impl("pyside-migrate", args))

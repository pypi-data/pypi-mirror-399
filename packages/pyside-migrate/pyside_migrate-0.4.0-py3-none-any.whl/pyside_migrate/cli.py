from __future__ import absolute_import, print_function

import sys

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand


class MigrateCommand(VisitorBasedCodemodCommand):
    """Codemod command to migrate PySide2 code to PySide6."""

    DESCRIPTION = "Migrate PySide2 code to PySide6 (enums and type annotations)"

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """Transform the module by applying the enum migration and type renaming."""
        context = CodemodContext()

        # Apply enum migration transformer
        from pyside_migrate.enum_codemod import EnumMigrationTransformer
        enum_transformer = EnumMigrationTransformer(context)
        tree = tree.visit(enum_transformer)

        # Apply type rename transformer
        # from pyside_migrate.type_rename import TypeRenameTransformer
        # type_transformer = TypeRenameTransformer(context)
        # tree = tree.visit(type_transformer)

        return tree


def main():
    import libcst.tool

    args = [
        "-x",
        "--no-format",
        "pyside_migrate.cli.MigrateCommand",
    ] + sys.argv[1:]
    sys.exit(libcst.tool._codemod_impl("pyside-migrate", args))

"""Codemod to migrate PySide2 enums from Qt namespace to their specific enum classes."""

import json
from importlib.resources import files

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor


class EnumMigrationTransformer(cst.CSTTransformer):
    """Transforms Qt.EnumValue to Qt.EnumClass.EnumValue based on enum-mappings.json."""

    def __init__(self, context: CodemodContext) -> None:
        super().__init__()
        self.context = context

        # Load the enum mappings using importlib.resources
        mappings_text = files("pyside_migrate").joinpath("enum-mappings.json").read_text()
        self.mappings: dict[str, str] = json.loads(mappings_text)

        # Track import aliases (e.g., "from PySide2.QtCore import Qt as QtNamespace")
        self.qt_aliases: set[str] = set()

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Track imports to identify Qt aliases."""
        # Check if importing from PySide2.QtCore
        if self._is_pyside_qtcore_import(node.module):
            # Check if importing Qt with an alias
            if node.names and not isinstance(node.names, cst.ImportStar):
                for name in node.names:
                    if isinstance(name.name, cst.Name) and name.name.value == "Qt":
                        if name.asname:
                            # Track the alias (e.g., QtNamespace)
                            self.qt_aliases.add(name.asname.name.value)
                        else:
                            # No alias, just Qt
                            self.qt_aliases.add("Qt")

    def _is_pyside_qtcore_import(self, module: cst.Attribute | cst.Name | None) -> bool:
        """Check if module is PySide2.QtCore."""
        if module is None:
            return False
        if isinstance(module, cst.Name):
            return False
        if isinstance(module, cst.Attribute):
            module_path = self._get_attribute_path(module)
            return module_path == "PySide2.QtCore" or module_path == "Qt.QtCore"
        return False

    def leave_Attribute(
        self, original_node: cst.Attribute, updated_node: cst.Attribute
    ) -> cst.Attribute:
        """Transform attribute access like Qt.ActionMask to Qt.DropAction.ActionMask."""

        # Build the full attribute path (e.g., "Qt.ActionMask" or "QtCore.Qt.ActionMask")
        attr_path = self._get_attribute_path(updated_node)

        if not attr_path:
            return updated_node

        # Try to find a matching suffix in our mappings
        # This handles cases like:
        # - "Qt.AlignCenter" -> direct match
        # - "QtCore.Qt.AlignCenter" -> match "Qt.AlignCenter" suffix
        # - "PySide2.QtCore.Qt.AlignCenter" -> match "Qt.AlignCenter" suffix
        # - "QtNamespace.AlignCenter" -> match with alias tracking

        parts = attr_path.split(".")

        # Try different suffix lengths to find a match
        for i in range(len(parts)):
            suffix = ".".join(parts[i:])

            if suffix in self.mappings:
                new_suffix = self.mappings[suffix]

                # Reconstruct the path with the prefix and new suffix
                if i > 0:
                    prefix = ".".join(parts[:i])
                    new_path = f"{prefix}.{new_suffix}"
                else:
                    new_path = new_suffix

                # Convert the new path to a CST node
                new_node = self._build_attribute_from_path(new_path)
                if new_node:
                    return new_node

        # Check if this is an alias pattern (e.g., QtNamespace.AlignCenter)
        # where QtNamespace is an alias for Qt
        if len(parts) >= 2 and parts[0] in self.qt_aliases:
            # Try matching with "Qt" prefix instead of the alias
            qt_suffix = "Qt." + ".".join(parts[1:])
            if qt_suffix in self.mappings:
                new_suffix = self.mappings[qt_suffix]
                # Replace "Qt" with the original alias
                new_path = new_suffix.replace("Qt.", f"{parts[0]}.", 1)

                new_node = self._build_attribute_from_path(new_path)
                if new_node:
                    return new_node

        return updated_node

    def _get_attribute_path(self, node: cst.Attribute) -> str | None:
        """Extract the full attribute path from a CST Attribute node.

        For example, Qt.ActionMask -> "Qt.ActionMask"
        """
        parts = []
        current = node

        while isinstance(current, cst.Attribute):
            parts.append(current.attr.value)
            current = current.value

        if isinstance(current, cst.Name):
            parts.append(current.value)
        else:
            return None

        parts.reverse()
        return ".".join(parts)

    def _build_attribute_from_path(self, path: str) -> cst.Attribute | None:
        """Build a CST Attribute node from a dotted path string.

        For example, "Qt.DropAction.ActionMask" -> Attribute(Attribute(Name("Qt"), "DropAction"), "ActionMask")
        """
        parts = path.split(".")
        if len(parts) < 2:
            return None

        # Start with the first name
        result: cst.BaseExpression = cst.Name(parts[0])

        # Build up the attribute chain
        for part in parts[1:]:
            result = cst.Attribute(value=result, attr=cst.Name(part))

        if isinstance(result, cst.Attribute):
            return result

        return None


class MigrateEnumsCommand(VisitorBasedCodemodCommand):
    """Codemod command to migrate PySide2 enums to their specific locations."""

    DESCRIPTION = "Migrate PySide2 enums from Qt namespace to specific enum classes"

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """Transform the module by applying the enum migration."""
        context = CodemodContext()
        transformer = EnumMigrationTransformer(context)
        return tree.visit(transformer)

"""Codemod to migrate PySide2 enums from Qt namespace to their specific enum classes."""

import json
from importlib.resources import files

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor


def attribute_from_path(path: str) -> cst.Attribute | None:
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


def path_from_attribute(node: cst.Attribute) -> str | None:
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


class EnumMigrationTransformer(cst.CSTTransformer):
    """Transforms Qt.EnumValue to Qt.EnumClass.EnumValue based on enum-mappings.json."""

    package_names = ["PySide2", "Qt"]

    def __init__(self, context: CodemodContext) -> None:
        super().__init__()
        self.context = context

        # Load the enum mappings using importlib.resources
        mappings_text = (
            files("pyside_migrate").joinpath("enum-mappings.json").read_text()
        )
        self.mappings: dict[str, str] = json.loads(mappings_text)

        # Get the full path of all of the classes that with enum members that we need to rename
        tracked_classes = set(key.rsplit(".", 1)[0] for key in self.mappings)

        self.tracked_classes = set()
        for package in self.package_names:
            self.tracked_classes.update(
                f"{package}.{class_name}" for class_name in tracked_classes
            )

        # Get modules (e.g., "QtCore" from "QtCore.Qt")
        tracked_modules = set(key.rsplit(".", 1)[0] for key in tracked_classes)

        # Add package prefixes to tracked modules
        self.tracked_modules = set()
        for package in self.package_names:
            self.tracked_modules.update(f"{package}.{mod}" for mod in tracked_modules)

        # Track import aliases (e.g., "from PySide2.QtCore import Qt as QtNamespace")
        # mapping of local aliases to full name
        self.local_class_names: dict[str, str] = {}

        # Track import aliases (e.g., "from PySide2 import QtCore as QtCoreNamespace")
        # mapping of local aliases to full name
        self.local_module_names: dict[str, str] = {}

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Track imports to identify Qt aliases."""
        # Check if importing from PySide2.QtCore
        module_name = self._get_module_name(node.module)
        if module_name:
            # Check if importing Qt with an alias
            if node.names and not isinstance(node.names, cst.ImportStar):
                for name in node.names:
                    if isinstance(name.name, cst.Name):
                        full_name = f"{module_name}.{name.name.value}"
                        if full_name in self.tracked_classes:
                            if name.asname:
                                # Track the alias (e.g., QtNamespace)
                                self.local_class_names[name.asname.name.value] = (
                                    full_name
                                )
                            else:
                                # No alias
                                self.local_class_names[name.name.value] = full_name
                        elif full_name in self.tracked_modules:
                            if name.asname:
                                # Track the alias (e.g., QtNamespace)
                                self.local_module_names[name.asname.name.value] = (
                                    full_name
                                )
                            else:
                                # No alias
                                self.local_module_names[name.name.value] = full_name

    def visit_Import(self, node: cst.Import) -> None:
        """Track regular import statements like 'import PySide2.QtCore'."""
        for name in node.names:
            if isinstance(name.name, (cst.Name, cst.Attribute)):
                full_name = (
                    path_from_attribute(name.name)
                    if isinstance(name.name, cst.Attribute)
                    else name.name.value
                )
                if full_name:
                    # Check if this is a tracked module or if it contains tracked classes
                    local_name = name.asname.name.value if name.asname else full_name

                    # Check if it's a tracked module
                    for package in self.package_names:
                        for tracked in self.tracked_modules:
                            if full_name == f"{package}.{tracked}":
                                self.local_module_names[local_name] = full_name

                    # Also track if the full import path itself is a tracked module
                    if full_name in self.tracked_modules or any(
                        full_name.endswith(f".{mod}") for mod in self.tracked_modules
                    ):
                        # For imports like "import PySide2.QtCore", track the full path
                        # This allows matching against "PySide2.QtCore.Qt.AlignCenter"
                        self.local_module_names[local_name] = full_name

    def _get_module_name(self, module: cst.Attribute | cst.Name | None) -> str | None:
        """Get the module name from an import statement."""
        if module is None:
            return None
        if isinstance(module, cst.Name):
            return module.value
        if isinstance(module, cst.Attribute):
            return path_from_attribute(module)
        return None

    def _get_new_name(self, lookup_key: str):
        if lookup_key in self.mappings:
            new_value = self.mappings[
                lookup_key
            ]  # e.g., "QtCore.Qt.AlignmentFlag.AlignCenter"
            new_value = self._strip_package(new_value)  # Strip package if present
            # Replace the class prefix with the local name
            new_value = new_value.replace(without_package, parts[0], 1)
            new_node = attribute_from_path(new_value)
            if new_node:
                return new_node

    def leave_Attribute(
        self, original_node: cst.Attribute, updated_node: cst.Attribute
    ) -> cst.Attribute:
        """Transform attribute access like Qt.ActionMask to Qt.DropAction.ActionMask."""

        attr_path = path_from_attribute(updated_node)
        if not attr_path:
            return updated_node

        # e.g. "Qt.AlignCenter" -> ["Qt", "AlignCenter"]
        # or   "QtCore.Qt.AlignCenter" -> ["QtCore", "Qt", "AlignCenter"]

        parts = attr_path.split(".")

        # Strategy 1: Check if first part is an imported class (e.g., "Qt" -> "PySide2.QtCore.Qt")
        if parts[0] in self.local_class_names:
            full_class = self.local_class_names[parts[0]]  # e.g., "PySide2.QtCore.Qt"
            without_package = self._strip_package(full_class)  # e.g., "QtCore.Qt"

            # Build lookup key
            if len(parts) > 1:
                lookup_key = f"{without_package}.{'.'.join(parts[1:])}"  # e.g., "QtCore.Qt.AlignCenter"
            else:
                lookup_key = without_package

            if lookup_key in self.mappings:
                new_value = self.mappings[
                    lookup_key
                ]  # e.g., "QtCore.Qt.AlignmentFlag.AlignCenter"
                # Replace the class prefix with the local name
                new_value = new_value.replace(without_package, parts[0], 1)
                new_node = attribute_from_path(new_value)
                if new_node:
                    return new_node

        # Strategy 2: Check if prefix is an imported module (e.g., "QtCore" -> "PySide2.QtCore")
        # Try from longest to shortest prefix
        for i in range(len(parts) - 1, 0, -1):
            prefix = ".".join(parts[:i])
            if prefix in self.local_module_names:
                full_module = self.local_module_names[prefix]  # e.g., "PySide2.QtCore"
                without_package = self._strip_package(full_module)  # e.g., "QtCore"

                # Build lookup key
                suffix = ".".join(parts[i:])  # e.g., "Qt.AlignCenter"
                lookup_key = (
                    f"{without_package}.{suffix}"  # e.g., "QtCore.Qt.AlignCenter"
                )

                if lookup_key in self.mappings:
                    new_value = self.mappings[
                        lookup_key
                    ]  # e.g., "QtCore.Qt.AlignmentFlag.AlignCenter"
                    # Replace the module prefix with the local name
                    new_value = new_value.replace(without_package, prefix, 1)
                    new_node = attribute_from_path(new_value)
                    if new_node:
                        return new_node

        # Strategy 3: Try direct lookup with package stripping
        # This handles fully qualified imports like "PySide2.QtCore.Qt.AlignCenter"
        for package in self.package_names:
            if attr_path.startswith(f"{package}."):
                without_package = attr_path[
                    len(package) + 1 :
                ]  # Strip "PySide2." or "Qt."
                if without_package in self.mappings:
                    new_value = self.mappings[
                        without_package
                    ]  # e.g., "QtCore.Qt.AlignmentFlag.AlignCenter"
                    # Reconstruct with the package prefix
                    new_path = f"{package}.{new_value}"
                    new_node = attribute_from_path(new_path)
                    if new_node:
                        return new_node

        return updated_node

    def _strip_package(self, path: str) -> str:
        """Strip the package prefix (PySide2 or Qt) from a path.

        E.g., "PySide2.QtCore.Qt.AlignCenter" -> "QtCore.Qt.AlignCenter"
        """
        for package in self.package_names:
            if path.startswith(f"{package}."):
                return path[len(package) + 1 :]
        return path


class MigrateEnumsCommand(VisitorBasedCodemodCommand):
    """Codemod command to migrate PySide2 enums to their specific locations."""

    DESCRIPTION = "Migrate PySide2 enums from Qt namespace to specific enum classes"

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """Transform the module by applying the enum migration."""
        context = CodemodContext()
        transformer = EnumMigrationTransformer(context)
        return tree.visit(transformer)

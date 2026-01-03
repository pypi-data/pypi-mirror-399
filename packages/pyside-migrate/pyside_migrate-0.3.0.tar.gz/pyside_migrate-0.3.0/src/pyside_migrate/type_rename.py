"""Transformer to rename types in type annotations based on type-renames.json."""

import json
from importlib.resources import files

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand

from pyside_migrate.enum_codemod import (
    ImportTracker,
    attribute_from_path,
    get_module_name,
    path_from_attribute,
)


class TypeRenameTransformer(cst.CSTTransformer):
    """Transforms type annotations based on type-renames.json."""

    package_names = ["PySide2", "PySide6", "Qt"]

    def __init__(self, context: CodemodContext) -> None:
        super().__init__()
        self.context = context

        # Load the type rename mappings
        mappings_text = (
            files("pyside_migrate").joinpath("type-renames.json").read_text()
        )
        self.mappings: dict[str, str] = json.loads(mappings_text)

        # Get tracked classes from the mappings
        tracked_classes = set(key.rsplit(".", 1)[0] for key in self.mappings)
        self.import_tracker = ImportTracker(self.package_names, list(tracked_classes))

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Track imports to identify aliases."""
        self.import_tracker.track_import_from(node)

    def visit_Import(self, node: cst.Import) -> None:
        """Track regular import statements."""
        self.import_tracker.track_direct_import(node)

    def leave_Annotation(
        self, original_node: cst.Annotation, updated_node: cst.Annotation
    ) -> cst.Annotation:
        """Transform type annotations."""
        new_annotation_expr = self._transform_type_expression(updated_node.annotation)
        if new_annotation_expr is not updated_node.annotation:
            return updated_node.with_changes(annotation=new_annotation_expr)
        return updated_node

    def _transform_type_expression(
        self, node: cst.BaseExpression, parent_union_types: set[str] | None = None
    ) -> cst.BaseExpression:
        """Recursively transform a type expression.

        Handles:
        - Simple types: QtCore.QModelIndex
        - Subscripted types: list[QtCore.QModelIndex]
        - Nested subscripts: tuple[QtCore.QModelIndex, ...]
        - Union types: QtCore.QModelIndex | str

        Args:
            node: The expression to transform
            parent_union_types: Set of type strings that are part of a parent union.
                               Used to avoid creating duplicate types.
        """
        if parent_union_types is None:
            parent_union_types = set()

        # Handle subscripted types like list[X], tuple[X, Y], etc.
        if isinstance(node, cst.Subscript):
            # Check if this is typing.Union[...] or typing.Optional[...] which is similar to X | Y
            # Optional[X] is equivalent to Union[X, None]
            is_typing_union = False
            if isinstance(node.value, cst.Name):
                if node.value.value in ("Union", "Optional"):
                    is_typing_union = True
            elif isinstance(node.value, cst.Attribute):
                path = path_from_attribute(node.value)
                if path and (path.endswith(".Union") or path.endswith(".Optional")):
                    is_typing_union = True

            # If it's Union, collect all types in the union
            union_types_in_subscript = set()
            if is_typing_union:
                for slice_elem in node.slice:
                    if isinstance(slice_elem.slice, cst.Index):
                        union_types_in_subscript.update(
                            self._collect_union_types(slice_elem.slice.value)
                        )
                    elif isinstance(slice_elem.slice, cst.BaseExpression):
                        union_types_in_subscript.update(
                            self._collect_union_types(slice_elem.slice)
                        )

            # Transform the base type (e.g., "list" in list[X])
            new_value = self._transform_type_expression(node.value, parent_union_types)

            # Transform the subscript elements
            new_slice_elements = []
            changed = False
            for slice_elem in node.slice:
                # For Union, pass the collected types as context
                context_types = union_types_in_subscript if is_typing_union else parent_union_types
                new_elem = self._transform_subscript_element(slice_elem, context_types)
                if new_elem is not slice_elem:
                    changed = True
                new_slice_elements.append(new_elem)

            if new_value is not node.value or changed:
                return node.with_changes(value=new_value, slice=new_slice_elements)
            return node

        # Handle union types (X | Y)
        if isinstance(node, cst.BinaryOperation) and isinstance(
            node.operator, cst.BitOr
        ):
            # Collect all types in this union before transforming
            union_types = self._collect_union_types(node)

            # Transform each side with knowledge of sibling types
            new_left = self._transform_type_expression(node.left, union_types)
            new_right = self._transform_type_expression(node.right, union_types)

            if new_left is not node.left or new_right is not node.right:
                return node.with_changes(left=new_left, right=new_right)
            return node

        # Handle attribute access (e.g., QtCore.QModelIndex)
        if isinstance(node, cst.Attribute):
            attr_path = path_from_attribute(node)
            if not attr_path:
                return node

            parts = attr_path.split(".")

            # Strategy 1: Check if first part is an imported class
            if parts[0] in self.import_tracker.local_class_names:
                full_class = self.import_tracker.local_class_names[parts[0]]
                without_package = self._strip_package(full_class)

                # Build lookup key
                if len(parts) > 1:
                    lookup_key = f"{without_package}.{'.'.join(parts[1:])}"
                else:
                    lookup_key = without_package

                if lookup_key in self.mappings:
                    replacement = self.mappings[lookup_key]

                    # Check if we're in a union that already contains the replacement types
                    if self._replacement_already_present(replacement, without_package, parts[0], parent_union_types):
                        return node

                    # Parse the replacement and substitute the local name
                    return self._parse_replacement(replacement, without_package, parts[0])

            # Strategy 2: Check if prefix is an imported module
            for i in range(len(parts) - 1, 0, -1):
                prefix = ".".join(parts[:i])
                if prefix in self.import_tracker.local_module_names:
                    full_module = self.import_tracker.local_module_names[prefix]
                    without_package = self._strip_package(full_module)

                    # Build lookup key
                    suffix = ".".join(parts[i:])
                    lookup_key = f"{without_package}.{suffix}"

                    if lookup_key in self.mappings:
                        replacement = self.mappings[lookup_key]

                        # Check if replacement already present in parent union
                        if self._replacement_already_present(replacement, without_package, prefix, parent_union_types):
                            return node

                        # Parse the replacement and substitute the local name
                        return self._parse_replacement(replacement, without_package, prefix)

            # Strategy 3: Try direct lookup with package stripping
            for package in self.package_names:
                if attr_path.startswith(f"{package}."):
                    without_package = attr_path[len(package) + 1 :]
                    if without_package in self.mappings:
                        replacement = self.mappings[without_package]

                        # Check if replacement already present
                        if self._replacement_already_present(replacement, without_package, package, parent_union_types):
                            return node

                        # Parse and prepend package
                        parsed = self._parse_type_string(replacement)
                        return self._prepend_package_to_expression(parsed, package)

        # Handle simple names (e.g., just "QModelIndex" if imported directly)
        if isinstance(node, cst.Name):
            # Check if this name is in our tracked classes
            for full_class in self.import_tracker.local_class_names.values():
                without_package = self._strip_package(full_class)
                if without_package == node.value and without_package in self.mappings:
                    replacement = self.mappings[without_package]
                    return self._parse_type_string(replacement)

        return node

    def _transform_subscript_element(
        self, elem: cst.SubscriptElement, parent_union_types: set[str] | None = None
    ) -> cst.SubscriptElement:
        """Transform a single subscript element."""
        slice_node = elem.slice

        if isinstance(slice_node, cst.Index):
            # Wrapped index like Index(value=...)
            new_value = self._transform_type_expression(slice_node.value, parent_union_types)
            if new_value is not slice_node.value:
                new_slice = slice_node.with_changes(value=new_value)
                return elem.with_changes(slice=new_slice)
            return elem

        # In Python 3.9+, might be direct expression
        if isinstance(slice_node, cst.BaseExpression):
            new_value = self._transform_type_expression(slice_node, parent_union_types)
            if new_value is not slice_node:
                return elem.with_changes(slice=new_value)
            return elem

        return elem

    def _collect_union_types(self, node: cst.BaseExpression) -> set[str]:
        """Collect all type strings from a union expression.

        For `A | B | C`, returns {"A", "B", "C"}.
        """
        types = set()

        if isinstance(node, cst.BinaryOperation) and isinstance(node.operator, cst.BitOr):
            # Recursively collect from both sides
            types.update(self._collect_union_types(node.left))
            types.update(self._collect_union_types(node.right))
        elif isinstance(node, cst.Attribute):
            # Get the full path
            path = path_from_attribute(node)
            if path:
                types.add(path)
        elif isinstance(node, cst.Name):
            types.add(node.value)

        return types

    def _replacement_already_present(
        self,
        replacement: str,
        original_prefix: str,
        local_prefix: str,
        parent_union_types: set[str],
    ) -> bool:
        """Check if the replacement types are already present in the parent union.

        Args:
            replacement: The replacement string (e.g., "QtCore.Qt.ItemDataRole | int")
            original_prefix: The original prefix (e.g., "QtCore")
            local_prefix: The local name used (e.g., "QtCore" or alias)
            parent_union_types: Set of type strings already in the parent union

        Returns:
            True if all types from replacement are already in parent_union_types
        """
        if not parent_union_types:
            return False

        # Parse the replacement to get all types
        try:
            parsed = self._parse_type_string(replacement)
            # Replace prefix to match local names
            adjusted = self._replace_prefix_in_expression(parsed, original_prefix, local_prefix)
            # Collect types from the adjusted replacement
            replacement_types = self._collect_union_types(adjusted)

            # Check if all replacement types are already in the parent union
            return replacement_types.issubset(parent_union_types)
        except Exception:
            # If we can't parse, be conservative and don't skip
            return False

    def _parse_replacement(
        self, replacement: str, original_prefix: str, local_prefix: str
    ) -> cst.BaseExpression:
        """Parse a replacement string and substitute the prefix.

        Args:
            replacement: The replacement string (e.g., "QtCore.QModelIndex | QtCore.QPersistentModelIndex")
            original_prefix: The original prefix to replace (e.g., "QtCore")
            local_prefix: The local name to use (e.g., "QtCore" or an alias)
        """
        parsed = self._parse_type_string(replacement)
        return self._replace_prefix_in_expression(parsed, original_prefix, local_prefix)

    def _parse_type_string(self, type_string: str) -> cst.BaseExpression:
        """Parse a type string into a CST expression.

        Examples:
            "QtCore.QModelIndex | int" -> BinaryOperation with BitOr
            "QtCore.QModelIndex" -> Attribute chain
        """
        # Parse as a Python expression
        module = cst.parse_module(type_string)
        # Extract the expression from the module
        if (
            isinstance(module.body[0], cst.SimpleStatementLine)
            and isinstance(module.body[0].body[0], cst.Expr)
        ):
            return module.body[0].body[0].value
        raise ValueError(f"Could not parse type string: {type_string}")

    def _replace_prefix_in_expression(
        self, expr: cst.BaseExpression, old_prefix: str, new_prefix: str
    ) -> cst.BaseExpression:
        """Recursively replace a prefix in an expression."""
        if isinstance(expr, cst.Attribute):
            attr_path = path_from_attribute(expr)
            if attr_path and attr_path.startswith(old_prefix):
                # Replace the prefix
                new_path = attr_path.replace(old_prefix, new_prefix, 1)
                new_node = attribute_from_path(new_path)
                if new_node:
                    return new_node
            return expr

        if isinstance(expr, cst.BinaryOperation):
            new_left = self._replace_prefix_in_expression(expr.left, old_prefix, new_prefix)
            new_right = self._replace_prefix_in_expression(expr.right, old_prefix, new_prefix)
            if new_left is not expr.left or new_right is not expr.right:
                return expr.with_changes(left=new_left, right=new_right)
            return expr

        return expr

    def _prepend_package_to_expression(
        self, expr: cst.BaseExpression, package: str
    ) -> cst.BaseExpression:
        """Prepend a package name to all type references in an expression."""
        if isinstance(expr, cst.Attribute):
            attr_path = path_from_attribute(expr)
            if attr_path:
                new_path = f"{package}.{attr_path}"
                new_node = attribute_from_path(new_path)
                if new_node:
                    return new_node
            return expr

        if isinstance(expr, cst.BinaryOperation):
            new_left = self._prepend_package_to_expression(expr.left, package)
            new_right = self._prepend_package_to_expression(expr.right, package)
            if new_left is not expr.left or new_right is not expr.right:
                return expr.with_changes(left=new_left, right=new_right)
            return expr

        if isinstance(expr, cst.Name):
            # Simple name, make it an attribute
            new_path = f"{package}.{expr.value}"
            new_node = attribute_from_path(new_path)
            if new_node:
                return new_node

        return expr

    def _strip_package(self, path: str) -> str:
        """Strip the package prefix from a path."""
        for package in self.package_names:
            if path.startswith(f"{package}."):
                return path[len(package) + 1 :]
        return path


class TypeRenameCommand(VisitorBasedCodemodCommand):
    """Codemod command to rename types in annotations."""

    DESCRIPTION = "Rename types in type annotations based on type-renames.json"

    def transform_module_impl(self, tree: cst.Module) -> cst.Module:
        """Transform the module by applying type renaming."""
        context = CodemodContext()
        transformer = TypeRenameTransformer(context)
        return tree.visit(transformer)

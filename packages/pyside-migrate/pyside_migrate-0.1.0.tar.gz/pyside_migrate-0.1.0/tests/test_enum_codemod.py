"""Unit tests for the enum migration codemod."""

from libcst.codemod import CodemodTest

from pyside_migrate.enum_codemod import MigrateEnumsCommand


class TestEnumMigration(CodemodTest):
    """Test cases for the PySide2 enum migration codemod."""

    TRANSFORM = MigrateEnumsCommand

    def test_simple_enum_transformation(self) -> None:
        """Test basic enum transformation from Qt.EnumValue to Qt.EnumClass.EnumValue."""
        before = """
            from PySide2.QtCore import Qt

            alignment = Qt.AlignCenter
        """
        after = """
            from PySide2.QtCore import Qt

            alignment = Qt.AlignmentFlag.AlignCenter
        """
        self.assertCodemod(before, after)

    def test_multiple_enums_same_line(self) -> None:
        """Test transformation of multiple enums on the same line."""
        before = """
            from PySide2.QtCore import Qt

            flag = Qt.AlignLeft | Qt.AlignTop
        """
        after = """
            from PySide2.QtCore import Qt

            flag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        """
        self.assertCodemod(before, after)

    def test_multiple_enum_types(self) -> None:
        """Test transformation of different enum types."""
        before = """
            from PySide2.QtCore import Qt

            alignment = Qt.AlignCenter
            button = Qt.LeftButton
            orientation = Qt.Horizontal
            window_type = Qt.Window
        """
        after = """
            from PySide2.QtCore import Qt

            alignment = Qt.AlignmentFlag.AlignCenter
            button = Qt.MouseButton.LeftButton
            orientation = Qt.Orientation.Horizontal
            window_type = Qt.WindowType.Window
        """
        self.assertCodemod(before, after)

    def test_mouse_buttons(self) -> None:
        """Test transformation of various mouse button enums."""
        before = """
            from PySide2.QtCore import Qt

            left = Qt.LeftButton
            right = Qt.RightButton
            middle = Qt.MiddleButton
            back = Qt.BackButton
            forward = Qt.ForwardButton
        """
        after = """
            from PySide2.QtCore import Qt

            left = Qt.MouseButton.LeftButton
            right = Qt.MouseButton.RightButton
            middle = Qt.MouseButton.MiddleButton
            back = Qt.MouseButton.BackButton
            forward = Qt.MouseButton.ForwardButton
        """
        self.assertCodemod(before, after)

    def test_dock_widget_areas(self) -> None:
        """Test transformation of dock widget area enums."""
        before = """
            from PySide2.QtCore import Qt

            area = Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
        """
        after = """
            from PySide2.QtCore import Qt

            area = Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        """
        self.assertCodemod(before, after)

    def test_keyboard_modifiers(self) -> None:
        """Test transformation of keyboard modifier enums."""
        before = """
            from PySide2.QtCore import Qt

            mods = Qt.ControlModifier | Qt.ShiftModifier | Qt.AltModifier
        """
        after = """
            from PySide2.QtCore import Qt

            mods = Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.AltModifier
        """
        self.assertCodemod(before, after)

    def test_window_types(self) -> None:
        """Test transformation of window type enums."""
        before = """
            from PySide2.QtCore import Qt

            flags = Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        """
        after = """
            from PySide2.QtCore import Qt

            flags = Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        """
        self.assertCodemod(before, after)

    def test_item_flags(self) -> None:
        """Test transformation of item flag enums."""
        before = """
            from PySide2.QtCore import Qt

            flags = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        """
        after = """
            from PySide2.QtCore import Qt

            flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
        """
        self.assertCodemod(before, after)

    def test_text_interaction_flags(self) -> None:
        """Test transformation of text interaction flag enums."""
        before = """
            from PySide2.QtCore import Qt

            interaction = Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        """
        after = """
            from PySide2.QtCore import Qt

            interaction = Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        """
        self.assertCodemod(before, after)

    def test_orientation(self) -> None:
        """Test transformation of orientation enums."""
        before = """
            from PySide2.QtCore import Qt

            h = Qt.Horizontal
            v = Qt.Vertical
        """
        after = """
            from PySide2.QtCore import Qt

            h = Qt.Orientation.Horizontal
            v = Qt.Orientation.Vertical
        """
        self.assertCodemod(before, after)

    def test_function_call_argument(self) -> None:
        """Test transformation of enums used as function arguments."""
        before = """
            from PySide2.QtCore import Qt

            widget.setAlignment(Qt.AlignCenter)
            button.setOrientation(Qt.Horizontal)
        """
        after = """
            from PySide2.QtCore import Qt

            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button.setOrientation(Qt.Orientation.Horizontal)
        """
        self.assertCodemod(before, after)

    def test_comparison_operations(self) -> None:
        """Test transformation of enums in comparison operations."""
        before = """
            from PySide2.QtCore import Qt

            if button == Qt.LeftButton:
                pass
        """
        after = """
            from PySide2.QtCore import Qt

            if button == Qt.MouseButton.LeftButton:
                pass
        """
        self.assertCodemod(before, after)

    def test_dictionary_values(self) -> None:
        """Test transformation of enums in dictionary values."""
        before = """
            from PySide2.QtCore import Qt

            mapping = {
                "left": Qt.LeftButton,
                "right": Qt.RightButton,
            }
        """
        after = """
            from PySide2.QtCore import Qt

            mapping = {
                "left": Qt.MouseButton.LeftButton,
                "right": Qt.MouseButton.RightButton,
            }
        """
        self.assertCodemod(before, after)

    def test_list_elements(self) -> None:
        """Test transformation of enums in list elements."""
        before = """
            from PySide2.QtCore import Qt

            buttons = [Qt.LeftButton, Qt.RightButton, Qt.MiddleButton]
        """
        after = """
            from PySide2.QtCore import Qt

            buttons = [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton]
        """
        self.assertCodemod(before, after)

    def test_unmapped_enum_unchanged(self) -> None:
        """Test that enums not in the mapping are left unchanged."""
        before = """
            from PySide2.QtCore import Qt

            # Qt.SomeUnmappedEnum doesn't exist in enum-mappings.json
            value = Qt.Foo
        """
        after = """
            from PySide2.QtCore import Qt

            # Qt.SomeUnmappedEnum doesn't exist in enum-mappings.json
            value = Qt.Foo
        """
        self.assertCodemod(before, after)

    def test_non_qt_attribute_unchanged(self) -> None:
        """Test that non-Qt attributes are not transformed."""
        before = """
            class MyClass:
                AlignCenter = 1

            obj = MyClass()
            value = obj.AlignCenter
        """
        after = """
            class MyClass:
                AlignCenter = 1

            obj = MyClass()
            value = obj.AlignCenter
        """
        self.assertCodemod(before, after)

    def test_nested_expressions(self) -> None:
        """Test transformation in nested expressions."""
        before = """
            from PySide2.QtCore import Qt

            result = (Qt.AlignLeft | Qt.AlignTop) if condition else Qt.AlignCenter
        """
        after = """
            from PySide2.QtCore import Qt

            result = (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop) if condition else Qt.AlignmentFlag.AlignCenter
        """
        self.assertCodemod(before, after)

    def test_return_statement(self) -> None:
        """Test transformation in return statements."""
        before = """
            from PySide2.QtCore import Qt

            def get_alignment():
                return Qt.AlignCenter
        """
        after = """
            from PySide2.QtCore import Qt

            def get_alignment():
                return Qt.AlignmentFlag.AlignCenter
        """
        self.assertCodemod(before, after)

    def test_class_attribute_assignment(self) -> None:
        """Test transformation in class attribute assignments."""
        before = """
            from PySide2.QtCore import Qt

            class MyWidget:
                default_alignment = Qt.AlignCenter
                default_button = Qt.LeftButton
        """
        after = """
            from PySide2.QtCore import Qt

            class MyWidget:
                default_alignment = Qt.AlignmentFlag.AlignCenter
                default_button = Qt.MouseButton.LeftButton
        """
        self.assertCodemod(before, after)

    def test_match_flags(self) -> None:
        """Test transformation of match flag enums."""
        before = """
            from PySide2.QtCore import Qt

            flags = Qt.MatchExactly | Qt.MatchCaseSensitive
        """
        after = """
            from PySide2.QtCore import Qt

            flags = Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchCaseSensitive
        """
        self.assertCodemod(before, after)

    def test_input_method_hints(self) -> None:
        """Test transformation of input method hint enums."""
        before = """
            from PySide2.QtCore import Qt

            hints = Qt.ImhDigitsOnly | Qt.ImhNoAutoUppercase
        """
        after = """
            from PySide2.QtCore import Qt

            hints = Qt.InputMethodHint.ImhDigitsOnly | Qt.InputMethodHint.ImhNoAutoUppercase
        """
        self.assertCodemod(before, after)

    def test_drop_actions(self) -> None:
        """Test transformation of drop action enums."""
        before = """
            from PySide2.QtCore import Qt

            actions = Qt.CopyAction | Qt.MoveAction
        """
        after = """
            from PySide2.QtCore import Qt

            actions = Qt.DropAction.CopyAction | Qt.DropAction.MoveAction
        """
        self.assertCodemod(before, after)

    def test_screen_orientation(self) -> None:
        """Test transformation of screen orientation enums."""
        before = """
            from PySide2.QtCore import Qt

            orientation = Qt.LandscapeOrientation
            portrait = Qt.PortraitOrientation
        """
        after = """
            from PySide2.QtCore import Qt

            orientation = Qt.ScreenOrientation.LandscapeOrientation
            portrait = Qt.ScreenOrientation.PortraitOrientation
        """
        self.assertCodemod(before, after)


class _TestImportPatterns:
    """Test cases for different import patterns."""

    TRANSFORM = MigrateEnumsCommand
    MODULE: str

    def test_import_qtcore_module(self) -> None:
        """Test with 'from {self.MODULE} import QtCore' pattern."""
        before = f"""
            from {self.MODULE} import QtCore

            alignment = QtCore.Qt.AlignCenter
            button = QtCore.Qt.LeftButton
        """
        after = f"""
            from {self.MODULE} import QtCore

            alignment = QtCore.Qt.AlignmentFlag.AlignCenter
            button = QtCore.Qt.MouseButton.LeftButton
        """
        self.assertCodemod(before, after)

    def test_import_pyside2_qtcore(self) -> None:
        """Test with 'import {self.MODULE}.QtCore' pattern."""
        before = f"""
            import {self.MODULE}.QtCore

            alignment = {self.MODULE}.QtCore.Qt.AlignCenter
            button = {self.MODULE}.QtCore.Qt.LeftButton
        """
        after = f"""
            import {self.MODULE}.QtCore

            alignment = {self.MODULE}.QtCore.Qt.AlignmentFlag.AlignCenter
            button = {self.MODULE}.QtCore.Qt.MouseButton.LeftButton
        """
        self.assertCodemod(before, after)

    def test_import_qtcore_as_alias(self) -> None:
        """Test with 'import {self.MODULE}.QtCore as QtCore' pattern."""
        before = f"""
            import {self.MODULE}.QtCore as QtCore

            alignment = QtCore.Qt.AlignCenter
            button = QtCore.Qt.LeftButton
        """
        after = f"""
            import {self.MODULE}.QtCore as QtCore

            alignment = QtCore.Qt.AlignmentFlag.AlignCenter
            button = QtCore.Qt.MouseButton.LeftButton
        """
        self.assertCodemod(before, after)

    def test_import_qt_as_alias(self) -> None:
        """Test with 'from {self.MODULE}.QtCore import Qt as QtNamespace' pattern."""
        before = f"""
            from {self.MODULE}.QtCore import Qt as QtNamespace

            alignment = QtNamespace.AlignCenter
            button = QtNamespace.LeftButton
        """
        after = f"""
            from {self.MODULE}.QtCore import Qt as QtNamespace

            alignment = QtNamespace.AlignmentFlag.AlignCenter
            button = QtNamespace.MouseButton.LeftButton
        """
        self.assertCodemod(before, after)

    def test_mixed_import_patterns(self) -> None:
        """Test with mixed import patterns in the same file."""
        before = f"""
            from {self.MODULE}.QtCore import Qt
            from {self.MODULE} import QtCore

            alignment1 = Qt.AlignCenter
            alignment2 = QtCore.Qt.AlignLeft
        """
        after = f"""
            from {self.MODULE}.QtCore import Qt
            from {self.MODULE} import QtCore

            alignment1 = Qt.AlignmentFlag.AlignCenter
            alignment2 = QtCore.Qt.AlignmentFlag.AlignLeft
        """
        self.assertCodemod(before, after)

    def test_import_pyside2_only(self) -> None:
        """Test with 'import {self.MODULE}' pattern (fully qualified access)."""
        before = f"""
            import {self.MODULE}

            alignment = {self.MODULE}.QtCore.Qt.AlignCenter
        """
        after = f"""
            import {self.MODULE}

            alignment = {self.MODULE}.QtCore.Qt.AlignmentFlag.AlignCenter
        """
        self.assertCodemod(before, after)

    def test_from_pyside2_qtcore_import_multiple(self) -> None:
        """Test with 'from {self.MODULE}.QtCore import Qt, QObject' pattern."""
        before = f"""
            from {self.MODULE}.QtCore import Qt, QObject

            alignment = Qt.AlignCenter
            obj = QObject()
        """
        after = f"""
            from {self.MODULE}.QtCore import Qt, QObject

            alignment = Qt.AlignmentFlag.AlignCenter
            obj = QObject()
        """
        self.assertCodemod(before, after)

    def test_bitwise_operations_with_qtcore_prefix(self) -> None:
        """Test bitwise operations with QtCore prefix."""
        before = f"""
            from {self.MODULE} import QtCore

            flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
        """
        after = f"""
            from {self.MODULE} import QtCore

            flags = QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        """
        self.assertCodemod(before, after)

    def test_function_calls_with_module_prefix(self) -> None:
        """Test function calls with full module prefix."""
        before = f"""
            import {self.MODULE}.QtCore

            widget.setAlignment({self.MODULE}.QtCore.Qt.AlignCenter)
        """
        after = f"""
            import {self.MODULE}.QtCore

            widget.setAlignment({self.MODULE}.QtCore.Qt.AlignmentFlag.AlignCenter)
        """
        self.assertCodemod(before, after)


class TestPySideImportPatterns(_TestImportPatterns, CodemodTest):
    MODULE = "PySide2"


class TestQtpyImportPatterns(_TestImportPatterns, CodemodTest):
    MODULE = "Qt"

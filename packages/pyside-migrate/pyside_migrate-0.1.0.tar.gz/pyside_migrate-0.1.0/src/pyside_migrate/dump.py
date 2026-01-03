from __future__ import absolute_import, print_function

import inspect
import json
import enum
from pathlib import Path
from collections import defaultdict
from functools import cache


class PySideHelper:
    def __init__(self, pyside_package) -> None:
        self.pyside_package = pyside_package

    def is_pyside_obj(self, typ: type) -> bool:
        return typ.__module__.split(".")[0] in self.pyside_package

    @cache
    def is_flag(self, typ: type) -> bool:
        """A flag enum

        is_flag(PySide2.QtCore.QDir.Filter) is True
        is_flag(PySide6.QtCore.QDir.Filter) is True
        """
        if self.pyside_package == "PySide6":
            # FIXME: flag groups such as PySide6.QtCore.QDir.Filters will return True here
            return isinstance(typ, type) and issubclass(typ, enum.Flag)
        else:
            # in PySide2, the type of a flag item is a flag
            return self.is_flag_item_type(typ)

    @cache
    def is_enum(self, typ: type) -> bool:
        """An enum

        unlike flags, enums cannot be combined.

        is_enum(PySide2.QtCore.QLocale.Language) is True
        is_enum(PySide6.QtCore.QLocale.Language) is True
        """
        if self.pyside_package == "PySide6":
            # FIXME: flag groups such as PySide6.QtCore.QDir.Filters will return True here
            return isinstance(typ, type) and issubclass(typ, enum.Enum)
        else:
            return (
                hasattr(typ, "__pos__")
                and not hasattr(typ, "__invert__")
                and self.is_pyside_obj(typ)
                and typ.__bases__ == (object,)
            )

    def is_enum_item(self, obj: object) -> bool:
        """An individual enum item

        e.g.

        is_enum_item(PySide2.QtCore.QLocale.Language.Abkhazian) is True
        is_enum_item(PySide6.QtCore.QLocale.Language.Abkhazian) is True
        """
        if self.pyside_package == "PySide6":
            return isinstance(obj, enum.Enum) and not isinstance(obj, enum.Flag)
        else:
            return self.is_enum(type(obj))

    @cache
    def is_flag_group(self, typ: type) -> bool:
        """The result of joining two flag items

        In PySide6, with the switch to enum.Enum, the group and enum are the same
        object.

        e.g. PySide2.QtCore.QDir.Filters
        """
        if self.pyside_package == "PySide6":
            return False
        else:
            return (
                hasattr(typ, "__invert__")
                and not hasattr(typ, "values")
                and self.is_pyside_obj(typ)
                and typ.__bases__ == (object,)
            )

    @cache
    def is_flag_item_type(self, typ: type) -> bool:
        """The type of an individual flag item

        e.g.

        is_flag_item_type(type(PySide2.QtCore.QDir.Filter.AllDirs)) is True
        is_flag_item_type(type(PySide6.QtCore.QDir.Filter.AllDirs)) is True
        """
        if self.pyside_package == "PySide6":
            return isinstance(typ, type) and issubclass(typ, enum.Enum)
        else:
            return (
                hasattr(typ, "__invert__")
                and hasattr(typ, "values")
                and self.is_pyside_obj(typ)
                and typ.__bases__ == (object,)
            )

    def is_flag_item(self, obj: object) -> bool:
        """An individual flag item

        e.g.

        is_flag_item(PySide2.QtCore.QDir.Filter.AllDirs) is True
        is_flag_item(PySide6.QtCore.QDir.Filter.AllDirs) is True
        """
        if self.pyside_package == "PySide6":
            return isinstance(obj, enum.Flag)
        else:
            return self.is_flag_item_type(type(obj))

    def get_enum_kind(self, obj):
        typ = None
        if self.is_flag_item(obj):
            typ = "flag_item"
        elif self.is_enum_item(obj):
            typ = "enum_item"
        else:
            if isinstance(obj, type):
                if self.is_flag(obj):
                    typ = "flag"
                elif self.is_enum(obj):
                    typ = "enum"
                elif self.is_flag_group(obj):
                    typ = "flag_group"
        return typ


def dump_enums():
    from PySide2.QtCore import Qt

    helper = PySideHelper("PySide2")

    flags = defaultdict(set)
    for name, member in inspect.getmembers(Qt):
        print(f"{name:40}", helper.get_enum_kind(member))

        if isinstance(member, type) and (
            helper.is_flag(member) or helper.is_enum(member)
        ):
            flag_name = name
            for child_name in dir(member):
                child = getattr(member, child_name)
                if helper.is_flag_item(child) or helper.is_enum_item(child):
                    flags[child_name].add(flag_name)

    mapping = {}
    for name, member in inspect.getmembers(Qt):
        if helper.is_flag_item(member) or helper.is_enum_item(member):
            matches = list(flags[name])
            if len(matches) > 1:
                raise RuntimeError(f"{name} has more than one match: {matches}")
            mapping[f"Qt.{name}"] = f"Qt.{matches[0]}.{name}"

    output = Path(__file__).parent.joinpath("enum-mappings.json")
    with open(output, "w") as f:
        json.dump(mapping, f)

# Copyright (C) 2021 DigeeX
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Plugins that modify other plugins.
"""

from functools import partial
from typing import Callable, Optional, Union

from raider.plugins.common import Plugin


class Alter(Plugin):
    """Plugin used to alter other plugin's value.

    If the value extracted from other plugins cannot be used in it's raw
    form and needs to be somehow processed, Alter plugin can be used to
    do that. Initialize it with the original plugin and a function which
    will process the string and return the modified value.

    Attributes:
      alter_function:
        A function which will be given the plugin's value. It should
        return a string with the processed value.

    """

    def __init__(
        self,
        parent_plugin: Plugin,
        alter_function: Optional[Callable[[str], Optional[str]]] = None,
    ) -> None:
        """Initializes the Alter Plugin.

        Given the original plugin, and a function to alter the data,
        initialize the object, and get the modified value.

        Args:
          plugin:
            The original Plugin where the value is to be found.
          alter_function:
            The Function with instructions on how to alter the value.
        """
        super().__init__(
            name=parent_plugin.name,
            value=parent_plugin.value,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
            function=self.process_value,
        )
        self.plugins = [parent_plugin]
        self.alter_function = alter_function

    def process_value(self) -> Optional[str]:
        """Process the original plugin's value.

        Gives the original plugin's value to ``alter_function``. Return
        the processed value and store it in self.value.

        Returns:
          A string with the processed value.

        """
        if self.plugins[0].value:
            if self.alter_function:
                self.value = self.alter_function(self.plugins[0].value)
            else:
                self.value = None

        return self.value

    @classmethod
    def prepend(cls, parent_plugin: Plugin, string: str) -> "Alter":
        """Prepend a string to plugin's value."""
        alter = cls(
            parent_plugin=parent_plugin,
            alter_function=lambda value: string + value,
        )

        return alter

    @classmethod
    def append(cls, parent_plugin: Plugin, string: str) -> "Alter":
        """Append a string after the plugin's value"""
        alter = cls(
            parent_plugin=parent_plugin,
            alter_function=lambda value: value + string,
        )

        return alter

    @classmethod
    def replace(
        cls,
        parent_plugin: Plugin,
        old_value: str,
        new_value: Union[str, Plugin],
    ) -> "Alter":
        """Replace a substring from plugin's value with something else."""

        def replace_old_value(
            value: str, old: str, new: Union[str, Plugin]
        ) -> Optional[str]:
            """Replaces an old substring with the new one."""
            if isinstance(new, Plugin):
                if not new.value:
                    return None
                return value.replace(old, new.value)
            return value.replace(old, new)

        alter = cls(
            parent_plugin=parent_plugin,
            alter_function=partial(
                replace_old_value, old=old_value, new=new_value
            ),
        )

        if isinstance(new_value, Plugin):
            alter.plugins.append(new_value)

        return alter


class Combine(Plugin):
    """Plugin to combine the values of other plugins."""

    def __init__(self, *args: Union[str, Plugin]):
        """Initialize Combine object."""
        self.args = args
        name = str(sum(hash(item) for item in args))
        super().__init__(
            name=name,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
            function=self.concatenate_values,
        )
        self.plugins = []
        for item in args:
            if isinstance(item, Plugin):
                self.plugins.append(item)

    def concatenate_values(self) -> str:
        """Concatenate the provided values.

        This function will concatenate the arguments values. Accepts
        both strings and plugins.

        """
        combined = ""
        for item in self.args:
            if isinstance(item, str):
                combined += item
            elif item.value:
                combined += item.value
        return combined

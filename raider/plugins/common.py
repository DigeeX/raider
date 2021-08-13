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
"""Common Plugin classes used by other plugins.
"""


import logging
from typing import Callable, Dict, List, Optional

import requests


class Plugin:
    """Parent class for all plugins.

    Each Plugin class inherits from here. "get_value" function should
    be called when extracting the value from the plugin, which will then
    be stored in the "value" attribute.

    Attributes:
      name:
        A string used as an identifier for the Plugin.
      function:
        A function which will be called to extract the "value" of the
        Plugin when used as an input in a Flow. The function should set
        self.value and also return it.
      value:
        A string containing the Plugin's output value to be used as
        input in the HTTP request.
      flags:
        An integer containing the flags that define the Plugin's
        behaviour. For now only NEEDS_USERDATA and NEEDS_RESPONSE is
        supported. If NEEDS_USERDATA is set, the plugin will get its
        value from the user's data, which will be sent to the function
        defined here. If NEEDS_RESPONSE is set, the Plugin will extract
        its value from the HTTP response instead.

    """

    # Plugin flags
    NEEDS_USERDATA = 0x01
    NEEDS_RESPONSE = 0x02
    DEPENDS_ON_OTHER_PLUGINS = 0x04

    def __init__(
        self,
        name: str,
        function: Optional[Callable[..., Optional[str]]] = None,
        flags: int = 0,
        value: Optional[str] = None,
    ) -> None:
        """Initializes a Plugin object.

        Creates a Plugin object, holding a "function" defining how to
        extract the "value".

        Args:
          name:
            A string with the unique identifier of the Plugin.
          function:
            A Callable function that will be used to extract the
            Plugin's value.
          value:
            A string with the extracted value from the Plugin.
          flags:
            An integer containing the flags that define the Plugin's
            behaviour. For now only NEEDS_USERDATA and NEEDS_RESPONSE is
            supported. If NEEDS_USERDATA is set, the plugin will get its
            value from the user's data, which will be sent to the function
            defined here. If NEEDS_RESPONSE is set, the Plugin will extract
            its value from the HTTP response instead.

        """
        self.name = name
        self.plugins: List["Plugin"] = []
        self.value: Optional[str] = value
        self.flags = flags

        self.function: Callable[..., Optional[str]]

        if (flags & Plugin.NEEDS_USERDATA) and not function:
            self.function = self.extract_from_userdata
        elif not function:
            self.function = self.return_value
        else:
            self.function = function

    def get_value(
        self,
        userdata: Dict[str, str],
    ) -> Optional[str]:
        """Gets the value from the Plugin.

        Depending on the Plugin's flags, extract and return its value.

        Args:
          userdata:
            A dictionary with the user specific data.
        """
        if not self.needs_response:
            if self.needs_userdata:
                self.value = self.function(userdata)
            elif self.depends_on_other_plugins:
                for item in self.plugins:
                    item.get_value(userdata)
                self.value = self.function()
            else:
                self.value = self.function()
        return self.value

    def extract_value_from_response(
        self,
        response: Optional[requests.models.Response],
    ) -> None:
        """Extracts the value of the Plugin from the HTTP response.

        If NEEDS_RESPONSE flag is set, the Plugin will extract its value
        upon receiving the HTTP response, and store it inside the "value"
        attribute.

        Args:
          response:
            An requests.models.Response object with the HTTP response.

        """
        output = self.function(response)
        if output:
            self.value = output
            logging.debug(
                "Found ouput %s = %s",
                self.name,
                self.value,
            )
        else:
            logging.warning("Couldn't extract output: %s", str(self.name))

    def extract_from_userdata(
        self, data: Dict[str, str] = None
    ) -> Optional[str]:
        """Extracts the plugin value from userdata.

        Given a dictionary with the userdata, return its value with the
        same name as the "name" attribute from this Plugin.

        Args:
          data:
            A dictionary with user specific data.

        Returns:
          A string with the value of the variable found. None if no such
          variable has been defined.

        """
        if data and self.name in data:
            self.value = data[self.name]
        return self.value

    def return_value(self) -> Optional[str]:
        """Just return plugin's value.

        This is used when needing a function just to return the value.

        """
        return self.value

    @property
    def needs_userdata(self) -> bool:
        """Returns True if the NEEDS_USERDATA flag is set."""
        return bool(self.flags & self.NEEDS_USERDATA)

    @property
    def needs_response(self) -> bool:
        """Returns True if the NEEDS_RESPONSE flag is set."""
        return bool(self.flags & self.NEEDS_RESPONSE)

    @property
    def depends_on_other_plugins(self) -> bool:
        """Returns True if the DEPENDS_ON_OTHER_PLUGINS flag is set."""
        return bool(self.flags & self.DEPENDS_ON_OTHER_PLUGINS)


class Parser(Plugin):
    """Plugins that parse other plugins."""

    def __init__(
        self,
        name: str,
        function: Callable[[], Optional[str]],
        value: str = None,
    ) -> None:
        """Initializes the Parser plugin."""
        super().__init__(
            name=name,
            value=value,
            function=function,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )


class Empty(Plugin):
    """Empty plugin to use for fuzzing new data."""

    def __init__(self, name: str):
        """Initialize Empty plugin."""
        super().__init__(
            name=name,
            flags=0,
        )

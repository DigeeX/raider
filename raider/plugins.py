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

"""Plugins used as inputs/outputs in Flows.
"""

import json
import logging
import re
from base64 import b64encode
from typing import Any, Callable, Optional

import hy
from bs4 import BeautifulSoup

from raider.utils import hy_dict_to_python, match_tag


# pylint: disable=too-few-public-methods
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
        Plugin when used as an input in a Flow.
      value:
        A string containing the Plugin's output value.
    """

    def __init__(
        self,
        name: str,
        function: Callable[..., Optional[str]],
        value: Optional[str] = None,
    ) -> None:
        self.name = name
        self.function = function
        self.value: Optional[str] = value

    def get_value(self, data: Any = None) -> Optional[str]:
        if data:
            self.value = self.function(data)
        else:
            self.value = self.function()
        return self.value


class Regex(Plugin):
    """Plugin to extract something using regular expressions.

    This plugin will match the regex provided, and extract the value
    inside the matched group, which by default is the first one. A group
    is the string that matched inside the brackets.

    For example if the regular expression is:

    "accessToken":"([^"]+)"

    and the text to match it against contains:

    "accessToken":"0123456789abcdef"

    then only the string "0123456789abcdef" will be extracted and saved
    in the "value" attribute.

    Attributes:
      regex:
        A string containing the regular expression to be matched.
      extract:
        An integer with the group number that needs to be extracted.
    """

    def __init__(self, name: str, regex: str, extract: int = 0) -> None:
        super().__init__(name, self.extract_regex)
        self.regex = regex
        self.extract = extract

    def extract_regex(self, text: str) -> Optional[str]:
        matches = re.search(self.regex, text)
        if matches:
            groups = matches.groups()
            self.value = groups[self.extract]
            logging.debug("Regex %s: %s", self.name, str(self.value))
        else:
            logging.warning(
                "Regex %s not found in the response body", self.name
            )

        return self.value

    def __str__(self) -> str:
        return "Regex:" + self.regex + ":" + str(self.extract)


class Html(Plugin):
    """Plugin to extract something from an HTML tag.

    This Plugin will find the HTML "tag" containing the specified
    "attributes" and store the "extract" attribute of the matched tag
    in its "value" attribute.

    Attributes:
      tag:
        A string defining the HTML tag to look for.
      attributes:
        A dictionary with attributes matching the desired HTML tag. The
        keys in the dictionary are strings matching the tag's attributes,
        and the values are treated as regular expressions, to help
        match tags that don't have a static value.
      extract:
        A string defining the HTML tag's attribute that needs to be
        extracted and stored inside "value".
    """

    def __init__(
        self,
        name: str,
        tag: str,
        attributes: dict[hy.HyKeyword, str],
        extract: str,
    ) -> None:

        super().__init__(name, self.extract_html_tag)
        self.tag = tag
        self.attributes = hy_dict_to_python(attributes)
        self.extract = extract

    def extract_html_tag(self, text: str) -> Optional[str]:
        soup = BeautifulSoup(text, "html.parser")
        matches = soup.find_all(self.tag)

        for item in matches:
            if match_tag(item, self.attributes):
                self.value = item.attrs.get(self.extract)

        logging.debug("Html filter %s: %s", self.name, str(self.value))
        return self.value

    def __str__(self) -> str:
        return (
            "Html:"
            + self.tag
            + ":"
            + str(self.attributes)
            + ":"
            + str(self.extract)
        )


class Json(Plugin):
    """Plugin to extract a field from JSON.

    The "extract" attribute is used to specify which field to store
    in the "value". Using the dot "." character you can go deeper inside
    the JSON object. No arrays are supported yet.

    Attributes:
      extract:
        A string defining the location of the field that needs to be
        extracted. For now this is still quite primitive, and cannot
        access data from JSON arrays.

    """

    def __init__(self, name: str, extract: str) -> None:
        super().__init__(name, self.extract_json_field)
        self.extract = extract

    def extract_json_field(self, text: str) -> Optional[str]:
        parsed = json.loads(text)

        items = self.extract.split(".")
        temp = parsed
        for item in items:
            temp = temp[item]

        self.value = str(temp)
        logging.debug("Json filter %s: %s", self.name, str(self.value))
        return self.value

    def __str__(self) -> str:
        return "Json:" + str(self.extract)


class Variable(Plugin):
    """Plugin to extract the value of a variable.

    For now only the username and password variables are supported.
    Use this when supplying credentials to the web application.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name, self.extract_variable)

    def extract_variable(
        self, data: Optional[dict[str, Any]] = None
    ) -> Optional[str]:

        if data and self.name in data:
            self.value = data[self.name]
        return self.value


class Prompt(Plugin):
    """Plugin to ask the user for an input.

    Use this plugin when the value cannot be known in advance, for
    example when asking for multi-factor authentication code that is
    going to be sent over SMS.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name, self.get_user_prompt)

    def get_user_prompt(self) -> str:
        while not self.value:
            print("Please provide the input value")
            self.value = input(self.name + " = ")
        return self.value


class Cookie(Plugin):
    """Plugin to deal with HTTP cookies.

    Use this Plugin when dealing with the cookies in the HTTP request.
    """

    def __init__(
        self,
        name: str,
        value: Optional[str] = None,
        function: Optional[Callable[..., Optional[str]]] = None,
    ) -> None:

        if not function:
            super().__init__(name, lambda: self.value, value)
        else:
            super().__init__(name, function)

    def __str__(self) -> str:
        return str({self.name: self.value})


class Header(Plugin):
    """Plugin to deal with HTTP headers.

    Use this Plugin when dealing with the headers in the HTTP request.
    """

    def __init__(
        self,
        name: str,
        value: Optional[str] = None,
        function: Optional[Callable[..., Optional[str]]] = None,
    ) -> None:

        if not function:
            super().__init__(name, lambda: self.value, value)
        else:
            super().__init__(name, function)

    def __str__(self) -> str:
        return str({self.name: self.value})

    @classmethod
    def basicauth(cls, username: str, password: str) -> "Header":
        encoded = b64encode(":".join([username, password]).encode("utf-8"))
        header = cls("Authorization", "Basic " + encoded.decode("utf-8"))
        return header

    @classmethod
    def bearerauth(cls, access_token: Plugin) -> "Header":
        header = cls(
            "Authorization",
            None,
            lambda: "Bearer " + access_token.value
            if access_token.value
            else None,
        )
        return header

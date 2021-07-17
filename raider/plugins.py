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

        """
        self.name = name
        self.function = function
        self.value: Optional[str] = value

    def get_value(self, data: Any = None) -> Optional[str]:
        """Extracts the value of the Plugin.

        Given an optional "data", extracts the "value" of the Plugin
        storing it inside the object, and also returning it.

        Args:
          data:
            An Optional object to be passed to the Plugin's "function"
            when extracting the value.

        Returns:
          A string with the value of the Plugin or None if no output has
        been extracted.

        """
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
        """Initializes the Regex Plugin.

        Creates a Regex Plugin with the given regular expression, and
        extracts the matched group given in the "extract" argument, or
        the first matching group if not specified.

        Args:
          name:
            A string with the name of the Plugin.
          regex:
            A string containing the regular expression to be matched.
          extract:
            An optional integer with the number of the group to be
            extracted. By default the first group will be assumed.

        """
        super().__init__(name, self.extract_regex)
        self.regex = regex
        self.extract = extract

    def extract_regex(self, text: str) -> Optional[str]:
        """Extracts defined regular expression from a text.

        Given a text to be searched for matches, return the string
        inside the group defined in "extract" or the first group if it's
        undefined.

        Args:
          text:
            A string containing the text to be searched for matches.

        Returns:
          A string with the match from the extracted group. Returns None
          if there are no matches.

        """
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
        """Returns a string representation of the Plugin."""
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
        """Initializes the Html Plugin.

        Creates a Html Plugin with the given "tag" and
        "attributes". Stores the "extract" attribute in the plugin's
        "value".

        Args:
          name:
            A string with the name of the Plugin.
          tag:
            A string with the HTML tag to look for.
          attributes:
            A hy dictionary with the attributes to look inside HTML
            tags. The values of dictionary elements are treated as
            regular expressions.
          extract:
            A string with the HTML tag attribute that needs to be
            extracted and stored in the Plugin's object.

        """
        super().__init__(name, self.extract_html_tag)
        self.tag = tag
        self.attributes = hy_dict_to_python(attributes)
        self.extract = extract

    def extract_html_tag(self, text: str) -> Optional[str]:
        """Extract data from an HTML tag.

        Given the HTML text, parses it, iterates through the tags, and
        find the one matching the attributes. Then it stores the matched
        "value" and returns it.

        Args:
          text:
            A string containing the HTML text to be processed.

        Returns:
          A string with the match as defined in the Plugin. Returns None
          if there are no matches.

        """
        soup = BeautifulSoup(text, "html.parser")
        matches = soup.find_all(self.tag)

        for item in matches:
            if match_tag(item, self.attributes):
                self.value = item.attrs.get(self.extract)

        logging.debug("Html filter %s: %s", self.name, str(self.value))
        return self.value

    def __str__(self) -> str:
        """Returns a string representation of the Plugin."""
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
        """Initializes the Json Plugin.

        Creates the Json Plugin and extracts the specified field.

        Args:
          name:
            A string with the name of the Plugin.
          extract:
            A string with the location of the JSON field to extract.
        """
        super().__init__(name, self.extract_json_field)
        self.extract = extract

    def extract_json_field(self, text: str) -> Optional[str]:
        """Extracts the JSON field from the text.

        Given the JSON body as a string, extract the field and store it
        in the Plugin's "value" attribute.

        Args:
          text:
            A string with the JSON body.

        Returns:
          A string with the result of extraction. If no such field is
          found None will be returned.

        """
        parsed = json.loads(text)

        items = self.extract.split(".")
        temp = parsed
        for item in items:
            temp = temp[item]

        self.value = str(temp)
        logging.debug("Json filter %s: %s", self.name, str(self.value))
        return self.value

    def __str__(self) -> str:
        """Returns a string representation of the Plugin."""
        return "Json:" + str(self.extract)


class Variable(Plugin):
    """Plugin to extract the value of a variable.

    For now only the username and password variables are supported.
    Use this when supplying credentials to the web application.
    """

    def __init__(self, name: str) -> None:
        """Initializes the Variable Plugin.

        Creates a Variable object that will return the data from a
        previously defined variable.

        Args:
          name:
            The name of the variable.

        """
        super().__init__(name, self.extract_variable)

    def extract_variable(self, data: dict[str, str] = None) -> Optional[str]:
        """Extracts the variable value.

        Given a dictionary with the predefined variables, return the
        value of the with the same name as the "name" attribute from
        this Plugin.

        Args:
          data:
            A dictionary with the predefined variables.

        Returns:
          A string with the value of the variable found. None if no such
          variable has been defined.

        """
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
        """Initializes the Prompt Plugin.

        Creates a Prompt Plugin which will ask the user's input to get
        the Plugin's value.

        Args:
          name:
            A string containing the prompt asking the user for input.

        """
        super().__init__(name, self.get_user_prompt)

    def get_user_prompt(self) -> str:
        """Gets the value from user input.

        Creates a prompt asking the user for input and stores the value
        in the Plugin.

        """
        self.value = None
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
        """Initializes the Cookie Plugin.

        Creates a Cookie Plugin, either with predefined value, or by
        using a function defining how the value should be generated on
        runtime.

        Args:
          name:
            A string with the name of the Cookie.
          value:
            An optional string with the value of the Cookie in case it's
            already known.
          function:
            A Callable function which is used to get the value of the
            Cookie on runtime.

        """
        if not function:
            super().__init__(name, lambda: self.value, value)
        else:
            super().__init__(name, function)

    def __str__(self) -> str:
        """Returns a string representation of the cookie."""
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
        """Initializes the Header Plugin.

        Creates a Header Plugin, either with predefined value, or by
        using a function defining how the value should be generated on
        runtime.

        Args:
          name:
            A string with the name of the Header.
          value:
            An optional string with the value of the Header in case it's
            already known.
          function:
            A Callable function which is used to get the value of the
            Header on runtime.

        """
        if not function:
            super().__init__(name, lambda: self.value, value)
        else:
            super().__init__(name, function)

    def __str__(self) -> str:
        """Returns a string representation of the Plugin."""
        return str({self.name: self.value})

    @classmethod
    def basicauth(cls, username: str, password: str) -> "Header":
        """Creates a basic authentication header.

        Given the username and the password for the basic
        authentication, returns the Header object with the proper value.

        Args:
          username:
            A string with the basic authentication username.
          password:
            A string with the basic authentication password.

        Returns:
          A Header object with the encoded basic authentication string.

        """
        encoded = b64encode(":".join([username, password]).encode("utf-8"))
        header = cls("Authorization", "Basic " + encoded.decode("utf-8"))
        return header

    @classmethod
    def bearerauth(cls, access_token: Plugin) -> "Header":
        """Creates a bearer authentication header.

        Given the access_token as a Plugin, extracts its value and
        returns a Header object with the correct value to be passed as
        the Bearer Authorization string in the Header.

        Args:
          access_token:
            A Plugin containing the value of the token to use.

        Returns:
          A Header object with the proper bearer authentication string.

        """
        header = cls(
            "Authorization",
            None,
            lambda: "Bearer " + access_token.value
            if access_token.value
            else None,
        )
        return header

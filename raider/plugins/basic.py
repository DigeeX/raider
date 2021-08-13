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
"""Basic plugins.
"""

import json
import logging
import os
import re
from base64 import b64encode
from typing import Callable, Dict, Optional

import hy
import requests
from bs4 import BeautifulSoup

from raider.plugins.common import Plugin
from raider.utils import hy_dict_to_python, match_tag, parse_json_filter


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
        super().__init__(
            name=name,
            function=self.extract_regex,
            flags=Plugin.NEEDS_RESPONSE,
        )
        self.regex = regex
        self.extract = extract

    def extract_regex(
        self, response: requests.models.Response
    ) -> Optional[str]:
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
        matches = re.search(self.regex, response.text)
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
        attributes: Dict[hy.HyKeyword, str],
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
        super().__init__(
            name=name,
            function=self.extract_html_tag,
            flags=Plugin.NEEDS_RESPONSE,
        )
        self.tag = tag
        self.attributes = hy_dict_to_python(attributes)
        self.extract = extract

    def extract_html_tag(
        self, response: requests.models.Response
    ) -> Optional[str]:
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
        soup = BeautifulSoup(response.text, "html.parser")
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

    The "extract" attribute is used to specify which field to store in
    the "value". Using the dot ``.`` character you can go deeper inside
    the JSON object. To look inside an array, use square brackets
    `[]`.

    Keys with special characters should be written inside double quotes
    ``"``. Keep in mind that when written inside ``hyfiles``,
    it'll already be between double quotes, so you'll have to escape
    them with the backslash character ``\\``.

    Examples:

      ``env.production[0].field``
      ``production.keys[1].x5c[0][1][0]."with space"[3]``

    Attributes:
      extract:
        A string defining the location of the field that needs to be
        extracted. For now this is still quite primitive, and cannot
        access data from JSON arrays.

    """

    def __init__(
        self,
        name: str,
        extract: str,
        function: Callable[[str], Optional[str]] = None,
        flags: int = Plugin.NEEDS_RESPONSE,
    ) -> None:
        """Initializes the Json Plugin.

        Creates the Json Plugin and extracts the specified field.

        Args:
          name:
            A string with the name of the Plugin.
          extract:
            A string with the location of the JSON field to extract.
        """
        if not function:
            super().__init__(
                name=name,
                function=self.extract_json_from_response,
                flags=flags,
            )
        else:
            super().__init__(
                name=name,
                function=function,
                flags=flags,
            )

        self.extract = extract

    def extract_json_from_response(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Extracts the json field from a HTTP response."""
        return self.extract_json_field(response.text)

    def extract_json_from_plugin(self) -> Optional[str]:
        """Extracts the json field from a plugin."""
        if self.plugins[0].value:
            return self.extract_json_field(self.plugins[0].value)
        return None

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
        data = json.loads(text)

        json_filter = parse_json_filter(self.extract)
        is_valid = True
        temp = data
        for item in json_filter:
            if item.startswith("["):
                index = int(item.strip("[]"))
                if len(temp) > index:
                    temp = temp[index]
                else:
                    logging.warning(
                        (
                            "JSON array index doesn't exist.",
                            "Cannot extract plugin's value.",
                        )
                    )
                    is_valid = False
                    break
            else:
                if item in temp:
                    temp = temp[item]
                else:
                    logging.warning(
                        (
                            "Key '%s' not found in the response body.",
                            "Cannot extract plugin's value.",
                        ),
                        item,
                    )
                    is_valid = False
                    break

        if is_valid:
            self.value = str(temp)
            logging.debug("Json filter %s: %s", self.name, str(self.value))
        else:
            return None

        return self.value

    @classmethod
    def from_plugin(
        cls, parent_plugin: Plugin, name: str, extract: str
    ) -> "Json":
        """Extracts the JSON field from another plugin's value."""
        json_plugin = cls(
            name=name,
            extract=extract,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )
        json_plugin.plugins = [parent_plugin]
        json_plugin.function = json_plugin.extract_json_from_plugin
        return json_plugin

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
        super().__init__(
            name=name,
            function=lambda data: data[self.name],
            flags=Plugin.NEEDS_USERDATA,
        )


class Command(Plugin):
    """Runs a shell command and extract the output."""

    def __init__(self, name: str, command: str) -> None:
        """Initializes the Command Plugin.

        The specified command will be executed with os.popen() and the
        output with the stripped last newline, will be saved inside the
        value.

        Args:
          name:
            A unique identifier for the plugin.
          command:
            The command to be executed.

        """
        self.command = command
        super().__init__(
            name=name,
            function=self.run_command,
        )

    def run_command(self) -> Optional[str]:
        """Runs a command and returns its value.

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
        self.value = os.popen(self.command).read().strip()

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
        super().__init__(name=name, function=self.get_user_prompt)

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
        flags: int = Plugin.NEEDS_RESPONSE,
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
            if flags & Plugin.NEEDS_RESPONSE:
                super().__init__(
                    name=name,
                    function=self.extract_from_response,
                    value=value,
                    flags=flags,
                )
            else:
                super().__init__(
                    name=name,
                    value=value,
                    flags=flags,
                )

        else:
            super().__init__(
                name=name, function=function, value=value, flags=flags
            )

    def extract_from_response(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Returns the cookie with the specified name from the response."""
        return response.cookies.get(self.name)

    def __str__(self) -> str:
        """Returns a string representation of the cookie."""
        return str({self.name: self.value})

    @classmethod
    def from_plugin(cls, parent_plugin: Plugin, name: str) -> "Cookie":
        """Creates a Cookie from a Plugin.

        Given another :class:`plugin <raider.plugins.Plugin>`, and a
        name, create a :class:`cookie <raider.plugins.Cookie>`.

        Args:
          name:
            The cookie name to use.
          plugin:
            The plugin which will contain the value we need.

        Returns:
          A Cookie object with the name and the plugin's value.

        """
        cookie = cls(
            name=name,
            value=parent_plugin.value,
            flags=0,
        )
        return cookie


class Header(Plugin):
    """Plugin to deal with HTTP headers.

    Use this Plugin when dealing with the headers in the HTTP request.
    """

    def __init__(
        self,
        name: str,
        value: Optional[str] = None,
        function: Optional[Callable[..., Optional[str]]] = None,
        flags: int = Plugin.NEEDS_RESPONSE,
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
            if flags & Plugin.NEEDS_RESPONSE:
                super().__init__(
                    name=name,
                    function=self.extract_from_response,
                    value=value,
                    flags=flags,
                )

            else:
                super().__init__(
                    name=name,
                    value=value,
                    flags=flags,
                )

        else:
            super().__init__(
                name=name, function=function, value=value, flags=flags
            )

    def extract_from_response(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Returns the header with the specified name from the response."""
        return response.headers.get(self.name)

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
            name="Authorization",
            value=None,
            flags=0,
            function=lambda: "Bearer " + access_token.value
            if access_token.value
            else None,
        )
        return header

    @classmethod
    def from_plugin(cls, parent_plugin: Plugin, name: str) -> "Header":
        """Creates a Header from a Plugin.

        Given another :class:`plugin <raider.plugins.Plugin>`, and a
        name, create a :class:`header <raider.plugins.Header>`.

        Args:
          name:
            The header name to use.
          plugin:
            The plugin which will contain the value we need.

        Returns:
          A Header object with the name and the plugin's value.

        """
        header = cls(
            name=name,
            value=parent_plugin.value,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )
        header.plugins = [parent_plugin]
        header.function = lambda: header.plugins[0].value
        return header

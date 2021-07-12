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

"""Operations performed on Flows after the response is received.
"""

import re
import sys
from typing import Any, Union

import requests

from raider.plugins import Html, Json, Regex, Variable


class Http:
    """Operation that runs actions depending on the HTTP status code.

    A Http object will check if the HTTP response status code matches
    the code defined in its "status" attribute, and run the Operation
    inside "action" if it matches or the one inside "otherwise" if not
    matching.

    Attributes:
      status:
        An integer with the HTTP status code to be checked.
      action:
        An Operation that will be executed if the status code matches.
      otherwise:
        An Operation that will be executed if the status code doesn't
        match.

    """

    def __init__(
        self,
        status: int,
        **kwargs: Any,
    ) -> None:

        self.status = status
        self.action = kwargs.get("action")
        self.otherwise = kwargs.get("otherwise")

    def run(self, response: requests.models.Response) -> Any:
        match = False
        if self.status == response.status_code:
            match = True

        if match:
            return self.action

        return self.otherwise

    def __str__(self) -> str:
        return "Http:" + str(self.status) + ":" + str(self.action.__str__())


class Grep:
    """Operation that runs actions depending on Regex matches.

    A Grep object will check if the HTTP response body matches the regex
    defined in its "regex" attribute, and run the Operation inside
    "action" if it matches or the one inside "otherwise" if not
    matching.

    Attributes:
      regex:
        A string with the regular expression to be checked.
      action:
        An Operation that will be executed if the status code matches.
      otherwise:
        An Operation that will be executed if the status code doesn't
        match.

    """

    def __init__(self, regex: str, **kwargs: Any) -> None:
        self.regex = regex
        self.action = kwargs.get("action")
        self.otherwise = kwargs.get("otherwise")

    def run(self, response: requests.models.Response) -> Any:
        match = False
        if re.search(self.regex, response.text):
            match = True

        if match:
            return self.action

        return self.otherwise

    def __str__(self) -> str:
        return "Grep:" + str(self.regex) + ":" + str(self.action.__str__())


class Print:
    """Operation that prints desired information.

    When this Operation is executed, it will print each of its elements
    in a new line.

    Attributes:
      *args:
        A list of Plugins and/or strings. The plugin's extracted values
        will be printed.

    """

    def __init__(self, *args: Union[str, Variable, Regex, Html, Json]):
        self.args = args

    def run(self) -> None:
        for item in self.args:
            if isinstance(item, str):
                print(item)
            else:
                print(item.name + " = " + str(item.value))

    def __str__(self) -> str:
        return "Print:" + str(self.args)


class Error:
    """Operation that will exit Raider and print the error message.

    Attributes:
      message:
        A string with the error message to be printed.
    """

    def __init__(self, message: str) -> None:
        self.message = message

    def run(self) -> None:
        sys.exit(self.message)

    def __str__(self) -> str:
        return "Error:" + str(self.message)


# pylint: disable=too-few-public-methods
class NextStage:
    """Operation defining the next stage.

    Inside the Authentication object NextStage is used to define the
    next step of the authentication process. It can also be used inside
    "action" attributes of the other Operations to allow conditional
    decision making.

    Attributes:
      stage:
        A string with the name of the next stage to be executed.

    """

    def __init__(self, stage: str) -> None:
        self.stage = stage

    def __str__(self) -> str:
        if self.stage:
            return "NextStage:" + self.stage

        return "Authentication complete"

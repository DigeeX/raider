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

from raider.modules import Html, Json, Regex, Variable


class Http:
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
    def __init__(self, message: str) -> None:
        self.message = message

    def run(self) -> None:
        sys.exit(self.message)

    def __str__(self) -> str:
        return "Error:" + str(self.message)


class NextStage:
    def __init__(self, stage: str) -> None:
        self.stage = stage

    def __str__(self) -> str:
        if self.stage:
            return "NextStage:" + self.stage

        return "Authentication complete"

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

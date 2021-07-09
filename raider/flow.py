import logging
from typing import Optional, Union

import requests

from raider.config import Config
from raider.cookies import Cookie
from raider.headers import Header
from raider.modules import Html, Json, Regex
from raider.operations import Error, Grep, Http, NextStage, Print
from raider.request import Request
from raider.user import User


class Flow:
    def __init__(
        self,
        request: Request,
        name: str,
        outputs: list[Union[Regex, Html, Json]] = None,
        operations: list[Union[Error, Grep, Http, NextStage, Print]] = None,
    ) -> None:
        self.name = name

        self.outputs = outputs
        self.operations = operations

        self.request = request
        self.response: requests.models.Response = None

        self.logger = logging.getLogger(self.name)

    def execute(self, user: User, config: Config) -> None:
        self.response = self.request.send(user, config)
        self.get_outputs()

    def get_outputs(self) -> None:
        if not self.outputs:
            return

        for output in self.outputs:
            if isinstance(output, Cookie):
                value = self.response.cookies.get(output.name)
                if value:
                    output.value = value
                    self.logger.debug(
                        "Found cookie %s = %s",
                        output.name,
                        str(output.value),
                    )
                else:
                    self.logger.warning("Cookie %s not found", output.name)
            elif isinstance(output, Header):
                value = self.response.headers.get(output.name)
                if value:
                    output.value = value
                    self.logger.debug(
                        "Found header %s = %s",
                        output.name,
                        str(output.value),
                    )
                else:
                    self.logger.warning("Header %s not found", output.name)
            elif isinstance(output, (Html, Regex, Json)):
                result = output.get_value(self.response.text)
                if not result:
                    self.logger.warning(
                        "Couldn't extract output: %s", str(output)
                    )

    def run_operations(self) -> Optional[str]:
        next_stage = None

        if self.operations:
            for item in self.operations:
                operation = item
                while operation:
                    self.logger.debug("Running operation %s", str(operation))
                    if isinstance(operation, (Http, Grep)):
                        operation = operation.run(self.response)
                    elif isinstance(operation, (Error, Print)):
                        operation.run()
                        break
                    elif isinstance(operation, NextStage):
                        next_stage = operation.stage
                        break

        return next_stage

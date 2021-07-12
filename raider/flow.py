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

"""Flow class holding the information exchanged between server and client.
"""

import logging
from typing import Optional, Union

import requests

from raider.config import Config
from raider.operations import Error, Grep, Http, NextStage, Print
from raider.plugins import Cookie, Header, Html, Json, Plugin, Regex
from raider.request import Request
from raider.user import User


class Flow:
    """Class dealing with the information exchange from HTTP.

    A Flow object in Raider defines all the information about one single
    HTTP information exchange. It has a name, contains one request, the
    response, the outputs that needs to be extracted from the response,
    and a list of operations to be run when the exchange is over.

    Flow objects are used as states in the Authentication class to
    define the authentication process as a finite state machine.

    It's also used in the Functions class to run arbitrary actions when
    it doesn't affect the authentication state.

    Attributes:
      name:
        A string used as a unique identifier for the defined Flow.
      request:
        A Request object detailing the HTTP request with its elements.
      response:
        A requests.model.Response object. It's empty until the request
        is sent. When the HTTP response arrives, it's stored here.
      outputs:
        A list of Plugin objects detailing the pieces of information to
        be extracted from the response. Those will be later available
        for other Flow objects.
      operations:
        A list of Operation objects to be executed after the response is
        received and outputs are extracted. Should contain a NextStage
        operation if another Flow is expected.
      logger:
        A logging.RootLogger object used for debugging.

    """

    def __init__(
        self,
        name: str,
        request: Request,
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
            elif isinstance(output, Plugin):
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

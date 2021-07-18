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
from typing import Optional

import requests

from raider.config import Config
from raider.operations import Operation
from raider.plugins import Plugin
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
        outputs: list[Plugin] = None,
        operations: list[Operation] = None,
    ) -> None:
        """Initializes the Flow object.

        Creates the Flow object with the associated Request, the outputs
        to be extracted, and the operations to be run upon completion.

        Args:
          name:
            A string with a unique identifier for this Flow.
          request:
            A Request object associated with this Flow.
          outputs:
            A list of Plugins to be used for extracting data from the
            response.
          operations:
            A list of Operations to be run after the response is
            received.

        """
        self.name = name

        self.outputs = outputs
        self.operations = operations

        self.request = request
        self.response: requests.models.Response = None

        self.logger = logging.getLogger(self.name)

    def execute(self, user: User, config: Config) -> None:
        """Sends the request and extracts the outputs.

        Given the user in context and the global Raider configuration,
        sends the HTTP request and extracts the defined outputs.

        Args:
          user:
            A User object containing all the user specific data relevant
            for this action.
          config:
            A Config object with the global Raider configuration.

        """
        self.response = self.request.send(user, config)
        self.get_outputs()

    def get_outputs(self) -> None:
        """Extract the outputs from the HTTP response.

        Iterates through the defined outputs in the Flow object, and
        extracts the data from the HTTP response, saving it in the
        respective Plugin object.

        """
        if self.outputs:
            for output in self.outputs:
                output.extract_value(self.response)

    def run_operations(self) -> Optional[str]:
        """Runs the defined operations.

        Iterates through the defined operations and executes them one by
        one. Iteration stops when the first NextStage operations is
        encountered.

        Returns:
          Optionally, it returns a string with the name of the next
          stage to run.

        """
        next_stage = None

        if self.operations:
            for item in self.operations:
                next_stage = item.run(self.response)
                if next_stage:
                    break

        return next_stage

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

import logging
import re
import sys
from typing import Any, Callable, Optional, Union

import requests

from raider.plugins import Html, Json, Regex, Variable


def execute_actions(
    operations: Union["Operation", list["Operation"]],
    response: requests.models.Response,
) -> Optional[str]:
    """Run an Operation or a list of Operations.

    In order to allow multiple Operations to be run inside the "action"
    and "otherwise" attributes lists of Operations are accepted. The
    execution will stop if one of the Operations returns a string, to
    indicate the next stage has been decided.

    Args:
      operations:
        An Operation object or a list of Operations to be executed.
      response:
        A requests.models.Response object with the HTTP response that
        might be needed to run the Operation.

    Returns:
      A string with the name of the next stage to be run, or None.

    """
    if isinstance(operations, Operation):
        return operations.run(response)

    if isinstance(operations, list):
        for item in operations:
            output = item.run(response)
            if output:
                return output

    return None


class Operation:
    """Parent class for all operations.

    Each Operation class inherits from here.

    Attributes:
      function:
        A callable function to be executed when the operation is run.
      flags:
        An integer with the flags which define the behaviour of the
        Operation. For now only two flags are allowed: NEEDS_RESPONSE
        and IS_CONDITIONAL. If NEEDS_RESPONSE is set, the HTTP response
        will be sent to the "function" for further processing. If
        IS_CONDITIONAL is set, the function should return a boolean, and
        if the return value is True the Operation inside "action" will
        be run next, if it's False, the one from the "otherwise" will be
        run.
      action:
        An Operation object that will be run if the function returns
        True. Will only be used if the flag IS_CONDITIONAL is set.
      otherwise:
        An Operation object that will be run if the function returns
        False. Will only be used if the flag IS_CONDITIONAL is set.

    """

    # Operation flags
    IS_CONDITIONAL = 0x01
    NEEDS_RESPONSE = 0x02

    def __init__(
        self,
        function: Callable[..., Any],
        flags: int = 0,
        action: Optional[Union["Operation", list["Operation"]]] = None,
        otherwise: Optional[Union["Operation", list["Operation"]]] = None,
    ):
        """Initializes the Operation object.

        Args:
          function:
            A callable function to be executed when the operation is run.
          flags:
            An integer with the flags that define the behaviour of this
            Operation.
          action:
            An Operation object that will be run when the function
            returns True.
          otherwise:
            An Operation object that will be run when the function
            returns False.

        """
        self.function = function
        self.flags = flags
        self.action = action
        self.otherwise = otherwise

    def run(self, response: requests.models.Response) -> Optional[str]:
        """Runs the Operation.

        Runs the defined Operation, considering the "flags" set.

        Args:
          response:
            A requests.models.Response object with the HTTP response to
            be passed to the operation's "function".

        Returns:
          An optional string with the name of the next stage.

        """
        logging.debug("Running operation %s", str(self))
        if self.is_conditional:
            return self.run_conditional(response)
        if self.needs_response:
            return self.function(response)
        return self.function()

    def run_conditional(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Runs a conditional operation.

        If the IS_CONDITIONAL flag is set, run the Operation's
        "function" and if True runs the "action" next, if it's False
        runs the "otherwise" Operation instead.

        Args:
          response:
            A requests.models.Response object with the HTTP response to
            be passed to the operation's "function".

        Returns:
          An optional string with the name of the next stage.

        """
        if self.needs_response:
            check = self.function(response)
        else:
            check = self.function()

        if check and self.action:
            return execute_actions(self.action, response)
        if self.otherwise:
            return execute_actions(self.otherwise, response)

        return None

    @property
    def needs_response(self) -> bool:
        """Returns True if the NEEDS_RESPONSE flag is set."""
        return bool(self.flags & self.NEEDS_RESPONSE)

    @property
    def is_conditional(self) -> bool:
        """Returns True if the IS_CONDITIONAL flag is set."""
        return bool(self.flags & self.IS_CONDITIONAL)


class Http(Operation):
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
        action: Optional[Union[Operation, list[Operation]]],
        otherwise: Optional[Union[Operation, list[Operation]]] = None,
    ) -> None:
        """Initializes the Http Operation.

        Args:
          status:
            An integer with the HTTP response status code.
          action:
            An Operation object to be run if the defined status matches
            the response status code.
          otherwise:
            An Operation object to be run if the defined status doesn't
            match the response status code.

        """
        self.status = status
        super().__init__(
            function=self.match_status_code,
            action=action,
            otherwise=otherwise,
            flags=self.IS_CONDITIONAL | self.NEEDS_RESPONSE,
        )

    def match_status_code(self, response: requests.models.Response) -> bool:
        """Check if the defined status matches the response status code."""
        return self.status == response.status_code

    def __str__(self) -> str:
        """Returns a string representation of the Operation."""
        return (
            "(Http:"
            + str(self.status)
            + "="
            + str(self.action)
            + "/"
            + str(self.otherwise)
            + ")"
        )


class Grep(Operation):
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

    def __init__(
        self,
        regex: str,
        action: Operation,
        otherwise: Optional[Operation] = None,
    ) -> None:
        """Initializes the Grep Operation.

        Args:
          regex:
            A string with the regular expression to be checked.
          action:
            An Operation object to be run if the defined regex matches
            the response body.
          otherwise:
            An Operation object to be run if the defined regex doesn't
            match the response body.

        """
        self.regex = regex
        super().__init__(
            function=self.match_response,
            action=action,
            otherwise=otherwise,
            flags=self.IS_CONDITIONAL | self.NEEDS_RESPONSE,
        )

    def match_response(self, response: requests.models.Response) -> bool:
        """Checks if the response body contains the defined regex."""
        return bool(re.search(self.regex, response.text))

    def __str__(self) -> str:
        """Returns a string representation of the Operation."""
        return (
            "(Grep:"
            + str(self.regex)
            + "="
            + str(self.action)
            + "/"
            + str(self.otherwise)
            + ")"
        )


class Print(Operation):
    """Operation that prints desired information.

    When this Operation is executed, it will print each of its elements
    in a new line.

    Attributes:
      *args:
        A list of Plugins and/or strings. The plugin's extracted values
        will be printed.

    """

    def __init__(self, *args: Union[str, Variable, Regex, Html, Json]):
        """Initializes the Print Operation.

        Args:
          *args:
            Strings or Plugin objects to be printed.
        """
        self.args = args
        super().__init__(
            function=self.print_items,
        )

    def print_items(self) -> None:
        """Prints the defined items."""
        for item in self.args:
            if isinstance(item, str):
                print(item)
            else:
                print(item.name + " = " + str(item.value))

    def __str__(self) -> str:
        """Returns a string representation of the Print Operation."""
        return "(Print:" + str(self.args) + ")"


class Error(Operation):
    """Operation that will exit Raider and print the error message.

    Attributes:
      message:
        A string with the error message to be printed.
    """

    def __init__(self, message: str) -> None:
        """Initializes the Error Operation.

        Args:
          message:
            A string with the error message to be displayed.
        """
        self.message = message
        super().__init__(
            function=lambda: sys.exit(self.message),
        )

    def __str__(self) -> str:
        """Returns a string representation of the Operation."""
        return "(Error:" + str(self.message) + ")"


class NextStage(Operation):
    """Operation defining the next stage.

    Inside the Authentication object NextStage is used to define the
    next step of the authentication process. It can also be used inside
    "action" attributes of the other Operations to allow conditional
    decision making.

    Attributes:
      next_stage:
        A string with the name of the next stage to be executed.

    """

    def __init__(self, next_stage: Optional[str]) -> None:
        """Initializes the NextStage Operation.

        Args:
          next_stage:
            A string with the name of the next stage.
        """
        self.next_stage = str(next_stage)
        super().__init__(
            function=lambda: self.next_stage,
        )

    def __str__(self) -> str:
        """Returns a string representation of the Operation."""
        return "(NextStage:" + self.next_stage + ")"

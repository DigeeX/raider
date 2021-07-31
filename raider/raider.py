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

"""Main object used to perform common actions.
"""

import logging
import sys
from typing import Any, Callable, Optional

from raider.application import Application
from raider.attacks import Fuzz
from raider.authentication import Authentication


class Raider:
    """Main class used as the point of entry.

    The Raider class should be used to access everything else inside
    Raider. For now it's still not doing much, but for the future this
    is where all of the features available to the end user should be.

    Attributes:
      application:
        An :class:`Application <raider.application.Application>` object
        with the currently active project.
      config:
        A Config object containing all of the necessary settings.
      user:
        A User object containing the active user of the active project.
      functions:
        A Functions object containing the defined functions of the
        active project.

    """

    def __init__(self, project: Optional[str] = None) -> None:
        """Initializes the Raider object.

        Initializes the main entry point for Raider. If the name of the
        project is supplied, this application will be used, otherwise
        the last used application will be chosen.

        Args:
          project:
            A string with the name of the project.

        """
        self.application = Application(project)
        self.config = self.application.config
        self.user = self.application.active_user
        if hasattr(self.application, "functions"):
            self.functions = self.application.functions

    def authenticate(self, username: str = None) -> None:
        """Authenticates in the chosen application.

        Runs the authentication process from start to end on the
        selected application with the specified user.

        Args:
          username:
            A string with the username to authenticate. If not
            specified, the last used user will be selected.

        """
        self.application.authenticate(username)

    def run_function(self, function: str) -> None:
        """Runs a function in the chosen application.

        With the selected application and user run the function from the
        argument.

        Args:
          function:
            A string with the function identifier as defined in
            "_functions" variable.

        """
        if not hasattr(self, "functions"):
            logging.critical("No functions defined. Cannot continue.")
            sys.exit()
        self.functions.run(function, self.user, self.config)

    def fuzz_function(
        self,
        function_name: str,
        fuzzing_point: str,
        fuzzing_function: Callable[..., Any],
    ) -> None:
        """Fuzz a function with an authenticated user.

        Given a function name, a starting point for fuzzing, and a
        function to generate the fuzzing strings, run the attack.

        Args:
          function_name:
            The name of the :class:`Flow <raider.flow.Flow>` containing
            the :class:`Request <raider.request.Request>` which will be
            fuzzed.
          fuzzing_point:
            The name given to the :class:`Plugin
            <raider.plugins.Plugin>` inside :class:`Request
            <raider.request.Request>` which will be fuzzed.
          fuzzing_function:
            A callable function, that will be used to generate the
            strings that will be used for fuzzing. It should accept one
            argument, which will the value of the plugin before
            fuzzing. It can be used to build the list of strings to be
            used for the attack.

        """
        flow = self.functions.get_function_by_name(function_name)
        if flow:
            Fuzz(flow, fuzzing_point, fuzzing_function).attack_function(
                self.user, self.config
            )
        else:
            logging.critical(
                "Function %s not defined, cannot fuzz!", function_name
            )

    @property
    def authentication(self) -> Authentication:
        """Returns the Authentication object"""
        return self.application.authentication

    def fuzz_authentication(
        self,
        flow_name: str,
        fuzzing_point: str,
        fuzzing_function: Callable[..., Any],
    ) -> None:
        """Fuzz an authentication step.

        Given a flow name, a starting point for fuzzing, and a function
        to generate the fuzzing strings, run the attack. Unlike
        ``fuzz_function``, it takes into consideration the
        :class:`NextStage <raider.operations.NextStage>` operations,
        making it possible to start from the beginning of the
        authentication process if new tokens are needed.

        Args:
          flow_name:
            The name of the :class:`Flow <raider.flow.Flow>` containing
            the :class:`Request <raider.request.Request>` which will be
            fuzzed.
          fuzzing_point:
            The name given to the :class:`Plugin
            <raider.plugins.Plugin>` inside :class:`Request
            <raider.request.Request>` which will be fuzzed.
          fuzzing_function:
            A callable function, that will be used to generate the
            strings that will be used for fuzzing. It should accept one
            argument, which will the value of the plugin before
            fuzzing. It can be used to build the list of strings to be
            used for the attack.

        """
        flow = self.authentication.get_stage_by_name(flow_name)
        if flow:
            Fuzz(
                flow=flow,
                fuzzing_point=fuzzing_point,
                fuzzing_function=fuzzing_function,
                flags=Fuzz.IS_AUTHENTICATION,
            ).attack_authentication(
                self.authentication, self.user, self.config
            )
        else:
            logging.critical("Stage %s not defined, cannot fuzz!", flow_name)

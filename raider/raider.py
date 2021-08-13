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
from typing import Optional

from raider.application import Application
from raider.attacks import Fuzz
from raider.authentication import Authentication
from raider.config import Config
from raider.plugins.common import Plugin
from raider.user import User


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

    # Raider flags
    # Session was loaded and the information is already in userdata
    SESSION_LOADED = 0x01

    def __init__(self, project: Optional[str] = None, flags: int = 0) -> None:
        """Initializes the Raider object.

        Initializes the main entry point for Raider. If the name of the
        project is supplied, this application will be used, otherwise
        the last used application will be chosen.

        Args:
          project:
            A string with the name of the project.
          flags:
            An integer with the flags. Only SESSION_LOADED is supported
            now. It indicates the authentication was not performed from
            the start, but loaded from a previously saved session file,
            which means the plugins should get their value from userdata.

        """
        self.application = Application(project)
        if hasattr(self.application, "functions"):
            self.functions = self.application.functions

        self.flags = flags

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

    def load_session(self) -> None:
        """Loads saved session from ``_userdata.hy``."""
        self.application.load_session_file()
        self.flags = self.flags | self.SESSION_LOADED

    def save_session(self) -> None:
        """Saves session to ``_userdata.hy``."""
        self.application.write_session_file()

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

        if self.session_loaded:
            self.fix_function_plugins(function)

        self.functions.run(function, self.user, self.config)

    def fuzz(
        self,
        flow_name: str,
        fuzzing_point: str,
    ) -> Fuzz:
        """Fuzz a function with an authenticated user.

        Given a function name, a starting point for fuzzing, and a
        function to generate the fuzzing strings, run the attack.

        Args:
          flow_name:
            The name of the :class:`Flow <raider.flow.Flow>` containing
            the :class:`Request <raider.request.Request>` which will be
            fuzzed.
          fuzzing_point:
            The name given to the :class:`Plugin
            <raider.plugins.Plugin>` inside :class:`Request
            <raider.request.Request>` which will be fuzzed.

        """
        is_authentication = False
        flow = self.functions.get_function_by_name(flow_name)
        if not flow:
            flow = self.authentication.get_stage_by_name(flow_name)
            is_authentication = True
        if flow:
            if self.session_loaded:
                self.fix_function_plugins(flow_name)

            if is_authentication:
                fuzzer = Fuzz(
                    application=self.application,
                    flow=flow,
                    fuzzing_point=fuzzing_point,
                    flags=Fuzz.IS_AUTHENTICATION,
                )
            else:
                fuzzer = Fuzz(
                    application=self.application,
                    flow=flow,
                    fuzzing_point=fuzzing_point,
                    flags=0,
                )

        else:
            logging.critical(
                "Function %s not defined, cannot fuzz!", flow_name
            )
            sys.exit()

        return fuzzer

    def fix_function_plugins(self, function: str) -> None:
        """Given a function name, prepare its Flow to be fuzzed.

        For each plugin acting as an input for the defined function,
        change its flags and function so it uses the previously
        extracted data instead of extracting it again.

        """
        flow = self.functions.get_function_by_name(function)
        if not flow:
            logging.critical(
                "Function %s not found. Cannot continue.", function
            )
            sys.exit()

        inputs = flow.request.list_inputs()

        if inputs:
            for plugin in inputs.values():
                # Reset plugin flags, and get the values from userdata
                plugin.flags = Plugin.NEEDS_USERDATA
                plugin.function = plugin.extract_from_userdata

    @property
    def authentication(self) -> Authentication:
        """Returns the Authentication object"""
        return self.application.authentication

    @property
    def config(self) -> Config:
        """Returns the Configuration object"""
        return self.application.config

    @property
    def user(self) -> User:
        """Returns the User object"""
        return self.application.active_user

    @property
    def session_loaded(self) -> bool:
        """Returns True if the SESSION_LOADED flag is set."""
        return bool(self.flags & self.SESSION_LOADED)

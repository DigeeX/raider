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

"""Attacks to be run on Flows.
"""

import logging
import sys
from copy import deepcopy
from functools import partial
from typing import Callable, List, Optional

from raider.application import Application
from raider.flow import Flow
from raider.plugins.common import Plugin


class Fuzz:
    """Fuzz an input."""

    # Fuzzing flags
    IS_AUTHENTICATION = 0x01

    def __init__(
        self,
        application: Application,
        flow: Flow,
        fuzzing_point: str,
        flags: int = 0,
    ) -> None:
        """Initialize the Fuzz object.

        Given a :class:`Flow <raider.flow.Flow>`, a fuzzing point (in
        case of Raider this should be a :class:`Plugin
        <raider.plugins.Plugin>`), and a function, run the attack. The
        function is used to generate the strings to be used for
        fuzzing. The ``fuzzing_point`` attribute should contain the name
        of the plugin.

        Args:
          application:
            An :class:`Application <raider.application.Application>`
            object.
          flow:
            A :class:`Flow <raider.flow.Flow>` object which needs to be
            fuzzed.
          fuzzing_point:
            The name given to the :class:`Plugin
            <raider.plugins.Plugin>` which should be fuzzed.
          fuzzing_generator:
            A function which returns a Python generator, that will
            create the strings that will be used for fuzzing. The
            function should accept one argument. This will be the value
            of the plugin before fuzzing. It can be considered when
            building the fuzzing list, or ignored.

        """

        self.application = application
        self.flow = flow
        self.fuzzing_point = fuzzing_point
        self.flags = flags

        self.generator: Optional[Callable[..., List[str]]] = None
        self.processor: Callable[[str], str] = lambda value: value

    def run(self) -> None:
        """Runs the fuzzer."""
        if self.is_authentication:
            self.attack_authentication()
        else:
            self.attack_function()

    def set_input_file(
        self, filename: str, prepend: bool = False, append: bool = False
    ) -> None:
        """Sets the input file for the fuzzer.

        Uses the input file to generate fuzzing strings, and sets the
        generator function to return those values.

        """

        def fuzzing_generator(
            value: str, filename: str, prepend: bool, append: bool
        ) -> List[str]:
            """Generate a list of strings to use for fuzzing.

            Args:
              value:
                The original value of the field.
              filename:
                The filename with the inputs.
              prepend:
                A boolean flag meaning the original value will be
                prepended with the fuzzing string.
              append:
                A boolean flag meaning the original value will be
                appended with the fuzzing string.

            Returns:
              A list of final strings to be fuzzed.
            """
            fuzzstrings = []
            with open(filename) as contents:
                for item in contents.readlines():
                    if prepend:
                        fuzzstrings.append(item.strip() + value)
                    elif append:
                        fuzzstrings.append(value + item.strip())
                    else:
                        fuzzstrings.append(item.strip())

            return fuzzstrings

        self.generator = partial(
            fuzzing_generator,
            filename=filename,
            prepend=prepend,
            append=append,
        )

    def get_fuzzing_input(self, flow: Flow) -> Plugin:
        """Returns the Plugin associated with the fuzzing input.

        Args:
          flow:
            The flow object with the plugin to be returned.

        Returns:
          The plugin object to be fuzzed.
        """
        flow_inputs = flow.request.list_inputs()
        if flow_inputs:
            fuzzing_plugin = flow_inputs.get(self.fuzzing_point)
            if not fuzzing_plugin:
                logging.critical(
                    "Fuzzing point %s not found", self.fuzzing_point
                )
                sys.exit()
        else:
            logging.critical("Flow %s has no inputs", flow.name)
            sys.exit()

        return fuzzing_plugin

    def attack_function(self) -> None:
        """Attacks a flow defined in ``_functions``.

        Fuzz blindly the Flow object. It doesn't take into account the
        authentication process, so this function is useful for fuzzing
        stuff as an already authenticated user.

        Args:
          user:
            A :class:`User <raider.user.User>` object with the user
            specific information.
          config:
            A :class:`Config <raider.config.Config>` object with global
            **Raider** configuration.

        """
        user = self.application.active_user
        config = self.application.config
        flow = deepcopy(self.flow)
        fuzzing_plugin = self.get_fuzzing_input(flow)
        flow.get_plugin_values(user)

        # Reset plugin flags because it doesn't need userdata nor
        # the HTTP response anymore when fuzzing
        fuzzing_plugin.flags = 0

        if not self.generator:
            logging.critical(
                "Cannot run fuzzing without configuring the generator."
            )
            sys.exit()

        for item in self.generator(fuzzing_plugin.value):
            fuzzing_plugin.value = self.processor(item)
            fuzzing_plugin.function = fuzzing_plugin.return_value
            flow.execute(user, config)
            flow.run_operations()

    def attack_authentication(self) -> None:
        """Attacks a Flow defined in ``_authentication``.

        Unlike ``attack_function``, this will take into account the
        finite state machine defined in the hyfiles. This should be used
        when the authentication process can be altered by the fuzzing,
        for example if some token needs to be extracted again from a
        previous authentication step for fuzzing to work.

        It will first follow the authentication process until reaching
        the desired state, then it will try fuzzing it, and if a
        :class:`NextStage <raider.operations.NextStage>` operation is
        encountered, it will follow the instruction and move to this
        stage, then continue fuzzing.

        """
        authentication = self.application.authentication
        user = self.application.active_user
        config = self.application.config

        while authentication.current_stage_name != self.flow.name:
            authentication.run_current_stage(user, config)

        flow = deepcopy(self.flow)
        fuzzing_plugin = self.get_fuzzing_input(flow)

        # Reset plugin flags because it doesn't need userdata nor
        # the HTTP response anymore when fuzzing
        fuzzing_plugin.flags = 0

        if not self.generator:
            logging.critical(
                "Cannot run fuzzing without configuring the generator."
            )
            sys.exit()

        elements = self.generator(fuzzing_plugin.value)

        for item in elements:
            fuzzing_plugin.value = self.processor(item)
            fuzzing_plugin.function = fuzzing_plugin.return_value
            flow.execute(user, config)
            next_stage = flow.run_operations()
            if next_stage:
                while next_stage != flow.name:
                    if next_stage:
                        next_stage = authentication.run_stage(
                            next_stage, user, config
                        )
                    else:
                        logging.critical(
                            (
                                "Cannot reach the %s stage. ",
                                "Make sure you defined NextStage correctly.",
                            ),
                            flow.name,
                        )

    @property
    def is_authentication(self) -> bool:
        """Returns True if the IS_AUTHENTICATION flag is set."""
        return bool(self.flags & self.IS_AUTHENTICATION)

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
from typing import Callable, Iterator, Optional

from raider.authentication import Authentication
from raider.config import Config
from raider.flow import Flow
from raider.plugins import Plugin
from raider.user import User


class Fuzz:
    """Fuzz an input."""

    def __init__(
        self,
        flow: Flow,
        fuzzing_point: str,
        fuzzing_generator: Callable[[Optional[str]], Iterator[str]],
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

        self.flow = flow
        self.fuzzing_point = fuzzing_point
        self.fuzzing_generator = fuzzing_generator
        self.flags = flags

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

    def attack_function(self, user: User, config: Config) -> None:
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
        flow = deepcopy(self.flow)
        fuzzing_plugin = self.get_fuzzing_input(flow)
        flow.get_plugin_values(user)

        # Reset plugin flags because it doesn't need userdata nor
        # the HTTP response anymore when fuzzing
        fuzzing_plugin.flags = 0

        for item in self.fuzzing_generator(fuzzing_plugin.value):
            fuzzing_plugin.value = item
            fuzzing_plugin.function = fuzzing_plugin.return_value
            flow.execute(user, config)
            flow.run_operations()

    def attack_authentication(
        self, authentication: Authentication, user: User, config: Config
    ) -> None:
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

        Args:
          authentication:
            An :class:`Authentication
            <raider.authentication.Authentication>` object with the
            finite state machine definitions.
          user:
            A :class:`User <raider.user.User>` object with the user
            specific information.
          config:
            A :class:`Config <raider.config.Config>` object with global
            **Raider** configuration.

        """
        while authentication.current_stage_name != self.flow.name:
            authentication.run_current_stage(user, config)

        flow = deepcopy(self.flow)
        fuzzing_plugin = self.get_fuzzing_input(flow)

        # Reset plugin flags because it doesn't need userdata nor
        # the HTTP response anymore when fuzzing
        fuzzing_plugin.flags = 0

        elements = self.fuzzing_generator(fuzzing_plugin.value)

        for item in elements:
            fuzzing_plugin.value = item
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

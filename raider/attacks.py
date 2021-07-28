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
from typing import Callable, List

from raider.config import Config
from raider.flow import Flow
from raider.user import User


# pylint: disable=too-few-public-methods
class Fuzz:
    """Fuzz an input."""

    def __init__(
        self,
        flow: Flow,
        fuzzing_point: str,
        fuzzing_function: Callable[..., List[str]],
    ) -> None:
        """Initialize the Fuzz object.

        Given a :class:`Flow <raider.flow.Flow>`, a fuzzing point (in
        case of Raider this should be a :class:`Plugin
        <raider.plugins.Plugin>`), and a function, run the attack. The
        function is used to generate the strings to be used for
        fuzzing. The ``fuzzing_point`` attribute should contain the name
        of the plugin.

        Attributes:
          flow:
            A :class:`Flow <raider.flow.Flow>` object which needs to be
            fuzzed.
          fuzzing_point:
            The name given to the :class:`Plugin
            <raider.plugins.Plugin>` which should be fuzzed.
          fuzzing_function:
            A callable function, which will generate the strings that
            will be used for fuzzing.

        """
        self.flow = flow
        self.fuzzing_point = fuzzing_point
        self.fuzzing_function = fuzzing_function

    def attack(self, user: User, config: Config) -> None:
        """Runs the fuzzing attack.

        Given a user and a config object, runs the fuzzing attack in
        this context.

        Args:


        """
        flow = deepcopy(self.flow)
        flow_inputs = flow.request.list_inputs()
        if flow_inputs:
            fuzzing_plugin = flow_inputs.get(self.fuzzing_point)
            if not fuzzing_plugin:
                logging.critical(
                    "Fuzzing point %s not found", self.fuzzing_point
                )
                sys.exit()
        else:
            logging.critical("Flow %s has no inputs", self.flow.name)
            sys.exit()

        # Reset plugin flags because it doesn't need userdata nor
        # the HTTP response anymore when fuzzing
        fuzzing_plugin.flags = 0

        elements = self.fuzzing_function()

        for item in elements:
            fuzzing_plugin.function = lambda item=item: item
            flow.execute(user, config)

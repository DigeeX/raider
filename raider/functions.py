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

"""Functions class holding all Flows unrelated to authentication.
"""


import logging
import sys
from typing import List, Optional

from raider.config import Config
from raider.flow import Flow
from raider.user import User


class Functions:
    """Class holding all Flows that don't affect the authentication.

    This class shouldn't be used directly by the user, instead the
    Raider class should be used which will deal with Functions
    internally.

    Attributes:
      functions:
        A list of Flow objects with all available functions.

    """

    def __init__(self, functions: List[Flow]) -> None:
        """Initializes the Functions object.

        Args:
          functions:
            A list of Flow objects to be included in the Functions
            object.

        """
        self.functions = functions

    def get_function_by_name(self, name: str) -> Optional[Flow]:
        """Gets the function given its name.

        Tries to find the Flow object with the given name, and returns
        it if it's found, otherwise returns None.

        Args:
          name:
            A string with the unique identifier of the function as
            defined in the Flow.

        Returns:
          A Flow object associated with the name, or None if no such
          function has been found.

        """
        for function in self.functions:
            if function.name == name:
                return function
        return None

    def run(self, name: str, user: User, config: Config) -> None:
        """Runs a Function.

        Executes the given function, in the context of the specified
        user, and applies the global Raider configuration.

        Args:
          name:
            A string with the name of the function to run.
          user:
            A User object containing all the data needed to run the
            function in this user's context.
          config:
            A Config object with the global Raider configuration.

        """
        logging.info("Running function %s", name)
        function = self.get_function_by_name(name)
        if function:
            function.execute(user, config)
            if function.outputs:
                for item in function.outputs:
                    if item.value:
                        user.set_data(item)

            function.run_operations()

        else:
            logging.critical("Function %s not defined. Cannot continue", name)
            sys.exit()

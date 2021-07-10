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


import logging
import sys
from typing import Optional

from raider.config import Config
from raider.flow import Flow
from raider.user import User


class Functions:
    def __init__(self, functions: list[Flow]) -> None:
        self.functions = functions

    def get_function_by_name(self, name: str) -> Optional[Flow]:
        for function in self.functions:
            if function.name == name:
                return function
        return None

    def run(self, name: str, user: User, config: Config) -> None:
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

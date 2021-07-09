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

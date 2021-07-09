import logging
import os

import hy

from raider.authentication import Authentication
from raider.config import Config
from raider.functions import Functions
from raider.user import UserStore
from raider.utils import create_hy_expression, get_project_file


class Application:
    def __init__(self, name: str = None) -> None:
        self.config = Config()

        if name:
            self.config.active_project = name
            self.config.write_config_file()
            self.name = name
        else:
            self.name = self.config.active_project

        output = self.config.load_project(name)
        self.users = UserStore(output["_users"])
        active_user = output.get("_active_user")
        if active_user:
            self.active_user = self.users[active_user]
        else:
            self.active_user = self.users.active

        self.authentication = Authentication(output["_authentication"])
        functions = output.get("_functions")
        if functions:
            self.functions = Functions(functions)
        self.base_url = output["_base_url"]

    def authenticate(self, username: str = None) -> None:
        if username:
            self.active_user = self.users[username]
        self.authentication.run_all(self.active_user, self.config)
        self.write_project_file()

    def write_session_file(self) -> None:
        self.load_session_file()
        filename = get_project_file(self.name, "_userdata.hy")
        value = ""
        cookies = {}
        headers = {}
        data = {}
        with open(filename, "w") as sess_file:
            for username in self.users:
                user = self.users[username]
                cookies.update({username: user.cookies.to_dict()})
                headers.update({username: user.headers.to_dict()})
                data.update({username: user.data.to_dict()})

            value += create_hy_expression("_cookies", cookies)
            value += create_hy_expression("_headers", headers)
            value += create_hy_expression("_data", data)
            logging.debug("Writing to session file %s", filename)
            logging.debug("value = %s", str(value))
            sess_file.write(value)

    def load_session_file(self) -> None:
        filename = get_project_file(self.name, "_userdata.hy")
        logging.debug("Loading session file %s", filename)
        if not os.path.exists(filename):
            logging.critical("Configuration file doesn't exist")
        else:
            with open(filename) as sess_file:
                try:
                    while True:
                        expr = hy.read(sess_file)
                        if expr:
                            logging.debug(
                                "expr = %s", str(expr).replace("\n", " ")
                            )
                            hy.eval(expr)
                except EOFError:
                    logging.debug("Finished processing %s", filename)

    def write_project_file(self) -> None:
        filename = get_project_file(self.name, "_project.hy")
        value = ""
        with open(filename, "w") as proj_file:
            value += create_hy_expression(
                "_active_user", self.active_user.username
            )
            logging.debug("Writing to session file %s", filename)
            logging.debug("value = %s", str(value))
            proj_file.write(value)

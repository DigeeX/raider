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

"""Application class holding project configuration.
"""

import logging

from raider.authentication import Authentication
from raider.config import Config
from raider.functions import Functions
from raider.user import UserStore
from raider.utils import create_hy_expression, eval_file, get_project_file


class Application:
    """Class holding all the project related data.

    This class isn't supposed to be used directly by the user, instead
    the Raider class should be used, which will deal with the
    Application class internally.

    Attributes:
      name:
        A string with the name of the application.
      base_url:
        A string with the base URL of the application.
      config:
        A Config object with Raider global configuration plus the
        variables defined in hy configuration files related to the
        Application.
      users:
        A UserStore object generated from the "_users" variable set in
        the hy configuration files for the project.
      active_user:
        A User object pointing to the active user inside the "users"
        object.
      authentication:
        An Authentication object containing all the Flows relevant to
        the authentication process. It's created out of the
        "_authentication" variable from the hy configuration files.
      functions:
        A Functions object with all Flows that don't affect the
        authentication process. This object is being created out of the
        "_functions" variable from the hy configuration files.

    """

    def __init__(self, project: str = None) -> None:
        """Initializes the Application object.

        Sets up the environment necessary to test the specified
        application.

        Args:
          project:
            A string with the name of the application to be
            initialized. If not supplied, the last used application will
            be selected

        """
        self.config = Config()

        if project:
            self.config.active_project = project
            self.config.write_config_file()
            self.project = project
        else:
            self.project = self.config.active_project

        output = self.config.load_project(project)
        self.users = UserStore(output["_users"])
        active_user = output.get("_active_user")
        if active_user and active_user in self.users:
            self.active_user = self.users[active_user]
        else:
            self.active_user = self.users.active

        self.authentication = Authentication(output["_authentication"])
        functions = output.get("_functions")
        if functions:
            self.functions = Functions(functions)
        self.base_url = output.get("_base_url")

    def authenticate(self, username: str = None) -> None:
        """Authenticates the user.

        Runs all the steps of the authentication process defined in the
        hy config files for the application.

        Args:
          username:
            A string with the user to be authenticated. If not supplied,
            the last used username will be selected.

        """
        if username:
            self.active_user = self.users[username]
        self.authentication.run_all(self.active_user, self.config)
        self.write_project_file()

    def write_session_file(self) -> None:
        """Saves session data.

        Saves user related session data in a file for later use. This
        includes cookies, headers, and other data extracted using
        Plugins.

        """
        filename = get_project_file(self.project, "_userdata.hy")
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
        """Loads session data.

        If session data was saved with write_session_file() this
        function will load this data into existing :class:`User
        <raider.user.User>` objects.

        """
        filename = get_project_file(self.project, "_userdata.hy")
        output = eval_file(filename)
        cookies = output.get("_cookies")
        headers = output.get("_headers")
        data = output.get("_data")

        if cookies:
            for username in cookies:
                self.users[username].set_cookies_from_dict(cookies[username])

        if headers:
            for username in headers:
                self.users[username].set_headers_from_dict(headers[username])

        if data:
            for username in data:
                self.users[username].set_data_from_dict(data[username])

    def write_project_file(self) -> None:
        """Writes the project settings.

        For now only the active user is saved, so that the next time the
        project is used, there's no need to specify the user manually.

        """
        filename = get_project_file(self.project, "_project.hy")
        value = ""
        with open(filename, "w") as proj_file:
            value += create_hy_expression(
                "_active_user", self.active_user.username
            )
            logging.debug("Writing to session file %s", filename)
            logging.debug("value = %s", str(value))
            proj_file.write(value)

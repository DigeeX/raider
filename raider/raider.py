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

from typing import Optional

from raider.application import Application


class Raider:
    """Main class used as the point of entry.

    The Raider class should be used to access everything else inside
    Raider. For now it's still not doing much, but for the future this
    is where all of the features available to the end user should be.

    Attributes:
      application:
        An :class:`Application <Application>` object with the currently
        active project.
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
        self.functions.run(function, self.user, self.config)

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

from raider.application import Application


class Raider:
    """Main class used as the point of entry.

    The Raider class should be used to access everything else inside
    Raider. For now it's still not doing much, but for the future this
    is where all of the features available to the end user should be.

    Attributes:
      application:
        An Application object with the currently active project.
      config:
        A Config object containing all of the necessary settings.
      user:
        A User object containing the active user of the active project.
      functions:
        A Functions object containing the defined functions of the
        active project.

    """

    def __init__(self, name: str) -> None:
        self.application = Application(name)
        self.config = self.application.config
        self.user = self.application.active_user
        self.functions = self.application.functions

    def authenticate(self, username: str = None) -> None:
        self.application.authenticate(username)

    def run_function(self, function: str) -> None:
        self.functions.run(function, self.user, self.config)

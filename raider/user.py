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

"""Classes used for handling users.
"""


import hy

from raider.plugins import Cookie, Header, Plugin
from raider.structures import CookieStore, DataStore, HeaderStore
from raider.utils import hy_dict_to_python


class User:
    """Class holding user related information.

    User objects are created inside the UserStore. Each User object
    contains at least the username and the password. Every time a Plugin
    generates an output, it is saved in the User object. If the Plugin
    is a Cookie or a Header, the output will be stored in the the
    "cookies" and "headers" attributes respectively. Otherwise they'll
    be saved inside "data".

    Attributes:
      username:
        A string containing the user's email or username used to log in.
      password:
        A string containing the user's password.
      cookies:
        A CookieStore object containing all of the collected cookies for
        this user. The Cookie plugin only writes here.
      headers:
        A HeaderStore object containing all of the collected headers for
        this user. The Header plugin only writes here.
      data:
        A DataStore object containing the rest of the data collected
        from plugins for this user.

    """

    def __init__(
        self,
        username: str,
        password: str,
        **kwargs: dict[str, str],
    ) -> None:
        """Initializes a User object.

        Creates an object for easy access to user specific
        information. It's used to store the username, password, cookies,
        headers, and other data extracted from the Plugin objects.

        Args:
          username:
            A string with the username used for the login process.
          password:
            A string with the password used for the login process.
          **kwargs:
            A dictionary with additional data about the user.

        """

        self.username = username
        self.password = password

        self.cookies = CookieStore.from_dict(kwargs.get("cookies"))
        self.headers = HeaderStore.from_dict(kwargs.get("headers"))
        self.data = DataStore(kwargs.get("data"))

    def set_cookie(self, cookie: Cookie) -> None:
        """Sets the cookie for the user.

        Given a Cookie object, update the user's "cookies" attribute to
        include this cookie.

        Args:
          cookie:
            A Cookie Plugin object with the data to be added.

        """
        if cookie.value:
            self.cookies.set(cookie)

    def set_header(self, header: Header) -> None:
        """Sets the header for the user.

        Given a Header object, update the user's "headers" attribute to
        include this header.

        Args:
          header:
            A Header Plugin object with the data to be added.

        """
        if header.value:
            self.headers.set(header)

    def set_data(self, data: Plugin) -> None:
        """Sets the data for the user.

        Given a Plugin, update the user's data attribute to include this
        data.

        Args:
          data:
            A Plugin object with the data to be added.

        """
        if data.value:
            self.data.update({data.name: data.value})

    def to_dict(self) -> dict[str, str]:
        """Returns this object's data in a dictionary format."""
        data = {}
        data["username"] = self.username
        data["password"] = self.password
        data.update(self.cookies.to_dict())
        data.update(self.headers.to_dict())
        data.update(self.data.to_dict())
        return data


class UserStore(DataStore):
    """Class holding all the users of the Application.

    UserStore inherits from DataStore, and contains the users set up in
    the "_users" variable from the hy configuration file. Each user is
    an User object. The data from a UserStore object can be accessed
    same way like from the DataStore.

    If "_active_user" is set up in the configuration file, this will be
    the default user. Otherwise, the first user will be the active one.

    Attributes:
      active_user:
        A string with the currently active user.

    """

    def __init__(
        self, users: list[dict[hy.HyKeyword, str]], active_user: str = None
    ) -> None:
        """Initializes the UserStore object.

        Given a list of dictionaries, map them to a User object and
        store them in this UserStore object.

        Args:
          users:
            A list of dictionaries. Dictionary's data is mapped to a
            User object.
          active_user:
            An optional string specifying the active user to be set.

        """
        if active_user:
            self.active_user = active_user
        else:
            self.active_user = hy_dict_to_python(users[0])["username"]

        values = {}
        for item in users:
            userdata = hy_dict_to_python(item)
            username = userdata["username"]
            user = User(**userdata)
            values[username] = user

        super().__init__(values)

    def to_dict(self) -> dict[str, str]:
        """Returns the UserStore data in dictionary format."""
        data = {}
        for username in self:
            data[username] = self[username].to_dict()

        return data

    @property
    def active(self) -> User:
        """Returns the active user as an User object."""
        return self[self.active_user]

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

from typing import Union

import hy

from raider.plugins import Cookie, Header, Html, Json, Regex
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

        self.username = username
        self.password = password

        self.cookies = CookieStore.from_dict(kwargs.get("cookies"))
        self.headers = HeaderStore.from_dict(kwargs.get("headers"))
        self.data = DataStore(kwargs.get("data"))

    def set_cookie(self, cookie: Cookie) -> None:
        if cookie.value:
            self.cookies.set(cookie)

    def set_header(self, header: Header) -> None:
        if header.value:
            self.headers.set(header)

    def set_data(self, data: Union[Regex, Html, Json]) -> None:
        if data.value:
            self.data.update({data.name: data.value})

    def to_dict(self) -> dict[str, str]:
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
        data = {}
        for username in self:
            data[username] = self[username].to_dict()

        return data

    @property
    def active(self) -> User:
        return self[self.active_user]

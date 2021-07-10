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

from raider.cookies import Cookie, CookieStore
from raider.headers import Header, HeaderStore
from raider.modules import Html, Json, Regex
from raider.structures import DataStore
from raider.utils import hy_dict_to_python


class User:
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

    def set_cookies(self, cookie: Cookie) -> None:
        if cookie.value:
            self.cookies.update({cookie.name: cookie.value})

    def set_headers(self, header: Header) -> None:
        if header.value:
            self.headers.update({header.name: header.value})

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

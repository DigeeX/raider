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

"""Classes used for handling cookies.
"""

from typing import Optional

from raider.structures import DataStore


class Cookie:
    def __init__(self, name: str, value: str = None) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return str({self.name: self.value})


class CookieStore(DataStore):
    def __init__(self, data: Optional[list[Cookie]]) -> None:
        values = {}
        if data:
            for cookie in data:
                values[cookie.name] = cookie
        super().__init__(values)

    def to_dict(self) -> dict[str, str]:
        data = {}
        for key in self:
            data[key] = self[key].value
        return data

    def update(self, data: dict[str, str]) -> None:
        values = {}
        for key in data:
            values[key] = Cookie(key, data[key])

        super().update(values)

    @classmethod
    def from_dict(cls, data: Optional[dict[str, str]]) -> "CookieStore":
        cookielist = []
        if data:
            for name, value in data.items():
                cookie = Cookie(name, value)
                cookielist.append(cookie)
        return cls(cookielist)

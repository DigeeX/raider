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

"""Data structures used in Raider.
"""

from typing import Any, Iterator, Optional

from raider.plugins import Cookie, Header


class DataStore:
    """Class defining a dictionary-like data structure.

    This class was created to hold information relevant to Raider in a
    structure similar to Python dictionaries.

    """

    def __init__(self, data: Optional[dict[Any, Any]]) -> None:
        self._index = -1
        if data:
            self._store = data
        else:
            self._store = {}

    def __getitem__(self, key: Any) -> Any:
        if key in self._store:
            return self._store[key]
        return None

    def __setitem__(self, key: Any, value: Any) -> None:
        self._store.update({key: value})

    def __iter__(self) -> Iterator[Any]:
        for key in list(self._store):
            yield key

    def __next__(self) -> Any:
        self._index += 1
        if self._index >= len(self._store):
            self._index = -1
            raise StopIteration

        key = list(self._store)[self._index]
        return self._store[key]

    def update(self, data: dict[Any, Any]) -> None:
        self._store.update(data)

    def pop(self, name: Any) -> Any:
        return self._store.pop(name)

    def list_keys(self) -> list[Any]:
        return list(self._store)

    def list_values(self) -> list[Any]:
        data = []
        for key in self._store:
            data.append(self._store[key])
        return data

    def to_dict(self) -> dict[Any, Any]:
        return self._store


class HeaderStore(DataStore):
    """Class storing the HTTP headers.

    This class inherits from DataStore, and converts the values into
    Header objects.

    """

    def __init__(self, data: Optional[list[Header]]) -> None:
        values = {}
        if data:
            for header in data:
                values[header.name] = header
        super().__init__(values)

    def set(self, header: Header) -> None:
        super().update({header.name: header})

    @classmethod
    def from_dict(cls, data: Optional[dict[str, str]]) -> "HeaderStore":
        headerlist = []
        if data:
            for name, value in data.items():
                header = Header(name, value)
                headerlist.append(header)
        return cls(headerlist)


class CookieStore(DataStore):
    """Class storing the HTTP cookies.

    This class inherits from DataStore, and converts the values into
    Cookie objects.

    """

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

    def set(self, cookie: Cookie) -> None:
        super().update({cookie.name: cookie})

    @classmethod
    def from_dict(cls, data: Optional[dict[str, str]]) -> "CookieStore":
        cookielist = []
        if data:
            for name, value in data.items():
                cookie = Cookie(name, value)
                cookielist.append(cookie)
        return cls(cookielist)

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

from typing import Any, Dict, Iterator, List, Optional, Tuple

from raider.plugins.basic import Cookie, Header


class DataStore:
    """Class defining a dictionary-like data structure.

    This class was created to hold information relevant to Raider in a
    structure similar to Python dictionaries.

    """

    def __init__(self, data: Optional[Dict[Any, Any]]) -> None:
        """Initializes the DataStore object.

        Given a dictionary with the data, store them in this object.

        Args:
          data:
            A dictionary with Any elements to be stored.

        """
        self._index = -1
        if data:
            self._store = data
        else:
            self._store = {}

    def __getitem__(self, key: Any) -> Any:
        """Getter to return an element with the key."""
        if key in self._store:
            return self._store[key]
        return None

    def __setitem__(self, key: Any, value: Any) -> None:
        """Setter to add a new element to DataStore."""
        self._store.update({key: value})

    def __iter__(self) -> Iterator[Any]:
        """Iterator to yield the keys."""
        for key in list(self._store):
            yield key

    def __next__(self) -> Any:
        """Iterator to get the next element."""
        self._index += 1
        if self._index >= len(self._store):
            self._index = -1
            raise StopIteration

        key = list(self._store)[self._index]
        return self._store[key]

    def update(self, data: Dict[Any, Any]) -> None:
        """Updates the DataStore with a new element."""
        self._store.update(data)

    def pop(self, name: Any) -> Any:
        """Pops an element from the DataStore."""
        return self._store.pop(name)

    def list_keys(self) -> List[Any]:
        """Returns a list of the keys in the DataStore."""
        return list(self._store)

    def list_values(self) -> List[Any]:
        """Returns a list of the values in the DataStore."""
        data = []
        for key in self._store:
            data.append(self._store[key])
        return data

    def to_dict(self) -> Dict[Any, Any]:
        """Returns the DataStore elements as a dictionary."""
        return self._store

    def items(self) -> List[Tuple[Any, Any]]:
        """Returns a list of tuples containing the keys and values."""
        data = []
        for key in self._store:
            data.append((key, self._store[key]))

        return data


class HeaderStore(DataStore):
    """Class storing the HTTP headers.

    This class inherits from DataStore, and converts the values into
    Header objects.

    """

    def __init__(self, data: Optional[List[Header]]) -> None:
        """Initializes the HeaderStore object.

        Creates a HeaderStore object out of the given Header list.

        Args:
          data:
            A list of Header objects to store.

        """
        values = {}
        if data:
            for header in data:
                values[header.name.lower()] = header
        super().__init__(values)

    def set(self, header: Header) -> None:
        """Sets the value of a Header.

        Given a Header object, add or update its value in the
        HeaderStore.

        Args:
          header:
            A Header object to be added to the HeaderStore.

        """
        super().update({header.name.lower(): header.value})

    def merge(self, headerstore: "HeaderStore") -> None:
        """Merge HeaderStore object with another one."""
        for item in headerstore:
            self._store[item] = headerstore[item]

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, str]]) -> "HeaderStore":
        """Creates a HeaderStore object from a dictionary.

        Given a dictionary with header values, creates a HeaderStore
        object and returns it.

        Args:
          data:
            A dictionary with header values. Those will be mapped in
            Header objects.

        Returns:
          A HeaderStore object containing the headers created from the
          supplied dictionary.

        """
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

    def __init__(self, data: Optional[List[Cookie]]) -> None:
        """Initializes a CookieStore object.

        Given a list of Cookie objects, create the CookieStore
        containing them.

        Args:
          data:
            A list of Cookies to be added to the CookieStore.

        """
        values = {}
        if data:
            for cookie in data:
                values[cookie.name] = cookie
        super().__init__(values)

    def set(self, cookie: Cookie) -> None:
        """Sets the value of a Cookie.

        Given a Cookie object, add or update its value in the
        CookieStore.

        Args:
          cookie:
            A Cookie object to be added to the CookieStore

        """
        super().update({cookie.name: cookie.value})

    def merge(self, cookiestore: "CookieStore") -> None:
        """Merge CookieStore object with another one."""
        for item in cookiestore:
            self._store[item] = cookiestore[item]

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, str]]) -> "CookieStore":
        """Creates a CookieStore object from a dictionary.

        Given a dictionary with cookie values, creates a CookieStore
        object and returns it.

        Args:
          data:
            A dictionary with cookie values. Those will be mapped in
            Cookie objects.

        Returns:
          A CookieStore object containing the cookies created from the
          supplied dictionary.

        """
        cookielist = []
        if data:
            for name, value in data.items():
                cookie = Cookie(name, value)
                cookielist.append(cookie)
        return cls(cookielist)

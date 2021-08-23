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

"""Plugins used to parse data.
"""

from typing import Optional, Union
from urllib.parse import parse_qs, urlsplit

from raider.plugins.common import Parser, Plugin


class UrlParser(Parser):
    """Parse the URL and extract elements from it.

    Use this when needing to extract some piece of information from
    the URL.

    """

    def __init__(self, parent_plugin: Plugin, element: str) -> None:
        super().__init__(name=element, function=self.parse_url)
        self.plugins = [parent_plugin]
        self.element = element
        self.url: Optional[str] = None

    def parse_url(self) -> Optional[str]:
        """Parses the URL and returns the string with the desired element."""

        def get_query(query: Union[str, bytes], element: str) -> str:
            """Extracts a parameter from the URL query."""
            key = element.split(".")[1]
            return parse_qs(str(query))[key][0]

        value: Optional[str] = None

        self.url = self.plugins[0].value
        parsed_url = urlsplit(self.url)

        if self.element.startswith("query"):
            value = get_query(parsed_url.query, self.element)
        elif self.element.startswith("netloc"):
            value = str(parsed_url.netloc)
        elif self.element.startswith("path"):
            value = str(parsed_url.path)
        elif self.element.startswith("scheme"):
            value = str(parsed_url.scheme)
        elif self.element.startswith("fragment"):
            value = str(parsed_url.fragment)

        if value:
            return str(value)
        return None

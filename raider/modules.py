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

"""Module elements used as inputs/outputs in Flows
"""

import json
import logging
import re
from typing import Any, Optional

import bs4
import hy

from raider.utils import hy_dict_to_python


def match_tag(html_tag: bs4.element.Tag, attributes: dict[str, str]) -> bool:
    for key, value in attributes.items():
        if not (key in html_tag.attrs) or not (
            re.match(value, html_tag.attrs[key])
        ):
            return False
    return True


class Variable:
    def __init__(self, name: str) -> None:
        self.name = name
        self.value: Optional[str] = None

    def get_value(self, data: dict[str, Any]) -> Optional[str]:
        self.value = data[self.name]
        return self.value


class Prompt:
    def __init__(self, prompt: str) -> None:
        self.prompt = prompt
        self.value: Optional[str] = None

    def get_value(self) -> str:
        print("Please provide the input value")
        self.value = input(self.prompt + " = ")
        return self.value


class Regex:
    def __init__(self, name: str, regex: str, extract: int = 0) -> None:
        self.name = name
        self.regex = regex
        self.extract = extract
        self.value: Optional[str] = None

    def get_value(self, text: str) -> Optional[str]:
        matches = re.search(self.regex, text)
        if matches:
            groups = matches.groups()
            self.value = groups[self.extract]
            logging.debug("Regex filter %s: %s", self.name, str(self.value))
        else:
            logging.warning(
                "Regex filter %s not found in the response body", self.name
            )

        return self.value

    def __str__(self) -> str:
        return "Regex:" + self.regex + ":" + str(self.extract)


class Html:
    def __init__(
        self,
        name: str,
        tag: str,
        attributes: dict[hy.HyKeyword, str],
        extract: str,
    ) -> None:

        self.name = name
        self.tag = tag
        self.attributes = hy_dict_to_python(attributes)
        self.extract = extract
        self.value: Optional[str] = None

    def get_value(self, text: str) -> Optional[str]:
        soup = bs4.BeautifulSoup(text, "html.parser")
        matches = soup.find_all(self.tag)

        for item in matches:
            if match_tag(item, self.attributes):
                self.value = item.attrs.get(self.extract)

        logging.debug("Html filter %s: %s", self.name, str(self.value))
        return self.value

    def __str__(self) -> str:
        return (
            "Html:"
            + self.tag
            + ":"
            + str(self.attributes)
            + ":"
            + str(self.extract)
        )


class Json:
    def __init__(self, name: str, extract: str) -> None:
        self.name = name
        self.extract = extract
        self.value: Optional[str] = None

    def get_value(self, text: str) -> Optional[str]:
        parsed = json.loads(text)

        items = self.extract.split(".")
        temp = parsed
        for item in items:
            temp = temp[item]

        self.value = temp
        logging.debug("Json filter %s: %s", self.name, str(self.value))
        return self.value

    def __str__(self) -> str:
        return "Json:" + str(self.extract)

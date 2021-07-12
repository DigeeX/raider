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


"""Request class used to handle HTTP.
"""

import logging
import sys
from typing import Any, Optional, Union
from urllib import parse

import requests
from urllib3.exceptions import InsecureRequestWarning

from raider.config import Config
from raider.plugins import Cookie, Header, Html, Json, Prompt, Regex, Variable
from raider.structures import CookieStore, DataStore, HeaderStore
from raider.user import User


def get_module_value(
    item: Union[Variable, Prompt, Regex, Html, Json], data: dict[str, str]
) -> Optional[str]:

    if isinstance(item, Variable):
        value = item.get_value(data)
    elif isinstance(item, Prompt):
        value = item.get_value()
    elif isinstance(item, (Regex, Html, Json)):
        value = data[item.name]

    return value


# pylint: disable=too-many-arguments
class Request:
    """Class holding the elements of the HTTP request.

    When a Flow object is created, it defines a Request object with the
    information necessary to create a HTTP request. The "method"
    attribute is required. One and only one of "url" and "path" is
    required too. Everything else is optional.

    The Request object can contain Plugins which will be evaluated and
    its value replaced in the HTTP request.

    Attributes:
      method:
        A string with the HTTP request method. Only GET and POST is
        supported for now.
      url:
        A string with the URL of the HTTP request. Cannot be used if
        "path" is used.
      path:
        A string with the path of the HTTP request. The base URL is
        defined in the "_base_url" variable from the hy configuration
        files of the project. If "path" is defined "url" cannot be used.
      cookies:
        A list of Cookie objects to be sent with the HTTP request.
      headers:
        A list of Header objects to be sent with the HTTP request.
      data:
        A dictionary of Any objects. Can contain strings and
        Plugins. When a key or a value of the dictionary is a Plugin, it
        will be evaluated and its value will be used in the HTTP
        request. If the "method" is GET those values will be put inside
        the URL parameters, and if the "method" is POST they will be
        inside the POST request body.

    """

    def __init__(
        self,
        method: str,
        url: str = None,
        path: str = None,
        cookies: list[Cookie] = None,
        headers: list[Header] = None,
        data: dict[Any, Any] = None,
    ) -> None:

        self.method = method
        if not self.method:
            logging.critical("Required :method parameter, can't run without")

        if not bool(url) ^ bool(path):
            logging.critical(
                "One and only one of :path and :url parameters required"
            )
            sys.exit()

        self.url = url
        self.path = path

        self.headers = HeaderStore(headers)
        self.cookies = CookieStore(cookies)
        self.data = DataStore(data)

    def process_inputs(
        self, user: User, config: Config
    ) -> dict[str, dict[str, str]]:
        userdata = user.to_dict()

        cookies = self.cookies.to_dict().copy()
        headers = self.headers.to_dict().copy()
        httpdata = self.data.to_dict().copy()

        if self.path:
            base_url = config.project_config["_base_url"]
            self.url = parse.urljoin(base_url, self.path)

        headers.update({"User-agent": config.user_agent})

        for key in self.cookies:
            if self.cookies[key].value:
                cookies.update({key: userdata[key]})
            else:
                cookies.pop(key)

        for key in self.headers:
            value = self.headers[key].get_value()
            headers.update({key: value})
            # elif isinstance(self.headers[key], Bearerauth):
            #     self.headers[key].load_token()
            #     value = self.headers[key].value
            #     headers.update({key: value})
            # else:
            #     headers.update({key: userdata[key]})

        for key in list(httpdata):
            value = httpdata[key]
            if type(value) in [Variable, Prompt, Regex, Html, Json]:
                value = get_module_value(value, userdata)
                httpdata.update({key: value})

            if type(key) in [Variable, Prompt, Regex, Html, Json]:
                httpdata.pop(key)
                new_key = get_module_value(key, userdata)
                if new_key:
                    httpdata.update({new_key: value})

        return {"cookies": cookies, "data": httpdata, "headers": headers}

    def send(
        self, user: User, config: Config
    ) -> Optional[requests.models.Response]:
        verify = config.verify
        if not verify:
            # pylint: disable=no-member
            requests.packages.urllib3.disable_warnings(
                category=InsecureRequestWarning
            )

        proxies = {"all": config.proxy}

        inputs = self.process_inputs(user, config)
        cookies = inputs["cookies"]
        headers = inputs["headers"]
        data = inputs["data"]

        logging.debug("Sending HTTP request:")
        logging.debug("%s %s", self.method, self.url)
        logging.debug("Cookies: %s", str(cookies))
        logging.debug("Headers: %s", str(headers))
        logging.debug("Data: %s", str(data))

        if self.method == "GET":
            req = requests.get(
                self.url,
                params=data,
                headers=headers,
                cookies=cookies,
                proxies=proxies,
                verify=verify,
                allow_redirects=False,
            )

            return req

        if self.method == "POST":
            req = requests.post(
                self.url,
                data=data,
                headers=headers,
                cookies=cookies,
                proxies=proxies,
                verify=verify,
                allow_redirects=False,
            )

            return req

        logging.critical("Method %s not allowed", self.method)
        sys.exit()
        return None

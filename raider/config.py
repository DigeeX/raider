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

"""Config class holding global Raider configuration.
"""

import logging
import os
import sys
from typing import Any

from raider.utils import (
    create_hy_expression,
    default_user_agent,
    eval_file,
    eval_project_file,
    get_config_file,
    get_project_dir,
    list_apps,
)


class Config:
    """Class dealing with global Raider configuration.

    A Config object will contain all the information necessary to run
    Raider. It will define global configurations like the web proxy and
    the logging level, but also the data defined in the active project
    configuration files.

    Attributes:
      proxy:
        An optional string to define the web proxy to relay the traffic
        through.
      verify:
        A boolean flag which will let the requests library know whether
        to check the SSL certificate or ignore it.
      loglevel:
        A string used by the logging library to define the desired
        logging level.
      user_agent:
        A string which will be used as the user agent in HTTP requests.
      active_project:
        A string defining the current active project.
      project_config:
        A dictionary containing all of the local variables defined in
        the active project's hy configuration files.
      logger:
        A logging.RootLogger object used for debugging.

    """

    def __init__(self) -> None:
        filename = get_config_file("common.hy")
        if os.path.isfile(filename):
            output = eval_file(filename)
        else:
            output = {}

        self.proxy = output.get("proxy", None)
        self.verify = output.get("verify", False)
        self.loglevel = output.get("loglevel", "WARNING")
        self.user_agent = output.get("user_agent", default_user_agent())
        self.active_project = output.get("active_project", None)
        self.project_config: dict[str, Any] = {}

        self.logger = logging.getLogger()
        self.logger.setLevel(self.loglevel)

        if not list_apps():
            self.logger.critical(
                "No application have been configured. Cannot run."
            )
            sys.exit()

    def load_project(self, project: str = None) -> dict[str, Any]:
        if not project:
            active_project = self.active_project
        else:
            active_project = project

        hyfiles = sorted(os.listdir(get_project_dir(active_project)))
        shared_locals: dict[str, Any]
        shared_locals = {}
        for confile in hyfiles:
            if confile.endswith(".hy"):
                shared_locals.update(
                    eval_project_file(active_project, confile, shared_locals)
                )
        self.project_config = shared_locals
        return shared_locals

    def write_config_file(self) -> None:
        filename = get_config_file("common.hy")
        data = ""
        with open(filename, "w") as conf_file:
            data += create_hy_expression("proxy", self.proxy)
            data += create_hy_expression("user_agent", self.user_agent)
            data += create_hy_expression("loglevel", self.loglevel)
            data += create_hy_expression("verify", self.verify)
            data += create_hy_expression("active_project", self.active_project)
            self.logger.debug("Writing to config file %s", filename)
            self.logger.debug("data = %s", str(data))
            conf_file.write(data)

    def print_config(self) -> None:
        print("proxy: " + self.proxy)
        print("verify: " + str(self.verify))
        print("loglevel: " + self.loglevel)
        print("user_agent: " + self.user_agent)
        print("active_project: " + self.active_project)

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

"""Functions that are used within Raider.
"""

import logging
import os
from typing import Any, Union

import hy

from raider.__version__ import __version__


def default_user_agent() -> str:
    return "digeex_raider/" + __version__


def get_config_dir() -> str:
    confdir = os.path.expanduser("~/.config")
    raider_conf = os.path.join(confdir, "raider")
    os.makedirs(raider_conf, exist_ok=True)
    return raider_conf


def get_config_file(filename: str) -> str:
    dir_path = get_config_dir()
    file_path = os.path.join(dir_path, filename)
    return file_path


def get_project_dir(project_name: str) -> str:
    dir_path = get_config_dir()
    file_path = os.path.join(dir_path, "apps", project_name)
    return file_path


def get_project_file(project_name: str, filename: str) -> str:
    app_path = get_project_dir(project_name)
    file_path = os.path.join(app_path, filename)
    return file_path


def import_raider_objects() -> dict[str, Any]:
    hy_imports = {
        "modules": "Variable Prompt Regex Html Json",
        "cookies": "Cookie",
        "headers": "Header Basicauth Bearerauth",
        "flow": "Flow",
        "request": "Request",
        "operations": "Http Grep Print Error NextStage",
    }

    for module, classes in hy_imports.items():
        expr = hy.read_str(
            "(import [raider." + module + " [" + classes + "]])"
        )
        logging.debug("expr = %s", str(expr).replace("\n", " "))
        hy.eval(expr)

    return locals()


def hy_dict_to_python(hy_dict: dict[hy.HyKeyword, Any]) -> dict[str, Any]:
    data = {}
    for hy_key in hy_dict:
        key = hy_key.name
        data.update({key: hy_dict[hy_key]})

    return data


def py_dict_to_hy_list(
    data: dict[str, Any]
) -> list[Union[hy.HyString, hy.HyDict, hy.HySymbol]]:

    value = []
    for key in data:
        if isinstance(key, str):
            value.append(hy.HyString(key))
            if isinstance(data[key], dict):
                value.append(hy.HyDict(py_dict_to_hy_list(data[key])))
            elif isinstance(data[key], str):
                value.append(hy.HyString(data[key]))
            else:
                value.append(hy.HySymbol(data[key]))

    return value


def create_hy_expression(
    variable: str, value: Union[str, dict[Any, Any], list[Any]]
) -> str:
    data = []
    data.append(hy.HySymbol("setv"))
    data.append(hy.HySymbol(variable))

    if isinstance(value, dict):
        data.append(hy.HyDict(py_dict_to_hy_list(value)))
    elif isinstance(value, list):
        data.append(hy.HyList(value))
    elif isinstance(value, str):
        data.append(hy.HyString(value))
    else:
        data.append(hy.HySymbol(value))

    return serialize_hy(hy.HyExpression(data)) + "\n"


def serialize_hy(
    form: Union[
        hy.models.HyExpression,
        hy.models.HyDict,
        hy.models.HyList,
        hy.models.HySymbol,
        hy.models.HyInteger,
        hy.models.HyKeyword,
        hy.models.HyString,
    ]
) -> str:

    if isinstance(form, hy.models.HyExpression):
        hystring = "(" + " ".join([serialize_hy(x) for x in form]) + ")"
    elif isinstance(form, hy.models.HyDict):
        hystring = "{" + " ".join([serialize_hy(x) for x in form]) + "}"
    elif isinstance(form, hy.models.HyList):
        hystring = "[" + " ".join([serialize_hy(x) for x in form]) + "]"
    elif isinstance(form, hy.models.HySymbol):
        hystring = "{}".format(form)
    elif isinstance(form, hy.models.HyInteger):
        hystring = "{}".format(int(form))
    elif isinstance(form, hy.models.HyKeyword):
        hystring = "{}".format(form.name)
    elif isinstance(form, hy.models.HyString):
        hystring = '"{}"'.format(form)
    else:
        hystring = "{}".format(form)

    return hystring


def eval_file(
    filename: str, shared_locals: dict[str, Any] = None
) -> dict[str, Any]:

    if shared_locals:
        locals().update(shared_locals)

    logging.debug("Loading %s", filename)
    with open(filename) as hyfile:
        try:
            while True:
                expr = hy.read(hyfile)
                if expr:
                    logging.debug("expr = %s", str(expr).replace("\n", " "))
                    hy.eval(expr)
        except EOFError:
            logging.debug("Finished processing %s", filename)

    return locals()


def eval_project_file(
    project: str, filename: str, shared_locals: dict[str, Any]
) -> dict[str, Any]:

    raider_objects = import_raider_objects()
    locals().update(raider_objects)
    if shared_locals:
        locals().update(shared_locals)

    file_path = get_project_file(project, filename)
    shared_locals = eval_file(file_path, locals())
    return shared_locals


def list_apps() -> list[str]:
    apps = []
    appdir = os.path.join(get_config_dir(), "apps")
    os.makedirs(appdir, exist_ok=True)
    for filename in os.listdir(appdir):
        if not filename[0] == "_":
            apps.append(filename)
    return apps

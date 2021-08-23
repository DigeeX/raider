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
import re
import sys
from typing import Any, Dict, List, Union

import bs4
import hy

from raider.__version__ import __version__


def default_user_agent() -> str:
    """Gets the default user agent.

    Gets the current version of Raider and creates the user agent
    string.

    Returns:
      A string with the user agent.

    """
    return "digeex_raider/" + __version__


def get_config_dir() -> str:
    """Gets the configuration directory.

    Returns the path of the directory with the Raider configuration
    files.

    Returns:
      A string with the path of the configuration directory.

    """
    confdir = os.path.expanduser("~/.config")
    raider_conf = os.path.join(confdir, "raider")
    os.makedirs(raider_conf, exist_ok=True)
    return raider_conf


def get_config_file(filename: str) -> str:
    """Gets the configuration file.

    Given the file name, it returns the path of this file in the Raider
    configuration directory.

    Args:
      filename:
        A string with the name of the file to look up for in the main
        configuration directory.

    Returns:
      A string with the path of the file.

    """
    confdir = get_config_dir()
    file_path = os.path.join(confdir, filename)
    return file_path


def get_project_dir(project: str) -> str:
    """Gets the directory of the project.

    Given the name of the project, returns the path to the directory
    containing the configuration files for this project.

    Args:
      project:
        A string with the name of the project.

    Returns:
      A string with the path of the directory where the config files for
      the project are located.

    """
    confdir = get_config_dir()
    project_conf = os.path.join(confdir, "projects", project)
    return project_conf


def get_project_file(project: str, filename: str) -> str:
    """Gets a file from a project.

    Given the project name and the file name, it returns the path to
    that file.

    Args:
      project:
        A string with the name of the project.
      filename:
        A string with the file name.

    Returns:
      The path of the file in the project directory.

    """
    project_conf = get_project_dir(project)
    file_path = os.path.join(project_conf, filename)
    return file_path


def import_raider_objects() -> Dict[str, Any]:
    """Imports Raider objects to use inside hy configuration files.

    To make Raider objects visible inside hy files without using
    separate imports, this function does the imports and returns the
    locals() which is later used when evaluating hy files.

    Returns:
       A dictionary with the locals() containing all the Raider objects
       that can be used in hy files.

    """
    hy_imports = {
        "plugins.common": ("Empty " "Plugin " "Parser "),
        "plugins.basic": (
            "Regex "
            "Html "
            "Json "
            "Variable "
            "Command "
            "Prompt "
            "Cookie "
            "Header "
        ),
        "plugins.modifiers": ("Alter " "Combine "),
        "plugins.parsers": ("Parser " "UrlParser "),
        "flow": "Flow",
        "request": "Request PostBody Template",
        "operations": (
            "Http " "Grep " "Print " "Error " "NextStage " "Operation " "Save "
        ),
    }

    for module, classes in hy_imports.items():
        expr = hy.read_str(
            "(import [raider." + module + " [" + classes + "]])"
        )
        logging.debug("expr = %s", str(expr).replace("\n", " "))
        hy.eval(expr)

    return locals()


def hy_dict_to_python(hy_dict: Dict[hy.HyKeyword, Any]) -> Dict[str, Any]:
    """Converts a hy dictionary to a python dictionary.

    When creating dictionaries in hylang using :parameters they become
    hy.HyKeyword objects. This function converts them to normal python
    dictionaries.

    Args:
      hy_dict:
        A dictionary created in hy, which uses hy.HyKeyword instead of
        simple strings as keys.

    Returns:
      A dictionary with the same elements only with hy.HyKeyword keys
      converted into normal strings.

    """
    data = {}
    for hy_key in hy_dict:
        key = hy_key.name
        data.update({key: hy_dict[hy_key]})

    return data


def py_dict_to_hy_list(
    data: Dict[str, Any]
) -> List[Union[hy.HyString, hy.HyDict, hy.HySymbol]]:
    """Converts a python dictionary to a hylang list.

    In hy, dictionaries are created out of lists, and this function
    converts a normal python dictionary to a list made out of hy symbols
    that will be later used to create the hy dictionary.

    Args:
      data:
        A python dictionary with the data to convert.

    Returns:
      A list with hy objects that can be used to create a hy dictionary.

    """
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
    variable: str, value: Union[str, Dict[Any, Any], List[Any]]
) -> str:
    """Creates a hy expression.

    Raider configuration is saved in hy format, and this function
    creates the assignments in this format.

    Args:
      variable:
        A string with the name of the variable to be created.
      value:
        The value of the variable.

    Returns:
      A string with the valid hy expression.
    """
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
    """Serializes hy expression.

    This function serializes the supplied hy expression and returns it
    in a string format, so that it can be later saved in a file.

    Args:
      form:
        A hy expression to convert to a string.

    Returns:
      A string with the serialized form.

    """
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
    filename: str, shared_locals: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Evaluate hy file.

    This function evaluates all the content inside the supplied hy file,
    and returns the created locals() so that it can be later used for
    other files.

    Args:
      filename:
        A string with the file name to be evaluated.
      shared_locals:
        A dictionary with the locals() that will be considered when
        evaluating the file.

    Returns:
      A dictionary with the updated locals() after evaluating the hy
      file.

    """
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
    project: str, filename: str, shared_locals: Dict[str, Any]
) -> Dict[str, Any]:
    """Evaluate a hy file from a project.

    This function evaluates the specified file inside the project and
    returns the locals() which are updated after evaluating the file.

    Args:
      project:
        A string with the name of the project.
      filename:
        A string with the file name to be evaluated.
      shared_locals:
        A dictionary of locals() to be included when evaluating the
        file.

    Returns:
      A dictionary of locals() updated after evaluating the file.

    """
    raider_objects = import_raider_objects()
    locals().update(raider_objects)
    if shared_locals:
        locals().update(shared_locals)

    file_path = get_project_file(project, filename)
    shared_locals = eval_file(file_path, locals())
    return shared_locals


def list_projects() -> List[str]:
    """List existing projects.

    This function returns the list of projects that have been
    configured in Raider.

    Returns:
      A list with the strings of the project found in the
      configuration directory.

    """
    projects = []
    projectdir = os.path.join(get_config_dir(), "projects")
    os.makedirs(projectdir, exist_ok=True)
    for filename in os.listdir(projectdir):
        if not filename[0] == "_":
            projects.append(filename)
    return projects


def match_tag(html_tag: bs4.element.Tag, attributes: Dict[str, str]) -> bool:
    """Tells if a tag matches the search.

    This function checks whether the supplied tag matches the
    attributes. The attributes is a dictionary, and the values are
    treated as a regular expression, to allow checking for tags that
    don't have a static value.

    Args:
      html_tag:
        A bs4.element.Tag object with the tag to be checked.
      attributes:
        A dictionary of attributes to check whether they match with the tag.

    Returns:
      A boolean saying whether the tag matched with the attributes or not.

    """
    for key, value in attributes.items():
        if not (key in html_tag.attrs) or not (
            re.match(value, html_tag.attrs[key])
        ):
            return False
    return True


def parse_json_filter(raw: str) -> List[str]:
    """Parses a raw JSON filter and returns a list with the items.

    Args:
      raw:
        A string with the expected JSON filter.

    Returns:
      A list with all items found in the filter.
    """
    splitted = raw.split(".")

    parsed_filter = []
    for item in splitted:
        parsed_item = []
        open_delim_index = item.find("[")

        if open_delim_index != -1:
            if open_delim_index == 0:
                logging.critical(
                    (
                        "Syntax error. '.' should be followed by a key,",
                        "not an array index.",
                    )
                )
                sys.exit()
            parsed_item.append(item[:open_delim_index].strip('"'))
            array_indices = item[open_delim_index:]
            open_delim_index = 0

            while array_indices:
                close_delim_index = array_indices.find(
                    "]", open_delim_index + 1
                )
                if close_delim_index == -1:
                    logging.critical("Syntax error. Closing ']' not found.")
                    sys.exit()

                index = array_indices[open_delim_index + 1 : close_delim_index]
                if index.isdecimal():
                    parsed_item.append("[" + index + "]")
                    array_indices = array_indices[close_delim_index + 1 :]
                else:
                    logging.critical(
                        (
                            "Syntax error.",
                            "The index between '[' and '] is not a decimal.",
                        )
                    )
                    sys.exit()
        else:
            parsed_item.append(item.strip('"'))

        parsed_filter += parsed_item

    return parsed_filter

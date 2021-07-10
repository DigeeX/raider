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

"""Authentication class responsible for running the defined stages.
"""

import logging
import sys
from typing import Optional, Union

from raider.config import Config
from raider.cookies import Cookie
from raider.flow import Flow
from raider.headers import Header
from raider.modules import Html, Json, Regex
from raider.user import User


class Authentication:
    def __init__(self, stages: list[Flow]) -> None:
        self.stages = stages
        self._current_stage = 0

    def get_stage_by_name(self, name: str) -> Optional[Flow]:
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None

    def get_stage_name_by_id(self, stage_id: int) -> str:
        return self.stages[stage_id].name

    def get_stage_index(self, name: str) -> int:
        if not name:
            return -1
        for stage in self.stages:
            if stage.name == name:
                return self.stages.index(stage)

        return -1

    def run_all(self, user: User, config: Config) -> None:
        while self._current_stage >= 0:
            logging.info(
                "Running stage %s",
                self.get_stage_name_by_id(self._current_stage),
            )
            self.run_current_stage(user, config)

    def run_current_stage(self, user: User, config: Config) -> None:
        self.run_stage(self._current_stage, user, config)

    def run_stage(
        self, stage_id: Union[int, str], user: User, config: Config
    ) -> Optional[str]:

        stage: Optional[Flow]
        if isinstance(stage_id, int):
            stage = self.stages[stage_id]
        elif isinstance(stage_id, str):
            stage = self.get_stage_by_name(stage_id)

        if not stage:
            logging.critical("Stage %s not defined. Cannot continue", stage_id)
            sys.exit()

        stage.execute(user, config)

        if stage.outputs:
            for item in stage.outputs:
                if isinstance(item, Cookie):
                    user.set_cookies(item)
                if isinstance(item, Header):
                    user.set_headers(item)
                elif type(item) in [Regex, Html, Json]:
                    user.set_data(item)

        next_stage = stage.run_operations()
        if next_stage:
            self._current_stage = self.get_stage_index(next_stage)
        else:
            self._current_stage = -1
        return next_stage

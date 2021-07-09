from base64 import b64encode
from typing import Any, Optional, Union

from raider.modules import Html, Json, Regex
from raider.structures import DataStore


class Header:
    def __init__(self, name: str, value: str = None) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return str({self.name: self.value})


class Bearerauth(Header):
    def __init__(self, access_token: Union[Html, Json, Regex]) -> None:
        self.access_token = access_token
        super().__init__("Authorization", "Bearer ")

    def load_token(self) -> None:
        if self.access_token.value:
            super().__init__(
                "Authorization", "Bearer " + self.access_token.value
            )


class Basicauth(Header):
    def __init__(self, username: str, password: str) -> None:
        temp = ":".join([username, password]).encode("utf-8")
        encoded = b64encode(temp)
        super().__init__("Authorization", "Basic " + encoded.decode("utf-8"))


class HeaderStore(DataStore):
    def __init__(self, data: Optional[list[Header]]) -> None:
        values = {}
        if data:
            for header in data:
                values[header.name] = header
        super().__init__(values)

    def update(self, data: dict[str, Any]) -> None:
        values = {}
        for key in data:
            values[key] = Header(key, data[key])

        super().update(values)

    @classmethod
    def from_dict(cls, data: Optional[dict[str, str]]) -> "HeaderStore":
        headerlist = []
        if data:
            for name, value in data.items():
                header = Header(name, value)
                headerlist.append(header)
        return cls(headerlist)

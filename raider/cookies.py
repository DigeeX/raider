from typing import Optional

from raider.structures import DataStore


class Cookie:
    def __init__(self, name: str, value: str = None) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return str({self.name: self.value})


class CookieStore(DataStore):
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

    def update(self, data: dict[str, str]) -> None:
        values = {}
        for key in data:
            values[key] = Cookie(key, data[key])

        super().update(values)

    @classmethod
    def from_dict(cls, data: Optional[dict[str, str]]) -> "CookieStore":
        cookielist = []
        if data:
            for name, value in data.items():
                cookie = Cookie(name, value)
                cookielist.append(cookie)
        return cls(cookielist)

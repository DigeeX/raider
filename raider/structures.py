from typing import Any, Iterator, Optional


class DataStore:
    def __init__(self, data: Optional[dict[Any, Any]]) -> None:
        self._index = -1
        if data:
            self._store = data
        else:
            self._store = {}

    def __getitem__(self, key: Any) -> Any:
        if key in self._store:
            return self._store[key]
        return None

    def __setitem__(self, key: Any, value: Any) -> None:
        self._store.update({key: value})

    def __iter__(self) -> Iterator[Any]:
        for key in list(self._store):
            yield key

    def __next__(self) -> Any:
        self._index += 1
        if self._index >= len(self._store):
            self._index = -1
            raise StopIteration

        key = list(self._store)[self._index]
        return self._store[key]

    def update(self, data: dict[Any, Any]) -> None:
        self._store.update(data)

    def pop(self, name: Any) -> Any:
        return self._store.pop(name)

    def list_keys(self) -> list[Any]:
        return list(self._store)

    def list_values(self) -> list[Any]:
        data = []
        for key in self._store:
            data.append(self._store[key])
        return data

    def to_dict(self) -> dict[Any, Any]:
        return self._store

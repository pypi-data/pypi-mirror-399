from typing import Any


class ItemNotStoredError(AssertionError):
    """Exception raised when trying to access an item that is not stored in the result dictionary."""


class StoredResult(dict[str, Any]):
    """
    A dictionary-like class that stores results from previous tests and allows access to items by key or attribute.
    """

    def __getitem__(self, key: str) -> Any:
        if key not in self:
            raise ItemNotStoredError(f"Key '{key}' not found in stored result. Known keys: {list(self.keys())}")

        return super().__getitem__(key)

    def __getattr__(self, key: str) -> Any:
        return self[key]

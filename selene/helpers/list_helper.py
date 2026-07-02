from collections.abc import Sequence
from typing import Any


def remove_duplicates(values: Sequence[Any] | str, separator: str = ',') -> list[Any]:
    if isinstance(values, str):
        values = values.split(separator)
    return list(set(values))

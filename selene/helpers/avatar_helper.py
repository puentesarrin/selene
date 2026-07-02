import hashlib
from collections.abc import Hashable
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')


class gravatar_memoized:
    def __init__(self, func: Callable[P, R]):
        self.func = func
        self.cache: dict[tuple[Any, ...], R] = {}

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        key = args + tuple(sorted(kwargs.items()))
        if not isinstance(key, Hashable):
            return self.func(*args, **kwargs)
        if key in self.cache:
            return self.cache[key]
        value = self.func(*args, **kwargs)
        self.cache[key] = value
        return value


@gravatar_memoized
def get_gravatar_url(email: str | None, size: int = 48) -> str:
    email = (email or '').strip().lower().encode('utf-8')
    md5email = hashlib.md5(email).hexdigest()
    return f'http://gravatar.com/avatar/{md5email}?s={size}'

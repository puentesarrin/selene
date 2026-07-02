version_tuple = (0, 1, 0, ".dev0")


def get_version_string():
    if isinstance(version_tuple[-1], str):
        return '.'.join(map(str, version_tuple[:-1])) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))


version = get_version_string()

from selene.web.application import Selene  # noqa: E402

__all__ = ('Selene',)

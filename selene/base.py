import re
from typing import Any

import tornado.locale
import tornado.web
from tornado.escape import to_unicode
from wtforms import Form


class BaseForm(Form):
    def __init__(
        self,
        formdata: Any = None,
        obj: Any = None,
        prefix: str = '',
        locale_code: str = 'en_US',
        **kwargs: Any,
    ):
        self._locale_code = locale_code
        data = kwargs or None
        super().__init__(formdata=formdata, obj=obj, prefix=prefix, data=data)
        self._translate_labels()

    def _translate_labels(self) -> None:
        locale = tornado.locale.get(self._locale_code)
        for field in self:
            field.label.text = locale.translate(field.label.text)

    def process(self, formdata: Any = None, obj: Any = None, data: Any = None, **kwargs: Any) -> None:
        if formdata is not None and not hasattr(formdata, 'getlist'):
            formdata = TornadoArgumentsWrapper(formdata)
        if data is None and kwargs:
            data = kwargs
        super().process(formdata=formdata, obj=obj, data=data, **kwargs)

    def _get_translations(self) -> Any:
        if not hasattr(self, '_locale_code'):
            self._locale_code = 'en_US'
        return TornadoLocaleWrapper(self._locale_code)


class TornadoArgumentsWrapper(dict[str, Any]):
    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def getlist(self, key: str) -> list[str]:
        try:
            values = []
            for value in self[key]:
                value = to_unicode(value)
                value = re.sub(r'[\x00-\x08\x0e-\x1f]', ' ', value)
                values.append(value)
            return values
        except KeyError as exc:
            raise AttributeError(key) from exc


class TornadoLocaleWrapper:
    def __init__(self, code: str):
        self.locale = tornado.locale.get(code)

    def gettext(self, message: str) -> str:
        return self.locale.translate(message)

    def ngettext(self, message: str, plural_message: str, count: int) -> str:
        return self.locale.translate(message, plural_message, count)


class BaseUIModule(tornado.web.UIModule): ...

import functools
import html
import re
import unicodedata
from collections.abc import Container, Iterable, Mapping
from datetime import datetime, tzinfo
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, TypeVar, Union

from dateutil.parser import parse as parse_date_string

from scrapbook.utils import remove_tags, tzinfos

if TYPE_CHECKING:
    from scrapbook.elements import BaseElement

FilterFunction = Callable[[Any], Any]

T = TypeVar("T")


class Filter(object):
    def __init__(self, empty_value: Optional[Any] = None):
        self.element: Optional[BaseElement] = None
        self.empty_value = empty_value

    def __call__(self, value: Optional[Any]) -> Any:
        if value is None:
            return self.empty_value
        return value


class Map(Filter):
    def __init__(self, *functions: FilterFunction, empty_value: Optional[Any] = None):
        self._functions = list(functions)
        super(Map, self).__init__(empty_value)

    def __call__(self, value: Optional[Any]):
        if value is None:
            return self.empty_value

        if isinstance(value, Mapping):
            return self._run_mapping(value)

        if isinstance(value, Iterable):
            return self._run_iterable(value)

        return self._run_other(value)

    def _run_mapping(self, mapping: Mapping[str, Any]):
        functions = self._get_functions()
        return {k: functools.reduce(lambda vv, f: f(vv), functions, v) for k, v in mapping.items()}

    def _run_iterable(self, iterable: Iterable[Any]):
        functions = self._get_functions()
        return list(
            functools.reduce(
                lambda v, f: map(f, v),
                functions,
                iterable,
            )
        )

    def _run_other(self, value: Any):
        functions = self._get_functions()
        return functools.reduce(
            lambda v, f: f(v),
            functions,
            value,
        )

    def _get_functions(self) -> list[FilterFunction]:
        if not self.element:
            return self._functions
        return [self.element.get_function(fn) for fn in self._functions]


class Through(Filter):
    def __call__(self, value: Optional[Any]):
        return value


class TakeFirst(Filter):
    def __call__(self, value: Optional[Iterable[Any]]):
        if value is None:
            return self.empty_value

        for v in value:
            if v is not None and v != "":
                return v

        return self.empty_value


class CleanText(Filter):
    def __init__(self, remove_line_breaks=False, empty_value: Optional[Any] = None):
        super(CleanText, self).__init__(empty_value)
        self.remove_line_breaks = remove_line_breaks

    def __call__(self, value: Optional[str]):
        if value is None or value == "":
            return self.empty_value

        retval = remove_tags(value)
        retval = html.unescape(retval)
        if self.remove_line_breaks:
            retval = re.sub(r"(?:\n\r|\r\n|\n|\r)+", " ", retval)
        retval = re.sub(r"[ 　]+", " ", retval)
        retval = retval.strip()

        if retval == "":
            return self.empty_value

        return retval


class Equals(Filter):
    def __init__(self, value: Optional[Any]):
        super(Equals, self).__init__()
        self.value = value

    def __call__(self, value: Optional[Any]):
        return self.value == value


class Contains(Filter):
    def __init__(self, value: Any, empty_value: Optional[Any] = None):
        super(Contains, self).__init__(empty_value)
        self.value = value

    def __call__(self, value: Optional[Container]):
        if value is None:
            return self.empty_value
        return self.value in value


class Fetch(Filter):
    def __init__(self, pattern: Union[str, re.Pattern], all=False, empty_value: Optional[Any] = None):
        super(Fetch, self).__init__(empty_value)
        self.pattern = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        self.all = all

    def __call__(self, value: Optional[str]):
        if value is None:
            return self.empty_value

        if self.all:
            return self._fetch_all(value)
        return self._fetch(value)

    def _fetch(self, value: str):
        match = self.pattern.search(value)
        if not match:
            return self.empty_value
        return self._get_value(match)

    def _fetch_all(self, value: str):
        data = []
        for match in self.pattern.finditer(value):
            data.append(self._get_value(match))
        return data

    def _get_value(self, match: re.Match):
        dict_value = match.groupdict()
        if dict_value:
            return dict_value

        list_value = match.groups()
        if list_value:
            return list(list_value)

        return match.group(0)


class Replace(Filter):
    def __init__(
        self,
        pattern: Union[str, re.Pattern],
        replace: Union[str, Callable[[re.Match[str]], str]],
        empty_value: Optional[Any] = None,
    ):
        super(Replace, self).__init__(empty_value)
        self.pattern = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        self.replace = replace

    def __call__(self, value: Optional[str]):
        if value is None:
            return self.empty_value
        return self.pattern.sub(self.replace, value)


class Join(Filter):
    def __init__(self, separator="", empty_value: Optional[Any] = None):
        super(Join, self).__init__(empty_value)
        self.separator = separator

    def __call__(self, value: Optional[Iterable[str]]):
        if value is None:
            return self.empty_value
        return self.separator.join(value)


class Split(Filter):
    def __init__(self, delimiter=",", empty_value: Optional[Any] = None):
        super(Split, self).__init__(empty_value)
        self.delimiter = delimiter

    def __call__(self, value: Optional[str]):
        if value is None:
            return self.empty_value
        return value.split(self.delimiter)


class Normalize(Filter):
    def __init__(self, form: Literal["NFC", "NFD", "NFKC", "NFKD"] = "NFKD", empty_value: Optional[Any] = None):
        super(Normalize, self).__init__(empty_value)
        self.form = form

    def __call__(self, value: Optional[str]):
        if value is None:
            return self.empty_value
        return unicodedata.normalize(self.form, value)


class RenameKey(Filter):
    def __init__(self, name_map: Mapping[str, str], empty_value: Optional[Any] = None):
        super(RenameKey, self).__init__(empty_value)
        self.name_map = name_map

    def __call__(self, value: Optional[Mapping[str, Any]]):
        if value is None:
            return self.empty_value
        return {self.name_map.get(k, k): v for k, v in value.items()}


class FilterDict(Filter):
    def __init__(self, keys: Iterable[str], ignore=False, empty_value: Optional[Any] = None):
        super(FilterDict, self).__init__(empty_value)
        self.keys = keys
        self.ignore = ignore

    def __call__(self, value: Optional[Any]):
        if value is None:
            return self.empty_value

        if self.ignore:
            return {k: v for k, v in value.items() if k not in self.keys}

        return {key: value[key] for key in self.keys if key in value}


class Partial(Filter):
    def __init__(
        self,
        fn: Callable,
        args: Optional[list[Any]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        arg_name=None,
        empty_value: Optional[Any] = None,
    ):
        super(Partial, self).__init__(empty_value)
        args = args or []
        kwargs = kwargs or {}
        self.fn = functools.partial(fn, *args, **kwargs)
        self.arg_name = arg_name

    def __call__(self, value: Optional[Any]):
        if value is None:
            return self.empty_value

        if self.arg_name:
            return self.fn(**{self.arg_name: value})
        return self.fn(value)


class DateTime(Filter):
    def __init__(
        self,
        format: Optional[str] = None,
        timezone: Optional[tzinfo] = None,
        truncate_time=False,
        truncate_timezone=False,
        empty_value: Optional[Any] = None,
    ):
        super(DateTime, self).__init__(empty_value)
        self.format = format
        self.timezone = timezone
        self.truncate_time = truncate_time
        self.truncate_timezone = truncate_timezone

    def __call__(self, value: Optional[str]):
        if value is None:
            return self.empty_value

        if self.format:
            dt = datetime.strptime(value, self.format)
            if self.timezone:
                dt = dt.replace(tzinfo=self.timezone)
        else:
            dt = parse_date_string(value, default=datetime(1, 1, 1), tzinfos=tzinfos)

        if self.truncate_timezone:
            dt = dt.replace(tzinfo=None)

        if self.truncate_time:
            return dt.date()

        return dt


class Bool(Filter):
    def __init__(self, *true_values: str, empty_value: Optional[Any] = None):
        super(Bool, self).__init__(empty_value)
        self.true_values = true_values or ("true", "True", "TRUE", "yes", "Yes", "YES", "1")

    def __call__(self, value: Optional[Any]):
        if value is None:
            return self.empty_value
        return value in self.true_values


through = Through()
take_first = TakeFirst()
clean_text = CleanText()

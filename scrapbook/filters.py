# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from collections import Iterable, Mapping
from datetime import datetime
import functools
import re
import unicodedata

from dateutil.parser import parse as parse_date_string
import six
from six.moves.html_parser import HTMLParser

from .utils import remove_tags, tzinfos


class Filter(object):
    def __init__(self, empty_value=None):
        self.element = None
        self.empty_value = empty_value

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value
        return value

    def is_empty(self, value):
        return value is None or value == ''


class Map(Filter):
    def __init__(self, *functions, **kwargs):
        self._functions = functions
        super(Map, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value

        if isinstance(value, Mapping):
            return self._run_mapping(value)

        if isinstance(value, Iterable):
            return self._run_iterable(value)

        return self._run_other(value)

    def _run_mapping(self, mapping):
        functions = self._get_functions()
        return {
            k: six.moves.reduce(lambda vv, f: f(vv), functions, v)
            for k, v in mapping.items()
        }

    def _run_iterable(self, iterable):
        functions = self._get_functions()
        return list(six.moves.reduce(
            lambda v, f: map(f, v),
            functions,
            iterable,
        ))

    def _run_other(self, value):
        functions = self._get_functions()
        return six.moves.reduce(
            lambda v, f: f(v),
            functions,
            value,
        )

    def _get_functions(self):
        if not self.element:
            return self._functions
        return [self.element.get_function(fn) for fn in self._functions]


class Through(Filter):
    def __call__(self, value):
        return value


class TakeFirst(Filter):
    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value

        for v in value:
            if v is not None and v != '':
                return v
        return self.empty_value


class CleanText(Filter):
    def __init__(self, remove_line_breaks=False, **kwargs):
        self.remove_line_breaks = remove_line_breaks
        super(CleanText, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value

        value = remove_tags(value)
        value = HTMLParser().unescape(value)
        if self.remove_line_breaks:
            value = re.sub(r'(?:\n\r|\r\n|\n|\r)+', ' ', value)
        value = re.sub(r'[ 　]+', ' ', value)
        value = value.strip()

        if value == '':
            return self.empty_value

        return value


class Equals(Filter):
    def __init__(self, value, **kwargs):
        self.value = value
        super(Equals, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value
        return self.value == value


class Contains(Filter):
    def __init__(self, value, **kwargs):
        self.value = value
        super(Contains, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value
        return self.value in value


class Fetch(Filter):
    def __init__(self, pattern, all=False, **kwargs):
        self.pattern = re.compile(pattern)
        self.all = all
        super(Fetch, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value

        if self.all:
            return self._fetch_all(value)
        return self._fetch(value)

    def _fetch(self, value):
        match = self.pattern.search(value)
        if not match:
            return self.empty_value
        return self._get_value(match)

    def _fetch_all(self, value):
        data = []
        for match in self.pattern.finditer(value):
            data.append(self._get_value(match))
        return data

    def _get_value(self, match):
        dict_value = match.groupdict()
        if dict_value:
            return dict_value

        list_value = match.groups()
        if list_value:
            return list_value

        return match.group(0)


class Replace(Filter):
    def __init__(self, pattern, replace, **kwargs):
        self.pattern = re.compile(pattern)
        self.replace = replace
        super(Replace, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value
        return self.pattern.sub(self.replace, value)


class Join(Filter):
    def __init__(self, separator='', **kwargs):
        self.separator = separator
        super(Join, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value
        return self.separator.join(value)


class Split(Filter):
    def __init__(self, delimiter, **kwargs):
        self.delimiter = delimiter
        super(Split, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value
        return value.split(self.delimiter)


class Normalize(Filter):
    def __init__(self, form='NFKD', **kwargs):
        self.form = form
        super(Normalize, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value
        return unicodedata.normalize(self.form, value)


class RenameKey(Filter):
    def __init__(self, name_map, **kwargs):
        self.name_map = name_map
        super(RenameKey, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value
        return {self.name_map.get(k, k): v for k, v in value.items()}


class FilterDict(Filter):
    def __init__(self, keys, ignore=False, **kwargs):
        self.keys = keys
        self.ignore = ignore
        super(FilterDict, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value

        if self.ignore:
            return {
                k: v
                for k, v in value.items()
                if k not in self.keys
            }

        return {
            key: value[key]
            for key in self.keys
            if key in value
        }


class Partial(Filter):
    def __init__(self, fn, args=None, kwargs=None, arg_name=None, **parent_kwargs):
        args = args or tuple()
        kwargs = kwargs or {}
        self.fn = functools.partial(fn, *args, **kwargs)
        self.arg_name = arg_name
        super(Partial, self).__init__(**parent_kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value

        if self.arg_name:
            return self.fn(**{self.arg_name: value})
        return self.fn(value)


class DateTime(Filter):
    def __init__(
        self,
        format=None,
        timezone=None,
        truncate_time=False,
        truncate_timezone=False,
        **kwargs
    ):
        self.format = format
        self.timezone = timezone
        self.truncate_time = truncate_time
        self.truncate_timezone = truncate_timezone
        super(DateTime, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
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
    def __init__(self, *true_values, **kwargs):
        self.true_values = true_values or ['true', 'True', 'TRUE', 'yes', 'Yes', 'YES', '1']
        super(Bool, self).__init__(**kwargs)

    def __call__(self, value):
        if self.is_empty(value):
            return self.empty_value
        return value in self.true_values


through = Through()
take_first = TakeFirst()
clean_text = CleanText()

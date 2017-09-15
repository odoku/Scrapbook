# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from collections import Iterable, Mapping
import re
import unicodedata

import six
from six.moves.html_parser import HTMLParser

from .utils import remove_tags


class Map(object):
    def __init__(self, *functions):
        self.functions = functions

    def __call__(self, values):
        if isinstance(values, Mapping):
            return self._run_mapping(values)

        if isinstance(values, Iterable):
            return self._run_iterable(values)

        return self._run_other(values)

    def _run_mapping(self, mapping):
        return {
            k: six.moves.reduce(lambda vv, f: f(vv), self.functions, v)
            for k, v in mapping.items()
        }

    def _run_iterable(self, iterable):
        return list(six.moves.reduce(
            lambda v, f: map(f, v),
            self.functions,
            iterable,
        ))

    def _run_other(self, value):
        return six.moves.reduce(
            lambda v, f: f(v),
            self.functions,
            value,
        )


class Through(object):
    def __call__(self, value):
        return value


class TakeFirst(object):
    def __call__(self, values):
        if values is None:
            return None

        for value in values:
            if value is not None and value != '':
                return value
        return None


class CleanText(object):
    def __call__(self, value):
        if value:
            value = remove_tags(value)
            value = HTMLParser().unescape(value)
            value = re.sub(r'[ 　]+', ' ', value)
            value = value.strip()
        return value


class Equals(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, value):
        return self.value == value


class Contains(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, value):
        if value is None:
            return False
        return self.value in value


class Fetch(object):
    def __init__(self, pattern, all=False):
        self.pattern = re.compile(pattern)
        self.all = all

    def __call__(self, value):
        if value is None:
            return None

        if self.all:
            return self._fetch_all(value)
        return self._fetch(value)

    def _fetch(self, value):
        match = self.pattern.search(value)
        if not match:
            return None
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


class Replace(object):
    def __init__(self, pattern, replace):
        self.pattern = re.compile(pattern)
        self.replace = replace

    def __call__(self, value):
        if value is None:
            return None
        return self.pattern.sub(self.replace, value)


class Join(object):
    def __init__(self, separator=''):
        self.separator = separator

    def __call__(self, value):
        if value is None:
            return None
        return self.separator.join(value)


class Normalize(object):
    def __init__(self, form='NFKD'):
        self.form = form

    def __call__(self, value):
        if value is None:
            return None
        return unicodedata.normalize(self.form, value)


class RenameKey(object):
    def __init__(self, name_map):
        self.name_map = name_map

    def __call__(self, value):
        if value is None:
            return None
        return {self.name_map.get(k, k): v for k, v in value.items()}


class FilterDict(object):
    def __init__(self, keys, ignore=False):
        self.keys = keys
        self.ignore = ignore

    def __call__(self, value):
        if value is None:
            return None

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


through = Through()
take_first = TakeFirst()
clean_text = CleanText()

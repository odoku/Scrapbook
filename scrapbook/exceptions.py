# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from parsel import SelectorList


class ScrapBookError(Exception):
    def __init__(self, parent, selector=None, value=None, field=None):
        self._parent = parent
        self._selector = selector
        self._value = value
        self._field = field

        super(ScrapBookError, self).__init__(self._create_message())
        self.with_traceback(parent.__traceback__)

    def _create_message(self):
        parent = self.parent
        message = 'Raises {}: {}\nXPath: {}\nValue: {}\nField: {}'.format(
            parent.__class__.__name__, str(parent),
            self.xpath,
            self.value,
            self.field,
        )
        return message

    @property
    def parent(self):
        if isinstance(self._parent, self.__class__):
            return self._parent.parent
        return self._parent

    @property
    def selector(self):
        if self._selector:
            return self._selector

        if isinstance(self._parent, self.__class__):
            return self._parent.selector

        return None

    @property
    def xpath(self):
        if not self.selector:
            return None

        if isinstance(self.selector, SelectorList):
            return self.selector[0]._expr
        return self.selector._expr

    @property
    def value(self):
        if self._value:
            return self._value

        if isinstance(self._parent, self.__class__):
            return self._parent.value

        return None

    @property
    def field(self):
        parent_field = self._parent.field if isinstance(self._parent, self.__class__) else None

        if parent_field and self._field:
            return '{}.{}'.format(self._field, parent_field)

        return self._field

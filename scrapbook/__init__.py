# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from collections import MutableMapping
import inspect
import six
from parsel import Selector

from .exceptions import ScrapBookError
from .filters import clean_text, Filter, through
from .parsers import First
from .utils import merge_dict


class BaseElement(object):
    filter = (through,)

    def __init__(self, xpath=None, filter=None):
        self.instance = None
        self.xpath = xpath
        if filter:
            self.filter = filter

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    @property
    def is_descriptor(self):
        return self.instance is not None

    def get_function(self, fn):
        if isinstance(fn, Filter):
            fn.element = self
            return fn

        if callable(fn):
            return fn

        method = getattr(self, six.text_type(fn), None)
        if method and callable(method):
            return method

        if self.instance and hasattr(self.instance, 'get_function'):
            return self.instance.get_function(fn)

        raise ValueError('{} is not callable.'.format(fn))

    def get_filter(self):
        if not isinstance(self.filter, (list, tuple)):
            filters = [self.filter]
        else:
            filters = self.filter

        return [self.get_function(f) for f in filters]

    def get_selector(self, html):
        selector = Selector(text=html) if isinstance(html, six.string_types) else html
        if self.xpath:
            return selector.xpath(self.xpath)
        return selector.xpath('.')

    def parse(self, html):
        raise NotImplementedError()


class ContentMeta(type):
    def __new__(klass, name, bases, attrs):
        new_class = super(ContentMeta, klass).__new__(klass, name, bases, attrs)

        elements = {
            attr: getattr(new_class, attr)
            for attr in attrs
            if not attr.startswith('_') and isinstance(getattr(new_class, attr), BaseElement)
        }

        for base in bases:
            if hasattr(base, 'elements'):
                elements = merge_dict(base.elements, elements)

        new_class.elements = elements

        return new_class


@six.add_metaclass(ContentMeta)
class Content(BaseElement):
    def __init__(self, *args, **kwargs):
        self.many = kwargs.pop('many', False)
        super(Content, self).__init__(*args, **kwargs)

    def _parse(self, selector):
        data = {}
        for name in self.elements:
            try:
                data[name] = getattr(self, name).parse(selector)
            except Exception as e:
                raise ScrapBookError(parent=e, field=name)
        return data

    def parse(self, html, object=None):
        selector = self.get_selector(html)
        if len(selector) == 0:
            return None

        if self.many:
            value = [self._parse(s) for s in selector]
        else:
            value = self._parse(selector)

        for filter in self.get_filter():
            try:
                value = filter(value)
            except Exception as e:
                raise ScrapBookError(parent=e, selector=selector, value=value)

        return self._map_to(value, object)

    def _map_to(self, value, object):
        if object is None:
            return value

        if isinstance(value, (list, tuple)):
            return [self._map_value(v, object) for v in value]
        return self._map_value(value, object)

    def _map_value(self, value, object):
        if inspect.isclass(object):
            object = object()

        if isinstance(object, MutableMapping):
            for k, v in value.items():
                object[k] = v
            return object

        for k, v in value.items():
            setattr(object, k, v)
        return object

    @classmethod
    def inline(base, xpath=None, filter=None, **attrs):
        cls = type('InlineContent', (base,), attrs)
        return cls(xpath, filter)


class Element(BaseElement):
    filter = (clean_text,)
    parser = First()

    def __init__(self, *args, **kwargs):
        parser = kwargs.pop('parser', None)
        if parser:
            self.parser = parser
        super(Element, self).__init__(*args, **kwargs)

    def get_parser(self):
        return self.get_function(self.parser)

    def _parse(self, selector):
        return self.get_parser()(selector)

    def parse(self, html):
        selector = self.get_selector(html)
        if len(selector) == 0:
            return None

        value = None
        try:
            value = self._parse(selector)
            for filter in self.get_filter():
                value = filter(value)
        except Exception as e:
            raise ScrapBookError(parent=e, selector=selector, value=value)

        return value

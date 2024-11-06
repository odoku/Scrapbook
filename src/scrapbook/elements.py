import inspect
from collections.abc import MutableMapping
from typing import Any, Callable, Optional, Union, cast

from parsel import Selector, SelectorList

from scrapbook.exceptions import ScrapBookError
from scrapbook.filters import Filter, FilterFunction, clean_text, through
from scrapbook.parsers import First, ParserFunction
from scrapbook.utils import merge_dict

FilterFunctionOrStr = Union[str, FilterFunction]
ParserFunctionOrStr = Union[str, ParserFunction]


class BaseElement:
    filter: Union[FilterFunctionOrStr, list[FilterFunctionOrStr]] = [through]

    def __init__(
        self,
        xpath: Optional[str] = None,
        filter: Optional[Union[FilterFunctionOrStr, list[FilterFunctionOrStr]]] = None,
    ):
        self.parent: Optional[BaseElement] = None
        self.xpath = xpath
        if filter:
            self.filter = filter

    def __get__(self, instance: Any, owner):
        self.parent = instance
        return self

    @property
    def is_descriptor(self):
        return self.parent is not None

    def get_function(self, fn: Union[str, Callable]) -> Callable:
        if isinstance(fn, Filter):
            fn.element = self
            return fn

        if callable(fn):
            return fn

        method = getattr(self, fn, None)
        if method and callable(method):
            return method

        if self.parent and hasattr(self.parent, "get_function"):
            return self.parent.get_function(fn)

        raise ValueError("{} is not callable.".format(fn))

    def get_filter(self) -> list[FilterFunction]:
        if isinstance(self.filter, list):
            filters = self.filter
        else:
            filters = [self.filter]
        return [self.get_function(f) for f in filters]

    def get_selector(self, html: Union[str, Selector]):
        selector = Selector(text=html) if isinstance(html, str) else html
        if self.xpath:
            return selector.xpath(self.xpath)
        return selector.xpath(".")

    def parse(self, html: Union[str, Selector]):
        raise NotImplementedError()


class Element(BaseElement):
    filter = [clean_text]
    parser: ParserFunctionOrStr = First()

    def __init__(
        self,
        xpath: Optional[str] = None,
        filter: Optional[Union[FilterFunctionOrStr, list[FilterFunctionOrStr]]] = None,
        parser: Optional[ParserFunctionOrStr] = None,
    ):
        if parser:
            self.parser = parser
        super(Element, self).__init__(xpath, filter)

    def get_parser(self) -> ParserFunction:
        return self.get_function(self.parser)

    def _parse(self, selector: SelectorList[Selector]):
        return self.get_parser()(selector)

    def parse(self, html: Union[str, Selector]):
        selector = self.get_selector(html)
        if len(selector) == 0:
            return None

        value = None
        try:
            value = self._parse(selector)
            for filter in self.get_filter():
                value = filter(value)
        except Exception as e:
            raise ScrapBookError(parent=e, selector=selector, value=value) from e

        return value


class ContentMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        return {"elements": {}}

    def __new__(klass, name: str, bases: tuple[type, ...], attrs: dict[str, Any]):
        new_class = cast("Content", super(ContentMeta, klass).__new__(klass, name, bases, attrs))

        elements = {
            attr: getattr(new_class, attr)
            for attr in attrs
            if not attr.startswith("_") and isinstance(getattr(new_class, attr), BaseElement)
        }

        for base in bases:
            # if issubclass(base, Content):
            if hasattr(base, "elements"):
                elements = merge_dict(base.elements, elements)

        new_class.elements = elements

        return new_class


class Content(BaseElement, metaclass=ContentMeta):
    elements: dict[str, BaseElement]

    def __init__(
        self,
        xpath: Optional[str] = None,
        filter: Optional[Union[FilterFunctionOrStr, list[FilterFunctionOrStr]]] = None,
        many=False,
    ):
        self.many = many
        super(Content, self).__init__(xpath, filter)

    def _parse(self, selector: Selector):
        data = {}
        for name in self.elements:
            try:
                data[name] = getattr(self, name).parse(selector)
            except Exception as e:
                raise ScrapBookError(parent=e, field=name) from e
        return data

    def parse(self, html: Union[str, Selector], object: Optional[Any] = None):
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
                raise ScrapBookError(parent=e, selector=selector, value=value) from e

        return self._map_to(value, object)

    def _map_to(self, value: Any, object: Optional[Any]):
        if object is None:
            return value

        if isinstance(value, (list, tuple)):
            return [self._map_value(v, object) for v in value]
        return self._map_value(value, object)

    def _map_value(self, value: Any, object: Optional[Any]):
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
    def inline(
        base: type,
        xpath: Optional[str] = None,
        filter: Optional[Union[FilterFunctionOrStr, list[FilterFunctionOrStr]]] = None,
        many=False,
        **attrs,
    ):
        cls = type("InlineContent", (base,), attrs)
        return cls(xpath, filter, many)

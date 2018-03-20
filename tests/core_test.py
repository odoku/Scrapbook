# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from collections import OrderedDict

from parsel import Selector

from scrapbook import (
    BaseElement,
    Content,
    Element,
)


class TestBaseElement(object):
    def test_is_description(self):
        obj = BaseElement()
        assert not obj.is_descriptor

        class A(object):
            element = BaseElement()

        assert A().element.is_descriptor

    def test_get_function(self, mocker):
        def fn1(value):
            return 1

        class A(BaseElement):
            element = BaseElement()

            def fn2(self, value):
                return 2

        a = A()
        assert fn1 == a.get_function(fn1)
        assert a.fn2 == a.get_function('fn2')
        assert fn1 == a.element.get_function(fn1)
        assert a.fn2 == a.element.get_function('fn2')

    def test_get_filter(self, mocker):
        def fn1(value):
            return 1

        class A(BaseElement):
            element1 = BaseElement(filter=fn1)
            element2 = BaseElement(filter='fn2')
            element3 = BaseElement(filter=[fn1, 'fn2'])

            def fn2(self, value):
                return 2

        a = A(filter='fn2')
        assert [a.fn2] == a.get_filter()
        assert [fn1] == a.element1.get_filter()
        assert [a.fn2] == a.element2.get_filter()
        assert [fn1, a.fn2] == a.element3.get_filter()

    def test_get_selector(self):
        html = Selector(u'<html><body><p><a href="http://google.com">Link</a></p></body></html>')

        assert BaseElement().get_selector(html).extract() == html.xpath('.').extract()
        assert BaseElement(xpath='/p/a').get_selector(html).extract() == \
            html.xpath('/p/a').extract()


class TestContent(object):
    def test_inherit(self):
        class A(Content):
            el1 = Element()
            _ignore = Element()

        class B(Content):
            el2 = Element()

        class C(B):
            el3 = Element()

        class D(A, C):
            el4 = Element()

        assert D().elements == {
            'el1': A.el1,
            'el2': B.el2,
            'el3': C.el3,
            'el4': D.el4,
        }

    def test_parse(self):
        html = u'<html><body><p><a href="http://google.com">Link</a></p></body></html>'

        class A(Content):
            el1 = Element(xpath='/html/body/p/a/text()')
            el2 = Element(xpath='/html/body/p/a/@href')

        assert A().parse(html) == {
            'el1': 'Link',
            'el2': 'http://google.com',
        }

    def test_parse_with_mutable_mapping_instance(self):
        html = u'<html><body><p><a href="http://google.com">Link</a></p></body></html>'

        class A(Content):
            el1 = Element(xpath='/html/body/p/a/text()')
            el2 = Element(xpath='/html/body/p/a/@href')

        obj = OrderedDict()

        result = A().parse(html, object=obj)
        assert isinstance(result, OrderedDict)
        assert 'Link' == result['el1']
        assert 'http://google.com' == result['el2']

    def test_parse_with_mutable_mapping_class(self):
        html = u'<html><body><p><a href="http://google.com">Link</a></p></body></html>'

        class A(Content):
            el1 = Element(xpath='/html/body/p/a/text()')
            el2 = Element(xpath='/html/body/p/a/@href')

        result = A().parse(html, object=OrderedDict)
        assert isinstance(result, OrderedDict)
        assert 'Link' == result['el1']
        assert 'http://google.com' == result['el2']

    def test_parse_with_object(self):
        html = u'<html><body><p><a href="http://google.com">Link</a></p></body></html>'

        class A(Content):
            el1 = Element(xpath='/html/body/p/a/text()')
            el2 = Element(xpath='/html/body/p/a/@href')

        class Obj(object):
            def __init__(self):
                self.el1 = None
                self.el2 = None

        obj = Obj()

        result = A().parse(html, object=obj)
        assert isinstance(result, Obj)
        assert 'Link' == result.el1
        assert 'http://google.com' == result.el2

    def test_parse_many(self):
        html = u'<html><body><ul><li>1</li><li>2</li><li>3</li></ul></body></html>'

        class A(Content):
            value = Element(xpath='./text()')

        result = A(xpath='/html/body/ul/li', many=True).parse(html)
        assert [
            {'value': '1'},
            {'value': '2'},
            {'value': '3'},
        ] == result

    def test_parse_many_with_object(self):
        html = u'<html><body><ul><li>1</li><li>2</li><li>3</li></ul></body></html>'

        class A(Content):
            value = Element(xpath='./text()')

        class Obj(object):
            def __init__(self):
                self.value = None

        result = A(xpath='/html/body/ul/li', many=True).parse(html, object=Obj)
        assert isinstance(result, list)
        assert 3 == len(result)
        assert isinstance(result[0], Obj)
        assert '1' == result[0].value
        assert isinstance(result[1], Obj)
        assert '2' == result[1].value
        assert isinstance(result[2], Obj)
        assert '3' == result[2].value

    def test_inline(self):
        html = u'<html><body><p><a href="http://google.com">Link</a></p></body></html>'

        class A(Content):
            content = Content.inline(
                el1=Element(xpath='/html/body/p/a/text()', filter='twice')
            )
            el2 = Element(xpath='/html/body/p/a/@href')

            def twice(self, value):
                return value * 2

        assert A().parse(html) == {
            'content': {'el1': 'LinkLink'},
            'el2': 'http://google.com',
        }


class TestElement(object):
    def test_get_parser(self):
        def fn1(value):
            return 1

        class A(Content):
            element1 = Element(parser=fn1)
            element2 = Element(parser='fn2')

            def fn2(self, value):
                return 2

        a = A()
        assert a.element1.get_parser() == fn1
        assert a.element2.get_parser() == a.fn2

    def test_parse(self):
        html = u'<html><body><p><a href="http://google.com">Link</a></p></body></html>'
        assert Element(xpath='/html/body/p/a/text()').parse(html) == 'Link'

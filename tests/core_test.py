# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from parsel import Selector

from scrapbook import (
    BaseElement,
    Element,
    Content,
)


class TestBaseElement(object):
    def test_is_description(self):
        obj = BaseElement()
        assert not obj.is_descriptor

        class A(object):
            element = BaseElement()

        assert A().element.is_descriptor

    def test_get_filter(self, mocker):
        def fn1(value):
            return 1

        class A(object):
            element1 = BaseElement(filter=fn1)
            element2 = BaseElement(filter='fn2')
            element3 = BaseElement(filter=[fn1, 'fn2'])

            def fn2(self, value):
                return 2

        a = A()
        assert a.element1.get_filter() == [fn1]
        assert a.element2.get_filter() == [a.fn2]
        assert a.element3.get_filter() == [fn1, a.fn2]

    def test_get_selector(self):
        html = Selector('<html><body><p><a href="http://google.com">Link</a></p></body></html>')

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

        assert D.fields == {
            'el1': A.el1,
            'el2': B.el2,
            'el3': C.el3,
            'el4': D.el4,
        }

    def test_parse(self):
        html = Selector('<html><body><p><a href="http://google.com">Link</a></p></body></html>')

        class A(Content):
            el1 = Element(xpath='/html/body/p/a/text()')
            el2 = Element(xpath='/html/body/p/a/@href')

        assert A().parse(html) == {
            'el1': 'Link',
            'el2': 'http://google.com',
        }


class TestElement(object):
    def test_get_parser(self):
        def fn1(value):
            return 1

        class A(object):
            element1 = Element(parser=fn1)
            element2 = Element(parser='fn2')

            def fn2(self, value):
                return 2

        a = A()
        assert a.element1.get_parser() == fn1
        assert a.element2.get_parser() == a.fn2

    def test_parse(self):
        html = Selector('<html><body><p><a href="http://google.com">Link</a></p></body></html>')
        assert Element(xpath='/html/body/p/a/text()').parse(html) == 'Link'

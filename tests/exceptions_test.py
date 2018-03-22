# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from parsel import Selector

from scrapbook import Content, Element, filters
from scrapbook.exceptions import ScrapBookError


class TestScrapBookError(object):
    def test_get_parent_property(self):
        ex1 = Exception('Root exception')

        ex2 = ScrapBookError(ex1)
        assert ex2.parent == ex1

        ex3 = ScrapBookError(ex2)
        assert ex3.parent == ex1

    def test_get_value_property(self):
        ex1 = Exception('Root exception')

        ex2 = ScrapBookError(ex1, value=10)
        assert ex2.value == 10

        ex3 = ScrapBookError(ex2)
        assert ex3.value == 10

        ex4 = ScrapBookError(ex3, value=20)
        assert ex4.value == 20

    def test_get_selector_property(self):
        ex1 = Exception('Root exception')

        s1 = Selector('<p />')
        ex2 = ScrapBookError(ex1, selector=s1)
        assert ex2.selector == s1

        ex3 = ScrapBookError(ex2)
        assert ex3.selector == s1

        s2 = Selector('<div />')
        ex4 = ScrapBookError(ex3, selector=s2)
        assert ex4.selector == s2

    def test_get_xpath_property(self):
        ex1 = Exception('Root exception')

        ex2 = ScrapBookError(ex1)
        assert ex2.xpath is None

        s1 = Selector('<p><span>zzz</span></p>')
        s1 = s1.xpath('/html/body/p')
        ex3 = ScrapBookError(ex2, selector=s1)
        assert ex3.xpath == '/html/body/p'

        ex4 = ScrapBookError(ex3)
        assert ex4.xpath == '/html/body/p'

        s2 = s1.xpath('./span')
        ex5 = ScrapBookError(ex4, selector=s2)
        assert ex5.xpath == './span'

    def test_get_field_property(self):
        ex1 = Exception('Root exception')

        ex2 = ScrapBookError(ex1)
        assert ex2.field is None

        ex3 = ScrapBookError(ex2, field='aaa')
        assert ex3.field == 'aaa'

        ex4 = ScrapBookError(ex3, field='bbb')
        assert ex4.field == 'bbb.aaa'

    def test_with_content(self):
        content = Content.inline(
            xpath='/html',
            field1=Content.inline(
                xpath='./body',
                field2=Element('./p/text()', filter=filters.DateTime())
            ),
        )

        try:
            content.parse('''
                <html>
                    <body>
                        <p>aaaa</p>
                        <div>bbbb</div>
                    </body>
                </html>
            ''')
        except ScrapBookError as e:
            assert isinstance(e.parent, ValueError)
            assert e.xpath == './p/text()'
            assert e.field == 'field1.field2'
            assert e.value == 'aaaa'
        else:
            assert False, 'ScrapBookError is not raise.'

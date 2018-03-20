# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from datetime import date, datetime

from dateutil.tz import tzoffset
import pytest

from scrapbook import Content, Element
from scrapbook.filters import (
    Bool,
    CleanText,
    Contains,
    DateTime,
    Equals,
    Fetch,
    FilterDict,
    Join,
    Map,
    Normalize,
    Partial,
    RenameKey,
    Replace,
    take_first,
    through,
)
from scrapbook.parsers import All


class TestMap(object):
    def test_with_int(self, mocker):
        fn1 = mocker.Mock(name='fn1', return_value=1)
        fn2 = mocker.Mock(name='fn2', return_value=2)

        result = Map(fn1, fn2)(0)

        fn1.assert_called_once_with(0)
        fn2.assert_called_once_with(1)
        assert 2 == result

    def test_with_dict(self, mocker):
        fn1 = mocker.Mock(name='fn1', side_effect=lambda v: v * 2)
        fn2 = mocker.Mock(name='fn2', side_effect=lambda v: v * 10)

        result = Map(fn1, fn2)({'AAA': 1, 'BBB': 2})

        fn1.assert_has_calls([mocker.call(1), mocker.call(2)], any_order=True)
        fn2.assert_has_calls([mocker.call(2), mocker.call(4)], any_order=True)
        assert {'AAA': 20, 'BBB': 40} == result

    def test_with_list(self, mocker):
        fn1 = mocker.Mock(name='fn1', side_effect=lambda v: v * 2)
        fn2 = mocker.Mock(name='fn2', side_effect=lambda v: v * 10)

        result = Map(fn1, fn2)([1, 2])

        fn1.assert_has_calls([mocker.call(1), mocker.call(2)], any_order=True)
        fn2.assert_has_calls([mocker.call(2), mocker.call(4)], any_order=True)
        assert [20, 40] == result

    def test_with_none(self, mocker):
        fn1 = mocker.Mock(name='fn1', side_effect=lambda v: v)
        fn2 = mocker.Mock(name='fn2', side_effect=lambda v: v)

        result = Map(fn1, fn2)(None)

        fn1.assert_not_called()
        fn2.assert_not_called()
        assert result is None

    def test_on_element(self, mocker):
        class El(Element):
            def fn2(self, value):
                pass

        fn1 = mocker.Mock(name='fn1', side_effect=lambda v: v * 2)
        fn2 = mocker.patch.object(target=El, attribute='fn2', side_effect=lambda v: v * 3)

        element = El(xpath='//p/text()', parser=All(), filter=Map(fn1, 'fn2'))
        result = element.parse(u'<p>a</p><p>b</p>')

        fn1.assert_has_calls([mocker.call('a'), mocker.call('b')], any_order=True)
        fn2.assert_has_calls([mocker.call('aa'), mocker.call('bb'), ], any_order=True)
        assert ['aaaaaa', 'bbbbbb'] == result

    def test_on_content(self, mocker):
        fn1 = mocker.Mock(name='fn1', side_effect=lambda v: v * 2)

        class C(Content):
            field = Element(xpath='//p/text()', parser=All(), filter=Map(fn1, 'fn2'))

            def fn2(self, value):
                pass

        fn2 = mocker.patch.object(target=C, attribute='fn2', side_effect=lambda v: v * 3)

        c = C(xpath='')
        result = c.parse(u'<p>a</p><p>b</p>')

        fn1.assert_has_calls([mocker.call('a'), mocker.call('b')], any_order=True)
        fn2.assert_has_calls([mocker.call('aa'), mocker.call('bb'), ], any_order=True)
        assert ['aaaaaa', 'bbbbbb'] == result['field']


class TestThrough(object):
    def test_(self):
        value = 100
        assert value == through(value)

    def test_with_none(self):
        assert through(None) is None


class TestTakeFirst(object):
    def test_(self):
        assert 1 == take_first([1, 2, 3, 4])

    def test_with_list_include_empty_value(self):
        assert 0 == take_first([None, '', 0, 1])

    def test_with_none(self):
        assert take_first(None) is None


class TestCleanText(object):
    @pytest.mark.parametrize(['text', 'result'], [
        ('  aaa  ', 'aaa'),
        ('<p>aaa</p>', 'aaa'),
        ('&amp;', '&'),
        ('aa       bb', 'aa bb'),
        ('<p>  aaa  &amp;  bbb  </p>', 'aaa & bbb'),
        ('a\nb', 'a\nb'),
        ('', None),
        (None, None),
    ])
    def test_(self, text, result):
        assert result == CleanText()(text)

    def test_with_empty_value(self):
        assert 'empty' == CleanText(empty_value='empty')('')

    @pytest.mark.parametrize(['text', 'result'], [
        ('a\nb', 'a b'),
        ('a\rb', 'a b'),
        ('a\n\rb', 'a b'),
        ('a\r\nb', 'a b'),
    ])
    def test_with_remove_line_breaks(self, text, result):
        assert result == CleanText(remove_line_breaks=True)(text)


class TestEquals(object):
    def test_(self):
        assert Equals('AAA')('AAA')
        assert not Equals('AAA')('AAABBBCCC')
        assert not Equals('AAA')(None)


class TestContains(object):
    def test_(self):
        assert Contains('BBB')('AAABBBCCC')
        assert not Contains('DDD')('AAABBBCCC')
        assert not Contains('AAA')(None)


class TestFetch(object):
    def test_fetch(self):
        pattern = r'\d+'
        result = Fetch(pattern)('10, 20, 30')
        assert '10' == result

    def test_fetch_with_group(self):
        pattern = r'(\d+), (\d+), (\d+)'
        result = Fetch(pattern)('10, 20, 30')
        assert ('10', '20', '30') == result

    def test_fetch_with_labeled_group(self):
        pattern = r'(?P<type>\w+): (?P<count>\d+)'
        result = Fetch(pattern)('Cat: 10, Dog: 20')
        assert {'type': 'Cat', 'count': '10'} == result

    def test_fetch_with_none(self):
        pattern = r'(?P<type>\w+): (?P<count>\d+)'
        result = Fetch(pattern)(None)
        assert result is None

    def test_fetch_all(self):
        pattern = r'\d+'
        result = Fetch(pattern, all=True)('10, 20, 30')
        assert ['10', '20', '30'] == result

    def test_fetch_all_with_group(self):
        pattern = r'(\d+), (\d+), (\d+)'
        result = Fetch(pattern, all=True)('10, 20, 30')
        assert [('10', '20', '30')] == result

    def test_fetch_all_with_labeled_group(self):
        pattern = r'(?P<type>\w+): (?P<count>\d+)'
        result = Fetch(pattern, all=True)('Cat: 10, Dog: 20')
        assert [
            {'type': 'Cat', 'count': '10'},
            {'type': 'Dog', 'count': '20'},
        ] == result

    def test_fetch_all_with_none(self):
        pattern = r'(?P<type>\w+): (?P<count>\d+)'
        result = Fetch(pattern, all=True)(None)
        assert result is None


class TestReplace(object):
    def test_(self):
        pattern = r'A+'
        replace = 'B'
        result = Replace(pattern, replace)('AAAAAABBBAAAA')
        assert 'BBBBB' == result

    def test_with_none(self):
        pattern = r'A+'
        replace = 'B'
        result = Replace(pattern, replace)(None)
        assert result is None


class TestJoin(object):
    def test_(self):
        assert 'A,B,C' == Join(',')(['A', 'B', 'C'])

    def test_with_none(self):
        assert Join(',')(None) is None


class TestNormalize(object):
    def test_(self):
        assert '12AB&%' == Normalize()(u'１２ＡＢ＆％')

    def test_with_none(self):
        assert Normalize()(None) is None


class TestRenameKey(object):
    def test_(self):
        name_map = {'AAA': 'XXX', 'BBB': 'YYY'}
        result = RenameKey(name_map)({'AAA': '10', 'BBB': '20'})
        assert {'XXX': '10', 'YYY': '20'} == result

    def test_with_none(self):
        name_map = {'AAA': 'XXX', 'BBB': 'YYY'}
        result = RenameKey(name_map)(None)
        assert result is None


class TestFilterDict(object):
    def test_(self):
        keys = ['AAA']
        result = FilterDict(keys)({'AAA': '10', 'BBB': '20'})
        assert {'AAA': '10'} == result

    def test_with_ignore(self):
        keys = ['AAA']
        result = FilterDict(keys, ignore=True)({'AAA': '10', 'BBB': '20'})
        assert {'BBB': '20'} == result

    def test_with_none(self):
        keys = ['AAA']
        result = FilterDict(keys)(None)
        assert result is None


class TestPartial(object):
    def test_(self):
        def add(a, b):
            return a + b
        result = Partial(add, b=10)(5)
        assert 15 == result

    def test_with_value_arg_name(self):
        def add(a, b, c):
            return a + b + c
        result = Partial(add, 'b', a=10, c=30)(20)
        assert 60 == result


class TestDateTime(object):
    @pytest.mark.parametrize(['value', 'result'], [
        ('2001', datetime(2001, 1, 1)),
        ('2001-02', datetime(2001, 2, 1)),
        ('2001-02-03', datetime(2001, 2, 3)),
        ('2001-02-03 04:05:06', datetime(2001, 2, 3, 4, 5, 6)),
        ('2001-02-03T04:05:06+09:00', datetime(2001, 2, 3, 4, 5, 6, 0, tzoffset(None, 3600 * 9))),
    ])
    def test_(self, value, result):
        dt = DateTime()(value)
        assert dt == result

    @pytest.mark.parametrize(['value', 'format', 'result'], [
        ('2001', '%Y', datetime(2001, 1, 1)),
        ('02 2001', '%m %Y', datetime(2001, 2, 1)),
    ])
    def test_with_format(self, value, format, result):
        dt = DateTime(format=format)(value)
        assert dt == result

    def test_with_truncate_time(self):
        dt = DateTime(truncate_time=True)('2001-02-03 04:05:06')
        assert dt == date(2001, 2, 3)

    def test_with_truncate_timezone(self):
        dt = DateTime(truncate_timezone=True)('2001-02-03T04:05:06+09:00')
        assert dt.tzinfo is None


class TestBool(object):
    @pytest.mark.parametrize(['value', 'result'], [
        ('true', True),
        ('false', False),
    ])
    def test_(self, value, result):
        assert result == Bool()(value)

    @pytest.mark.parametrize(['value', 'result'], [
        ('OK', True),
        ('ok', True),
        ('true', False),
        ('ng', False),
    ])
    def test_with_true_values(self, value, result):
        assert result == Bool('OK', 'ok')(value)

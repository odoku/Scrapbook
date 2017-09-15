# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import pytest

from scrapbook.filters import (
    clean_text,
    Contains,
    Equals,
    Fetch,
    FilterDict,
    Join,
    Map,
    Normalize,
    RenameKey,
    Replace,
    take_first,
    through,
)


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


class TestThrough(object):
    def test_(self):
        value = 100
        assert value == through(value)


class TestTakeFirst(object):
    def test_(self):
        assert 1 == take_first([1, 2, 3, 4])

    def test_with_list_include_empty_value(self):
        assert 0 == take_first([None, '', 0, 1])


class TestCleanText(object):
    @pytest.mark.parametrize(['text', 'result'], [
        ('  aaa  ', 'aaa'),
        ('<p>aaa</p>', 'aaa'),
        ('&amp;', '&'),
        ('aa       bb', 'aa bb'),
        ('<p>  aaa  &amp;  bbb  </p>', 'aaa & bbb'),
    ])
    def test_(self, text, result):
        assert result == clean_text(text)


class TestEquals(object):
    def test_(self):
        assert Equals('AAA')('AAA')
        assert not Equals('AAA')('AAABBBCCC')


class TestContains(object):
    def test_(self):
        assert Contains('BBB')('AAABBBCCC')
        assert not Contains('DDD')('AAABBBCCC')


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


class TestReplace(object):
    def test_(self):
        pattern = r'A+'
        replace = 'B'
        result = Replace(pattern, replace)('AAAAAABBBAAAA')
        assert 'BBBBB' == result


class TestJoin(object):
    def test_(self):
        assert 'A,B,C' == Join(',')(['A', 'B', 'C'])


class TestNormalize(object):
    def test_(self):
        assert '12AB&%' == Normalize()('１２ＡＢ＆％')


class TestRenameKey(object):
    def test_(self):
        name_map = {'AAA': 'XXX', 'BBB': 'YYY'}
        result = RenameKey(name_map)({'AAA': '10', 'BBB': '20'})
        assert {'XXX': '10', 'YYY': '20'} == result


class TestFilterDict(object):
    def test_(self):
        keys = ['AAA']
        result = FilterDict(keys)({'AAA': '10', 'BBB': '20'})
        assert {'AAA': '10'} == result

    def test_with_ignore(self):
        keys = ['AAA']
        result = FilterDict(keys, ignore=True)({'AAA': '10', 'BBB': '20'})
        assert {'BBB': '20'} == result

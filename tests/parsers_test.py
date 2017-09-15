# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os

from parsel import Selector
import pytest
import six

from scrapbook.parsers import (
    ParseDefinitionList,
    ParseList,
    ParseTable,
)


basepath = os.path.dirname(os.path.abspath(__file__))
html_dir = os.path.join(basepath, 'html')


def load_html(filepath):
    filepath = os.path.join(html_dir, filepath)
    with open(filepath) as fp:
        return six.u(fp.read())


class TestParseTable(object):
    @pytest.mark.parametrize('filepath', [
        'parse_table/table.html',
        'parse_table/table_has_thead_and_tbody.html',
    ])
    def test_(self, filepath):
        selector = Selector(load_html(filepath))
        result = ParseTable()(selector.xpath('//table'))
        expected = [
            ['Company', 'Contact', 'Country'],
            ['Alfreds Futterkiste', 'Maria Anders', 'Germany'],
            ['Centro comercial Moctezuma', 'Francisco Chang', 'Mexico'],
            ['Ernst Handel', 'Roland Mendel', 'Austria'],
            ['Island Trading', 'Helen Bennett', 'UK'],
            ['Laughing Bacchus Winecellars', 'Yoshi Tannamuri', 'Canada'],
            ['Magazzini Alimentari Riuniti', 'Giovanni Rovelli', None],
        ]
        assert expected == result

    @pytest.mark.parametrize('filepath', [
        'parse_table/table.html',
        'parse_table/table_has_thead_and_tbody.html',
    ])
    def test_with_table_has_header(self, filepath):
        selector = Selector(load_html(filepath))
        result = ParseTable(has_header=True)(selector.xpath('//table'))
        expected = [
            {
                'Company': 'Alfreds Futterkiste',
                'Contact': 'Maria Anders',
                'Country': 'Germany',
            },
            {
                'Company': 'Centro comercial Moctezuma',
                'Contact': 'Francisco Chang',
                'Country': 'Mexico',
            },
            {
                'Company': 'Ernst Handel',
                'Contact': 'Roland Mendel',
                'Country': 'Austria',
            },
            {
                'Company': 'Island Trading',
                'Contact': 'Helen Bennett',
                'Country': 'UK',
            },
            {
                'Company': 'Laughing Bacchus Winecellars',
                'Contact': 'Yoshi Tannamuri',
                'Country': 'Canada',
            },
            {
                'Company': 'Magazzini Alimentari Riuniti',
                'Contact': 'Giovanni Rovelli',
                'Country': None,
            },
        ]
        assert expected == result


class TestParseList(object):
    @pytest.mark.parametrize('filepath', [
        'parse_list/unordered_list.html',
        'parse_list/ordered_list.html',
    ])
    def test_(self, filepath):
        selector = Selector(load_html(filepath))
        result = ParseList()(selector.xpath('//ul | //ol'))
        expected = ['Coffee', 'Tea', 'Milk']
        assert expected == result


class TestParseDefinitionList(object):
    def test_(self):
        selector = Selector(load_html('parse_definition_list/definition_list.html'))
        result = ParseDefinitionList()(selector.xpath('//dl'))
        expected = {
            'Coffee': '- black hot drink',
            'Milk': [
                '- white cold drink',
                '- white hot drink',
            ],
        }
        assert expected == result

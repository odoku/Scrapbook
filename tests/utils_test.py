# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import pytest

from scrapbook.utils import merge_dict, remove_tags


class TestMergeDict(object):
    def test_(self):
        a = {'AAA': 10, 'BBB': 20}
        b = {'CCC': 30, 'DDD': 40}
        c = {'EEE': 50, 'FFF': 60}
        merged = merge_dict(a, b, c)
        assert all([
            a['AAA'] == merged['AAA'],
            a['BBB'] == merged['BBB'],
            b['CCC'] == merged['CCC'],
            b['DDD'] == merged['DDD'],
            c['EEE'] == merged['EEE'],
            c['FFF'] == merged['FFF'],
        ])


class TestRemoveTag(object):
    @pytest.mark.parametrize(['tag', 'text'], [
        ('<p>aaa</p>', 'aaa'),
        ('<a href="http://google.com">aaa</a>', 'aaa'),
        ('<p>aaa<br>bbb</p>', 'aaabbb'),
        ('<p><span>aaa</span></p>', 'aaa'),
    ])
    def test_(self, tag, text):
        assert text == remove_tags(tag)

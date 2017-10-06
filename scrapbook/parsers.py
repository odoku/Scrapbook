# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from .filters import clean_text


class First(object):
    def __call__(self, selector):
        return selector.extract_first()


class All(object):
    def __call__(self, selector):
        return selector.extract()


class ParseTable(object):
    def __init__(self, has_header=False):
        self.has_header = has_header

    def __call__(self, selector):
        rows = selector.xpath('.//tr')

        if self.has_header:
            return self._parse_as_dict(rows)
        return self._parse_as_list(rows)

    def _parse_as_list(self, rows):
        data = []
        for row in rows:
            data.append([
                clean_text(column.xpath('.//text()').extract_first())
                for column in row.xpath('./*')
            ])

        return data

    def _parse_as_dict(self, rows):
        keys = [
            clean_text(e.xpath('.//text()').extract_first())
            for e in rows[0].xpath('./*')
        ]

        data = []
        for row in rows[1:]:
            data.append({
                k: clean_text(row.xpath('./*[{}]//text()'.format(i + 1)).extract_first())
                for i, k in enumerate(keys)
            })

        return data


class ParseList(object):
    def __call__(self, selector):
        return [
            clean_text(v)
            for v in selector.xpath('./li/text()').extract()
        ]


class ParseDefinitionList(object):
    def __call__(self, selector):
        data = {}

        for s in selector.xpath('./dt | ./dd'):
            tag = s.extract()
            if tag.startswith('<dt>'):
                current_key = clean_text(tag)
                data[current_key] = []
            else:
                try:
                    data[current_key].append(clean_text(tag))
                except NameError:
                    pass

        return {
            k: v if len(v) > 1 else v[0]
            for k, v in data.items()
        }

# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re
import six


def merge_dict(*dicts):
    return six.moves.reduce(lambda a, b: dict(a, **b), dicts)


def remove_tags(text):
    pattern = re.compile(r'<[^>]+>')
    return pattern.sub('', text)

=====================================================================
Filters
=====================================================================

By using various filters for Element or Content, you can set the retrieved value to your preferred format.

.. code-block:: python

    el = Element(
        xpath='//html/body/ul/li',
        filter=[
            Map(
                clean_text,
                Normalize(),
                Fetch(r'(?P<key>.+): (?P<count>\d+)'),
            ),
            lambda values: {v['key']: v['count'] for v in values},
        ],
    )

Map
=====================================================================

Execute the filter specified by argument for each element of list or dict.

.. code-block:: python

    filter = Map(clean_text, Equals('yes'))
    result = filter({
        'AAA': '    no    ',
        'BBB': '    yes    ',
        'CCC': '    <strong>   yes  <strong>    ',
    })

    assert {
        'AAA': False,
        'BBB': True,
        'CCC': True,
    } == result

It is also possible to call functions defined in the Content class.

.. code-block:: python

    class Page(Content):
        links = Element(xpath='//a/@href', parser=All(), filter=Map('filter_link'))

        def filter_link(self, value):
            url = urlparse(value)
            return url.netloc

    page = Page(xpath='')
    result = page.parse('''
        <a href="http://google.com">Google</a>
        <a href="http://twitter.com">Twitter</a>
        <a href="http://facebook.com">Facebook</a>
    ''')

    assert {
        'links': [
            'google.com',
            'twitter.com',
            'facebook.com',
        ]
    } == result


Through
=====================================================================

It returns the passed value as it is.
This is the default filter for Element / Content.

.. code-block:: python

    assert 10 == through(10)


TakeFirst
=====================================================================

Get the first element of list.
However, if the acquired element is None or '', the next element is acquired.

.. code-block:: python

    assert 10 == take_first([None, '', 10])


CleanText
=====================================================================

Perform the following cleaning process on the character string.

* Removing HTML tags
* Decode HTML special characters
* Make 2 spaces or more of one contiguous space
* Remove Whitespace before and after

.. code-block:: python

    assert 'aaa & bbb' == clean_text('<p>  aaa  &amp;  bbb  </p>')


Equals
=====================================================================

Returns True if the value matches the specified string.

.. code-block:: python

    equals = Equals('yes')
    assert equals('yes')


Contains
=====================================================================

Returns True if the specified character string is included in the character string.

.. code-block:: python

    contains = Contains('B')
    assert contains('ABC')


Fetch
=====================================================================

Extract values from strings using regular expressions.

.. code-block:: python

    fetch = Fetch(r'\d+')
    assert '100' == fetch('Price: $100')

You can also get all matched values.

.. code-block:: python

    fetch = Fetch(r'\d+', all=True)
    assert ['100', '20'] == fetch('Price: $100, Amount: 20')

It can also be returned as dict by specifying label.

.. code-block:: python

    fetch = Fetch(r'Price: $(?P<price>\d+), Amount: (?P<amount>\d+)')
    assert {'price': '100', 'amount': '20'} == fetch('Price: $100, Amount: 20')


Replace
=====================================================================

You can replace the string using regular expressions.

.. code-block:: python

    replace = Replace(r'A+', 'A')
    assert 'ABC' == replace('AAAAABC')


Join
=====================================================================

Returns a string formed by combining list with separator.

.. code-block:: python

    join = Join(',')
    assert 'A,B,C' == join(['A', 'B', 'C'])


Normalize
=====================================================================

Returns the normalized string.

.. code-block:: python

    normalize = scrapbook.filters.normalize  # == scrapbook.filters.Normalize('NFKD')
    assert '12AB&%' == normalize('１２ＡＢ＆％')


RenameKey
=====================================================================

Rename the dict's key.

.. code-block:: python

    rename_key = RenameKey({'AAA': 'BBB'})
    assert {'BBB': 10} == rename_key({'AAA': 10})


FilterDict
=====================================================================

Returns dict with only the specified key.

.. code-block:: python

    filter_dict = FilterDict(['AAA', 'BBB'])
    assert {'AAA': 10, 'BBB': 20} == filter_dict({'AAA': 10, 'BBB': 20, 'CCC': 30})

Other than the specified key can be returned.

.. code-block:: python

    filter_dict = FilterDict(['AAA', 'BBB'], ignore=True)
    assert {'CCC': 30} == filter_dict({'AAA': 10, 'BBB': 20, 'CCC': 30})

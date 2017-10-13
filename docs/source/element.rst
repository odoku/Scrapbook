=====================================================================
Element
=====================================================================

Get the element specified by xpath from HTML.

.. code-block:: python

    from scrapbook import Element
    import requests

    response = requests.get('https://twitter.com/odoku')
    screen_name = Element(
        xpath='//*[@id="page-container"]/div[2]/div/div'
              '/div[1]/div/div/div/div[1]/h2/a/span/b/text()',
    )
    name = screen_name.parse(response.text)

    print(name)


Arguments
=====================================================================

.. code-block:: python

    Element(
        xpath: Optional[str] = None,
        filter: Union[Callable, str, list[Union[Callable, str]] = scrapbook.filters.through,
        parser: Union[Callable, str] = scrapbook.parsers.First(),
    )

xpath
---------------------------------------------------------------------

Specify the xpath of the element you want to retrieve.

.. code-block:: python

    el = Element(xpath='/html/body/p/text()')
    texts = el.parse()

filter
---------------------------------------------------------------------

Any processing can be performed on the acquired value.

.. code-block:: python

    def clean(values):
        return [v.strip() for v values]

    el = Element(xpath='/html/body/p/text()', filter=clean)


More than one filter can be specified.

.. code-block:: python

    def to_int(value):
        return [int(v.strip()) for v values]

    Element(xpath='/html/body/p/text()', filter=[to_int, sum])

parser
---------------------------------------------------------------------

You can specify a function to parse the element specified by xpath.

.. code-block:: python

    def parse_link(selector):
        # selector is parsel.SelectorList
        return {
            'url': selector.xpath('./@href').extract_first(),
            'text': selector.xpath('./text()').extract_first(),
        }

    Element(xpath='/html/body/a', parser=parse_link)


Methods
=====================================================================


parse
---------------------------------------------------------------------

.. code-block:: python

    parse(html: Union[str, parsel.Selector, parsel.SelectorList])

Parse html.

.. code-block:: python

    html = '<html><body><p>Hello!</p></body></html>'
    el = Element(xpath='/html/body/p/text()')
    text = el.parse()  # Hello!

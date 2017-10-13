=====================================================================
Content
=====================================================================

You can handle multiple Elements at once.

.. code-block:: python

    from scrapbook import Element, Content
    import requests


    class Twitter(Content):
        username = Element(
            xpath='//*[@id="page-container"]/div[2]/div/div'
                  '/div[1]/div/div/div/div[1]/h2/a/span/b/text()',
        )
        screen_name = Element(
            xpath='//*[@id="page-container"]/div[2]/div/div/'
                  'div[1]/div/div/div/div[1]/h1/a',
        )


    response = requests.get('https://twitter.com/odoku')
    data = Twitter().parse(response.text)

    print(data)


Include filter/parser functions
=====================================================================

You can define the filter / parser specified in the Element in the Content.

.. code-block:: python

    class Page(Content):
        username = Element(
            xpath='//*[@id="username"]',
            parse='parse_username',
            filter='filter_username',
        )

        def parse_username(self, selector):
            return selector.xpath('./text()').extract_first()

        def filter_username(self, value):
            return value.replace('username: ', '').strip()


Nest
=====================================================================

Content can be nested.

.. code-block:: python

    class Profile(Content):
        username = Element(xpath='./path/to/username/text()')
        screen_name = Element(xpath='./path/to/screen_name/text()')

    class Page(Content):
        profile = Profile(xpath='//*[@id="profile"]')


Inheritance
=====================================================================

Content supports inheritance.

.. code-block:: python

    class Common(Content):
        title = Element(xpath='/path/to/title/text()')

    class ProjectPage(Common):
        name = Element(xpath='/path/to/name/text()')

    class TeamPage(Common):
        name = Element(xpath='/path/to/name/text()')


Arguments
=====================================================================

.. code-block:: python

    Content(
        xpath: Optional[str] = None,
        filter: Union[Callable, str, list[Union[Callable, str]] = scrapbook.filters.through,
    )

xpath
---------------------------------------------------------------------

Specify the xpath of the element you want to parse.
For the included Element, the element of the specified xpath is passed.

.. code-block:: python

    class Page(Content):
        username = Element(xpath='./span[1]/text()')

    page = Page(xpath='//*[@id="profile"]')
    data = page.parse(html)

filter
---------------------------------------------------------------------

You can do arbitrary processing on the acquired value.
As with Element, multiple filters can be specified.

.. code-block:: python

    class Page(Content):
        username = Element(xpath='./span[1]/text()')

    def rename(value):
        alias = {'username': 'account'}
        return {alias.get(k, k): v for k, v in value.items()}

    page = Page(xpath='//*[@id="profile"]', filter=rename)
    data = page.parse(html)


Methods
=====================================================================

parse
---------------------------------------------------------------------

.. code-block:: python

    parse(
        html: Union[str, parsel.Selector, parsel.SelectorList],
        object: Optional[Any],
    )

Parse html.

.. code-block:: python

    class Page(Content):
        content = Element(xpath='/html/body/p/text()')

    html = '<html><body><p>Hello!</p></body></html>'
    page = Page()
    data = page.parse(html)  # {'content': 'Hello!'}

Map the value to the object specified in the object argument.

.. code-block:: python

    instance = PageModel()
    page = Page()
    instance = page.parse(html, object=instance)

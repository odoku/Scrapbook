=====================================================================
Scrapbook
=====================================================================

Scrapbook is simple scraping library.

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
                  'div[1]/div/div/div/div[1]/h1/a/text()',
        )


    response = requests.get('https://twitter.com/odoku')
    data = Twitter().parse(response.text)

    print(data)


Requirements
=====================================================================

- Python 2.7 or Python 3.3+


Installation
=====================================================================

.. code-block:: bash

    pip install scrapbook


Page
=====================================================================

.. toctree::
    :maxdepth: 2

    element
    content
    filters
    parsers

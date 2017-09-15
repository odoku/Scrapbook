Scrapbook
=================================================

[![CircleCI](https://circleci.com/gh/odoku/Scrapbook/tree/master.svg?style=svg)](https://circleci.com/gh/odoku/Scrapbook/tree/master)

Scrapbook is simple scraping library.


```python
from scrapbook import Element, Content
from scrapbook.filters import take_first
import requests


class Twitter(Content):
    username = Element(
        xpath='//*[@id="page-container"]/div[2]/div/div'
              '/div[1]/div/div/div/div[1]/h2/a/span/b/text()',
        filter=take_first,
    )
    screen_name = Element(
        xpath='//*[@id="page-container"]/div[2]/div/div/'
              'div[1]/div/div/div/div[1]/h1/a',
        filter=take_first,
    )


response = requests.get('https://twitter.com/odoku')
data = Twitter().parse(response.text)

print(data)
```



Requirements
-------------------------------------------------

- Python 2.7 or Python 3.3+


Installation
-------------------------------------------------

```
pip install scrapbook
```


Document
-------------------------------------------------

https://scrapbook.readthedocs.org

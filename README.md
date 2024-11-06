Scrapbook
=================================================

Scrapbook is simple scraping library.


```python
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
```



Requirements
-------------------------------------------------

- Python 3.9+


Installation
-------------------------------------------------

```
pip install scrapbook
```


Document
-------------------------------------------------

https://scrapbook.readthedocs.org

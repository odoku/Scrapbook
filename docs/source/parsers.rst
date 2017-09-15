=====================================================================
Parsers
=====================================================================


Extract
=====================================================================

It converts all elements matching xpath into text and returns it as list.
This is the default parser of Element.

.. code-block:: html

    <html>
        <body>
            <p>
                AAA
                <br>
                BBB
                <br>
                CCCC
            </p>
        </body>
    </html>


.. code-block:: python

    el = Element(xpath='//html/body/p/text()', parser=extract)
    texts = el.parse(html)

    assert ['AAA', 'BBB', 'CCC'] == texts


ParseTable
=====================================================================

Parse basic table and return it as list.

.. code-block:: html

    <html>
        <body>
            <table>
                <tr>
                    <th>Company</th>
                    <th>Contact</th>
                    <th>Country</th>
                </tr>
                <tr>
                    <td>Alfreds Futterkiste</td>
                    <td>Maria Anders</td>
                    <td>Germany</td>
                </tr>
                <tr>
                    <td>Centro comercial Moctezuma</td>
                    <td>Francisco Chang</td>
                    <td>Mexico</td>
                </tr>
            </table>
        </body>
    </html>

.. code-block:: python

    el = Element(xpath='//html/body/table', parser=ParseTable())
    data = el.parse(html)

    assert [
        ['Alfreds Futterkiste', 'Maria Anders', 'Germany'],
        ['Centro comercial Moctezuma', 'Francisco Chang', 'Mexico'],
    ] == data

If there is a header in table, passing `has_header = True` will return dict with the value of header as key.

.. code-block:: python

    el = Element(xpath='//html/body/table', parser=ParseTable(has_header=True))
    data = el.parse(html)

    assert [
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
    ] == data


ParseList
=====================================================================

Parse elements such as `<ul>` and `<ol>` and return them as list.

.. code-block:: html

    <html>
        <body>
            <ol>
                <li>Coffee</li>
                <li>Tea</li>
                <li>Milk</li>
            </ol>
        </body>
    </html>

.. code-block:: python

    el = Element(xpath='//html/body/ol', parser=ParseList())
    data = el.parse(html)

    assert ['Coffee', 'Tea', 'Milk'] == data


ParseDefinitionList
=====================================================================

It parses `<dl>` and returns it as dict.

.. code-block:: html

    <html>
        <body>
            <dl>
                <dt>Coffee</dt>
                <dd>black hot drink</dd>
                <dt>Milk</dt>
                <dd>white cold drink</dd>
                <dd>white hot drink</dd>
            </dl>
        </body>
    </html>

.. code-block:: python

    el = Element(xpath='//html/body/dl', parser=ParseDefinitionList())
    data = el.parse(html)

    assert {
        'Coffee': 'black hot drink',
        'Milk': [
            'white cold drink',
            'white hot drink',
        ]
    } = data

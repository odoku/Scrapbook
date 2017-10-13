# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='scrapbook',
    version='0.2.0',
    description='Simple scraping library.',
    author='odoku',
    author_email='masashi.onogawa@wamw.jp',
    keywords='scraping',
    url='https://github.com/odoku/scrapbook',
    license='MIT',

    packages=['scrapbook'],
    install_requires=[
        'parsel>=1.2.0',
        'six>=1.10.0',
    ],
    extras_require={
        'test': [
            'flake8>=3.4.1',
            'pytest>=3.2.2',
            'pytest-mock>=1.6.3'
        ],
    }
)

import asyncio
import pytest

from xbus import client


def test_get():
    c = client.ClientConf({'a': 'a', 'a.b': 'a.b', 'b': {'c': 'b.c'}})
    assert c['a'] == 'a'
    assert c['a.b'] == 'a.b'
    assert c['b.c'] == 'b.c'


def test_set():
    c = client.ClientConf({'a': 'a', 'a.b': 'a.b', 'b': {'c': 'b.c'}})

    c['a.b'] = 'new a.b'
    assert c['a.b'] == 'new a.b'

    c['b.c'] = 'new b.c'
    assert c['b.c'] == 'new b.c'

    c['c.a'] = 'c.a'
    assert c['c.a'] == 'c.a'

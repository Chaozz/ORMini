from unittest import TestCase
from ormini.utils import *


class DictTests(TestCase):
    def test_dot(self):
        d = Dict()
        d['foo'] = 1
        d['bar'] = 2
        self.assertEqual(1, d.foo)
        self.assertEqual(2, d.bar)
        self.assertRaises(AttributeError, lambda: d.x)

    def test_kw(self):
        d = Dict(foo=1, bar=2)
        self.assertEqual(1, d.foo)
        self.assertEqual(2, d.bar)
        self.assertRaises(AttributeError, lambda: d.x)

    def test_kv(self):
        d = Dict(('foo', 'bar'), (1, 2))
        self.assertEqual(1, d.foo)
        self.assertEqual(2, d.bar)
        self.assertRaises(AttributeError, lambda: d.x)

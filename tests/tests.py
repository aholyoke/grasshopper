import unittest
from grasshopper import Framework


def i(**kwargs): pass


def a(**kwargs): pass


def b(**kwargs): pass


def c(**kwargs): pass


def d(**kwargs): pass


def e(**kwargs): pass


def f(**kwargs): pass


def g(**kwargs): pass


def h(**kwargs): pass


class TestRouting(unittest.TestCase):

    def setUp(self):
        app = Framework({'a': 1, 'b': [2, 3]})
        app.get('/', i)
        app.get('/a/', a)
        app.get('/b', b)
        app.post('/b', b)
        app.get('/b/*', b)
        app.get('/b/*/d', d)
        app.get('/b/*/e', e)
        app.get('/b/f/g', g)
        app.get('/c', c)
        app.get('/c/f', f)
        app.get('/c/f/*', h)
        self.app = app

    def test_basic(self):
        self.assertEqual(self.app.lookup('a', 'GET'), a)
        self.assertEqual(self.app.lookup('/a', 'GET'), a)
        self.assertEqual(self.app.lookup('a/', 'GET'), a)
        self.assertEqual(self.app.lookup('/a/', 'GET'), a)

        self.assertEqual(self.app.lookup('b', 'GET'), b)
        self.assertEqual(self.app.lookup('/b', 'GET'), b)
        self.assertEqual(self.app.lookup('b/', 'GET'), b)
        self.assertEqual(self.app.lookup('/b/', 'GET'), b)

    def test_nested(self):
        self.assertEqual(self.app.lookup('b/f/g', 'GET'), g)
        self.assertEqual(self.app.lookup('/b/f/g', 'GET'), g)
        self.assertEqual(self.app.lookup('b/f/g/', 'GET'), g)
        self.assertEqual(self.app.lookup('/b/f/g/', 'GET'), g)

    def test_wildcards(self):
        self.assertEqual(self.app.lookup('b/*/e', 'GET'), e)
        self.assertEqual(self.app.lookup('b/x/e', 'GET'), e)
        self.assertEqual(self.app.lookup('b/abc/e', 'GET'), e)
        self.assertEqual(self.app.lookup('/b/abc/e', 'GET'), e)
        self.assertEqual(self.app.lookup('/b/abc/e/', 'GET'), e)
        self.assertEqual(self.app.lookup('/b/abc', 'GET'), b)
        self.assertEqual(self.app.lookup('/c/f', 'GET'), f)
        self.assertEqual(self.app.lookup('/c/f/', 'GET'), f)
        self.assertEqual(self.app.lookup('/c/f/abc', 'GET'), h)

    def test_slash_agnostic(self):
        self.assertEqual(
            self.app.lookup('a', 'GET'),
            self.app.lookup('/a/', 'GET'))
        self.assertEqual(
            self.app.lookup('a/', 'GET'),
            self.app.lookup('/a/', 'GET'))
        self.assertEqual(
            self.app.lookup('/a', 'GET'),
            self.app.lookup('/a/', 'GET'))

        self.assertEqual(
            self.app.lookup('a', 'GET'),
            self.app.lookup('/a', 'GET'))
        self.assertEqual(
            self.app.lookup('a/', 'GET'),
            self.app.lookup('/a', 'GET'))

        self.assertEqual(
            self.app.lookup('a', 'GET'),
            self.app.lookup('a/', 'GET'))
        self.assertEqual(
            self.app.lookup('/a', 'GET'),
            self.app.lookup('a/', 'GET'))

if __name__ == "__main__":
    unittest.main()

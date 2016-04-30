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


class TestLookup(unittest.TestCase):

    def setUp(self):
        app = Framework()
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


class TestRouting(unittest.TestCase):
    def setUp(self):
        self.app = Framework()

    def test_order_doesnt_matter(self):
        from itertools import permutations
        routes = [
            ('/a', a),
            ('/a/*', b),
            ('/a/c', c),
        ]
        routes_permutations = permutations(routes, len(routes))
        for i, routes in enumerate(routes_permutations):
            app = Framework({'app': i})
            for route in routes:
                app.get(*route)
            self.assertEqual(app.lookup('/a', 'GET'), a, i)
            self.assertEqual(app.lookup('/a/x', 'GET'), b, i)
            self.assertEqual(app.lookup('/a/c', 'GET'), c, i)


if __name__ == "__main__":
    unittest.main()

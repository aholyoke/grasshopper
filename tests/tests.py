import unittest
from grasshopper import Framework
from itertools import permutations


def i(**kwargs): pass


def a(**kwargs): pass


def b(**kwargs): pass


def c(**kwargs): pass


def d(**kwargs): pass


def e(**kwargs): pass


def f(**kwargs): pass


def g(**kwargs): pass


def h(**kwargs): pass


def _make_app(routings, settings=None):
    if settings is None:
        settings = {}
    app = Framework(**settings)
    for func, url, view in routings:
        getattr(app, func)(url, view)
    return app


class TestLookup(unittest.TestCase):

    def setUp(self):
        app = Framework(validators={'*': str})
        app.get('/', i)
        app.get('/a/', a)
        app.get('/b', b)
        app.post('/b', b)
        app.get('/b/<*>', b)
        app.get('/b/<*>/d', d)
        app.get('/b/<*>/e', e)
        app.get('/b/f/g', g)
        app.get('/c', c)
        app.get('/c/f', f)
        app.get('/c/f/<*>', h)
        app.post('/c/f/<*>/a/<*>', a)
        app.delete('/c/f/<*>/a/<*>/b', b)
        self.app = app

    def test_basic(self):
        self.assertEqual(self.app.lookup('a', 'GET')[0], a)
        self.assertEqual(self.app.lookup('/a', 'GET')[0], a)
        self.assertEqual(self.app.lookup('a/', 'GET')[0], a)
        self.assertEqual(self.app.lookup('/a/', 'GET')[0], a)

        self.assertEqual(self.app.lookup('b', 'GET')[0], b)
        self.assertEqual(self.app.lookup('/b', 'GET')[0], b)
        self.assertEqual(self.app.lookup('b/', 'GET')[0], b)
        self.assertEqual(self.app.lookup('/b/', 'GET')[0], b)

    def test_nested(self):
        self.assertEqual(self.app.lookup('b/f/g', 'GET')[0], g)
        self.assertEqual(self.app.lookup('/b/f/g', 'GET')[0], g)
        self.assertEqual(self.app.lookup('b/f/g/', 'GET')[0], g)
        self.assertEqual(self.app.lookup('/b/f/g/', 'GET')[0], g)

    def test_wildcards(self):
        self.assertEqual(self.app.lookup('b/*/e', 'GET')[0], e)
        self.assertEqual(self.app.lookup('b/x/e', 'GET')[0], e)
        self.assertEqual(self.app.lookup('b/abc/e', 'GET')[0], e)
        self.assertEqual(self.app.lookup('/b/abc/e', 'GET')[0], e)
        self.assertEqual(self.app.lookup('/b/abc/e/', 'GET')[0], e)
        self.assertEqual(self.app.lookup('/b/abc', 'GET')[0], b)
        self.assertEqual(self.app.lookup('/c/f', 'GET')[0], f)
        self.assertEqual(self.app.lookup('/c/f/', 'GET')[0], f)
        self.assertEqual(self.app.lookup('/c/f/abc', 'GET')[0], h)

    def test_slash_agnostic(self):
        self.assertEqual(
            self.app.lookup('a', 'GET')[0],
            self.app.lookup('/a/', 'GET')[0])
        self.assertEqual(
            self.app.lookup('a/', 'GET')[0],
            self.app.lookup('/a/', 'GET')[0])
        self.assertEqual(
            self.app.lookup('/a', 'GET')[0],
            self.app.lookup('/a/', 'GET')[0])

        self.assertEqual(
            self.app.lookup('a', 'GET')[0],
            self.app.lookup('/a', 'GET')[0])
        self.assertEqual(
            self.app.lookup('a/', 'GET')[0],
            self.app.lookup('/a', 'GET')[0])

        self.assertEqual(
            self.app.lookup('a', 'GET')[0],
            self.app.lookup('a/', 'GET')[0])
        self.assertEqual(
            self.app.lookup('/a', 'GET')[0],
            self.app.lookup('a/', 'GET')[0])

    def test_wildcard_passing_arguments(self):
        self.assertEqual(
            self.app.lookup('b/abc/e', 'GET')[1],
            ['abc'])
        self.assertEqual(
            self.app.lookup('c/f/77e/a/something', 'POST')[1],
            ['77e', 'something'])
        self.assertEqual(
            self.app.lookup('c/f/77e/a/something/b', 'DELETE')[1],
            ['77e', 'something'])


class Test404s(unittest.TestCase):
    def setUp(self):
        self.app = Framework(validators={'*': str})
        self.app.get('a/<*>', a)
        self.app.post('/c/f/<*>/a/<*>', a)
        self.app.put('/a/b/c', c)
        self.app.delete('/a/<*>/c', c)

    def test_wildcard_termination(self):
        self.assertEqual(self.app.lookup('/a', 'GET'), (None, []))
        self.assertEqual(self.app.lookup('c/f/x/a', 'POST'), (None, []))
        self.assertEqual(self.app.lookup('a/c/', 'DELETE'), (None, []))

    def test_wrong_url(self):
        self.assertEqual(self.app.lookup('/a/b', 'PUT'), (None, []))
        self.assertEqual(self.app.lookup('/a/b/c/d', 'PUT'), (None, []))
        self.assertEqual(self.app.lookup('/b/c', 'PUT'), (None, []))


class TestRouting(unittest.TestCase):

    def test_order_doesnt_matter(self):
        routes = [
            ('/a', a),
            ('/a/<*>', b),
            ('/a/c', c),
        ]
        routes_permutations = permutations(routes, len(routes))
        for i, routes in enumerate(routes_permutations):
            app = Framework({'app': i}, validators={'*': str})
            for route in routes:
                app.get(*route)
            self.assertEqual(app.lookup('/a', 'GET')[0], a)
            self.assertEqual(app.lookup('/a/x', 'GET')[0], b)
            self.assertEqual(app.lookup('/a/c', 'GET')[0], c)

    def test_improper_configuration(self):
        with self.assertRaises(ValueError):
            _make_app(
                [
                    ('get', '/a/b', a),
                    ('get', '/a/b', b),
                ]
            )
        with self.assertRaises(ValueError):
            _make_app(
                [
                    ('get', '/', a),
                    ('get', '/', b),
                ]
            )
        with self.assertRaises(ValueError):
            _make_app(
                [
                    ('route', '/a', a),
                    ('get', '/a', b),
                ]
            )


class TestCustomValidators(unittest.TestCase):

    def test_fallbacks(self):
        validators = [
            ('int', int),
            ('float', float),
            ('*', str),
        ]
        app = Framework(validators=validators)
        app.get("/x/a", f)
        app.get("/x/<int>", g)
        app.get("/x/<float>", h)
        app.get("/x/<*>", i)

        self.assertEqual(app.lookup("/x/a", "GET"), (f, []))
        self.assertEqual(app.lookup("/x/7", "GET"), (g, [7]))
        self.assertEqual(app.lookup("/x/7.9", "GET"), (h, [7.9]))
        self.assertEqual(app.lookup("/x/hello", "GET"), (i, ["hello"]))

    def test_validator_order_well_defined(self):
        """ Regardless of the order that endpoints are added to
        the application, the validators should be attempted in the
        order specified by the validators list passed in to the
        initializer """
        validators = [
            # use 1 / 0 to raise an exception if False
            ("match_a", lambda part: 1 if part in "a" else 1 / 0),
            ("match_b", lambda part: 1 if part in "ab" else 1 / 0),
            ("match_c", lambda part: 1 if part in "abc" else 1 / 0),
            ("match_d", lambda part: 1 if part in "abcd" else 1 / 0),
        ]
        routes = [
            ('/x/<match_a>', a),
            ('/x/<match_b>', b),
            ('/x/<match_c>', c),
            ('/x/<match_d>', d),
        ]
        routes_permutations = permutations(routes, len(routes))
        for i, routes in enumerate(routes_permutations):
            app = Framework({'app': i}, validators=validators)
            for route in routes:
                app.get(*route)
            self.assertEqual(app.lookup('/x/a', 'GET')[0], a)
            self.assertEqual(app.lookup('/x/b', 'GET')[0], b)
            self.assertEqual(app.lookup('/x/c', 'GET')[0], c)
            self.assertEqual(app.lookup('/x/d', 'GET')[0], d)

    def test_normal_wildcards(self):
        app = Framework(validators={'*': str})
        app.get("/x/a", f)
        app.get("/x/<*>", g)

        self.assertEqual(app.lookup("/x/a", "GET"), (f, []))
        self.assertEqual(app.lookup("/x/b", "GET"), (g, ["b"]))


if __name__ == "__main__":
    unittest.main()

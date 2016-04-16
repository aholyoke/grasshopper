CODES = {
    200: 'OK',
    404: 'Not Found',
    500: 'Internal Server Error'
}

METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
]


class Framework(object):
    def __init__(self):
        self.routing_get = {}
        self.routing_post = {}
        self.routing_put = {}
        self.routing_delete = {}
        self.routing = {
            'GET': self.routing_get,
            'POST': self.routing_post,
            'PUT': self.routing_put,
            'DELETE': self.routing_delete,
        }

    def lookup(self, url, method):
        url = url.lstrip('/')
        if not url.endswith('/'):
            url = url + '/'
        parts = url.split('/')
        return _lookup(parts, self.routing[method])

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        func = self._find_route(environ['PATH_INFO'], method)

        request = {
            'method': method,
            'headers': {},
            'body': u'',
        }
        response = {
            'headers': {},
            'body': u'',
        }
        if func is None:
            response_headers = [(key, val) for key, val in response['headers'].items()]
            start_response(u'404 Not Found', response_headers)
            yield 'Not Found'
            raise StopIteration()

        status_code = func(request, response)

        if status_code is None:
            status_code = 200
        if 'Content-Type' not in response['headers']:
            response['headers']['Content-Type'] = 'text/plain'
        if 'Content-Length' not in response['headers']:
            response['headers']['Content-Length'] = str(len(response['body']))

        response_headers = [(key, val) for key, val in response['headers'].items()]

        start_response(u'{} {}'.format(status_code, CODES[status_code]), response_headers)
        yield response['body']

    def route(self, url, func, methods=None):
        if methods is None:
            methods = METHODS
        parts = url.lstrip('/').rstrip('/').split('/')
        for method in methods:
            _route(parts, self.routing[method], func)

    def get(self, url, func):
        self.route(url, func, ['GET'])

    def post(self, url, func):
        self.route(url, func, ['POST'])

    def put(self, url, func):
        self.route(url, func, ['PUT'])

    def delete(self, url, func):
        self.route(url, func, ['DELETE'])

def _route(parts, table, func):
    if len(parts) == 1:
        val = table.get(parts[0])
        if val is None:
            table[parts[0]] = func
        elif isinstance(val, dict):
            1 / 0
        else:
            1 / 0
    else:
        val = table.get(parts[0])
        if val is None:
            table[parts[0]] = {}
            _route(parts[1:], table[parts[0]], func)
        elif isinstance(val, dict):
            _route(parts[1:], val, func)
        else:
            table[parts[0]] = {'': val}
            _route(parts[1:], table[parts[0]], func)


def _lookup(parts, table):
    try:
        sub_table = table[parts[0]]
    except KeyError:
        try:
            sub_table = table['*']
        except KeyError:
            return 404

    if not isinstance(sub_table, dict):
        return sub_table
    return _lookup(parts[1:], sub_table)


def index(request, response):
    response['body'] = 'index'


def hello(request, response):
    response['body'] = "hello"


def users(request, response):
    response['body'] = "users"


def user_profile(request, response):
    response['body'] = "user profile"


def user_stats(request, response):
    response['body'] = "user stats"


def not_stats(request, response):
    response['body'] = 'not stats'


app = Framework()
app.get('/hello/', hello)
app.get('/users', users)
app.get('/users/*/profile', user_profile)
app.get('/users/*/stats', user_stats)
app.get('/users/something/notstats', not_stats)
app.get('/', index)


assert app.lookup('users', 'GET') == app.lookup('/users', 'GET')
assert app.lookup('users/', 'GET') == app.lookup('/users/', 'GET')
assert app.lookup('/users', 'GET') == app.lookup('/users/', 'GET')
assert app.lookup('/', 'GET') == index
assert app.lookup('hello', 'GET') == hello
assert app.lookup('/hello', 'GET') == hello
assert app.lookup('hello/', 'GET') == hello
assert app.lookup('/hello/', 'GET') == hello
assert app.lookup('/users/something/notstats', 'GET') == not_stats
assert app.lookup('/users/nonexistant', 'GET') == 404
assert app.lookup('/users/50/profile', 'GET') == user_profile
assert app.lookup('/users/51/profile/', 'GET') == user_profile
assert app.lookup('/users/51/stats/', 'GET') == user_stats
assert app.lookup('users/52/stats', 'GET') == user_stats
assert app.lookup('users/something/stats', 'GET') == 404
assert app.lookup('users/something/stats', 'POST') == 404

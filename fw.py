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

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        func = self.lookup(path, method)

        request = {
            'method': method,
            'headers': {},
            'body': u'',
            'path': path,
        }
        response = {
            'headers': {},
            'body': u'',
        }
        if func is None:
            response_headers = [(key, val) for key, val in response['headers'].items()]
            start_response('404 Not Found', response_headers)
            yield 'Not Found'
            raise StopIteration()

        status_code = func(request, response)

        if status_code is None:
            status_code = 200
        if 'Content-Type' not in response['headers']:
            response['headers']['Content-Type'] = 'text/plain'
        if 'Content-Length' not in response['headers']:
            response['headers']['Content-Length'] = str(len(response['body']))

        response_headers = response['headers'].items()

        start_response('{} {}'.format(status_code, CODES[status_code]), response_headers)
        yield response['body']

    def lookup(self, url, method):
        parts = url.strip('/').split('/') + ['']
        return _lookup(parts, self.routing[method])

    def route(self, url, func, methods=None):
        if methods is None:
            methods = METHODS
        parts = url.strip('/').split('/')
        try:
            for method in methods:
                _route(parts, self.routing[method], func)
        except ValueError as e:
            raise ValueError("Path defined twice {} ({})".format(
                url,
                e.message))

    def get(self, url, func):
        self.route(url, func, ['GET'])

    def post(self, url, func):
        self.route(url, func, ['POST'])

    def put(self, url, func):
        self.route(url, func, ['PUT'])

    def delete(self, url, func):
        self.route(url, func, ['DELETE'])


def _route(parts, table, func):
    val = table.get(parts[0])
    if len(parts) == 1:
        if val is None:
            table[parts[0]] = {'': func}
            return
        raise ValueError("original: \"{}\" new: \"{}\"".format(
            val[''].__name__,
            func.__name__))
    else:
        if val is None:
            table[parts[0]] = {}
        _route(parts[1:], table[parts[0]], func)


def _lookup(parts, table):
    sub_table = table.get(parts[0], table.get('*'))
    if sub_table is None:
        return

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


def user_index(request, response):
    response['body'] = 'user index'


def new_user(request, response):
    response['body'] = 'new user'


def resource(request, response):
    response['body'] = 'resource'


def resource_list(request, response):
    response['body'] = 'resource_list'

app = Framework()
app.get('/', index)
app.get('/hello/', hello)
app.get('/users', users)
app.post('/users', new_user)
app.get('/users/*', user_index)
app.get('/users/*/profile', user_profile)
app.get('/users/*/stats', user_stats)
app.get('/users/something/notstats', not_stats)
app.get('/resource', resource)
app.get('/resource/list', resource_list)
app.get('/resource/list/*', resource_list)


assert app.lookup('users', 'GET') == app.lookup('/users', 'GET')
assert app.lookup('users/', 'GET') == app.lookup('/users/', 'GET')
assert app.lookup('/users', 'GET') == app.lookup('/users/', 'GET')
assert app.lookup('/', 'GET') == index
assert app.lookup('hello', 'GET') == hello
assert app.lookup('/hello', 'GET') == hello
assert app.lookup('hello/', 'GET') == hello
assert app.lookup('/hello/', 'GET') == hello
assert app.lookup('/users/something/notstats', 'GET') == not_stats
assert app.lookup('/users/50/profile', 'GET') == user_profile
assert app.lookup('/users/51/profile/', 'GET') == user_profile
assert app.lookup('/users/51/stats/', 'GET') == user_stats
assert app.lookup('users/52/stats', 'GET') == user_stats
assert app.lookup('users', 'POST') == new_user
assert app.lookup('/resource/list', 'GET') == resource_list
assert app.lookup('/resource/list/something', 'GET') == resource_list
assert app.lookup('/resource/list/something/somethingelse', 'GET') == None
assert app.lookup('/resource/notexistant', 'GET') == None

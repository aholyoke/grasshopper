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
        self.routing_get = []
        self.routing_post = []
        self.routing_put = []
        self.routing_delete = []
        self.routing = {
            'GET': self.routing_get,
            'POST': self.routing_post,
            'PUT': self.routing_put,
            'DELETE': self.routing_delete,
        }

    def _find_route(self, url, method):
        for path, func in self.routing[method]:
            if path == url:
                return func

    def __call__(self, environ, start_response):
        print("Call application on self {}".format(self))
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

    def all(self, url, func, methods=None):
        if methods is None:
            methods = METHODS
        for method in methods:
            self.routing[method].append((url, func))

    def get(self, url, func):
        self.all(url, func, ['GET'])

    def post(self, url, func):
        self.all(url, func, ['POST'])

    def put(self, url, func):
        self.all(url, func, ['PUT'])

    def delete(self, url, func):
        self.all(url, func, ['DELETE'])


def hello(request, response):
    response['body'] = 'Hello World!'
    return 200


def goodbye(request, response):
    if request['headers']['X-Something'] == 'Value':
        response['body'] = "GoodBye!"
        return 200
    else:
        response['body'] = "What?"
        return 404


app = Framework()
app.get('/hello', hello)
app.get('/goodbye', goodbye)
app.get('/', hello)

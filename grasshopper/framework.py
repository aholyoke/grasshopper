from urllib import quote
import traceback

CODES = {
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    204: 'No Content',
    301: 'Moved Permanently',
    302: 'Found',
    304: 'Not Modified',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    418: 'I\'m a teapot',  # super important
    429: 'Too Many Requests',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
}

METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'HEAD',
    'PATCH',
]

REQUEST_HEADERS = [
    'Accept',
    'Accept-Charset',
    'Accept-Datetime',
    'Accept-Encoding',
    'Accept-Language',
    'Authorization',
    'Cache-Control',
    'Connection',
    'Cookie',
    'Content-Length',
    'Content-Type',
    'Date',
    'Expect',
    'Forwarded',
    'From',
    'Host',
    'If-Match',
    'If-Modified-Since',
    'If-None-Match',
    'If-Range',
    'If-Unmodified-Since',
    'Max-Forwards',
    'Origin',
    'Pragma',
    'Proxy-Authorization',
    'Range',
    'Referer',
    'TE',
    'User-Agent',
    'Upgrade',
    'Via',
    'Warning',
]

COMMON_REQUEST_HEADERS = [
    'X-Requested-With',
    'DNT',
    'X-Forwarded-For',
    'X-Forwarded-With',
    'X-Forwarded-Host',
    'X-Forwarded-Proto',
    'Front-End-Https',
    'X-Http-Method-Override',
    'X-ATT-DeviceId',
    'X-Wap-Profile',
    'Proxy-Connection',
    'X-UIDH',
    'X-Csrf-Token',
    'CSRFToken',
    'X-XSRF-TOKEN',
]

RESPONSE_HEADERS = [
    'Access-Control-Allow-Origin',
    'Accept-Patch',
    'Accept-Ranges',
    'Age',
    'Allow',
    'Alt-Svc',
    'Cache-Control',
    'Connection',
    'Content-Disposition',
    'Content-Encoding',
    'Content-Length',
    'Content-Location',
    'Content-Range',
    'Content-Type',
    'Date',
    'ETag',
    'Expires',
    'Last-Modified',
    'Link',
    'Location',
    'Pragma',
    'Proxy-Authenticate',
    'Public-Key-Pins',
    'Refresh',
    'Retry-After',
    'Server',
    'Set-Cookie',
    'Status',
    'Strict-Transport-Security',
    'Trailer',
    'Transfer-Encoding',
    'TSV',
    'Upgrade',
    'Via',
    'Warning',
    'WWW-Authenticate',
]

COMMON_RESPONSE_HEADERS = [
    'X-XSS-Protection',
    'Content-Security-Policy',
    'X-Content-Security-Policy',
    'X-WebKit-Security-Policy',
    'X-Content-Type-Options',
    'X-Powered-By',
    'X-UA-Compatible',
    'X-Content-Duration',
    'Upgrade-Insecure-Requests',
]


class Framework(object):
    def __init__(self, settings=None):
        self.routing = {verb: {} for verb in METHODS}
        if settings is None:
            settings = {}
        self.settings = settings

    def __call__(self, environ, start_response):
        try:
            method = environ['REQUEST_METHOD']
            path = environ['PATH_INFO']
            func, wildcards = self.lookup(path, method)

            request = {
                'method': method,
                'headers': {
                    'User-Agent': environ.get('HTTP_USER_AGENT'),
                    'Accept-Language': environ.get('HTTP_ACCEPT_LANGUAGE'),
                },
                'body': '',
                'path': path,
                'environ': environ,
                'routing': self.routing,
                'wildcards': wildcards,
            }
            response = {
                'headers': {},
                'body': '',
            }
            if func is None:
                response_headers = response['headers'].items()
                start_response('404 Not Found', response_headers)
                return 'Not Found'

            try:
                status_code = func(
                    request=request,
                    response=response,
                    wildcards=wildcards,
                    settings=self.settings,
                )
            except Exception as e:
                start_response('500 Internal Server Error', [])
                return traceback.format_exc()

            if status_code is None:
                status_code = 200
            if 'Content-Type' not in response['headers']:
                response['headers']['Content-Type'] = 'text/plain'
            if 'Content-Length' not in response['headers']:
                response['headers']['Content-Length'] = str(len(response['body']))

            response_headers = response['headers'].items()

            start_response('{} {}'.format(status_code, CODES[status_code]), response_headers)
            return response['body']
        except Exception as e:
            start_response('500 Internal Server Error', [])
            return traceback.format_exc()

    def url_for(method, func):
        found_parts = _url_for(self.routing[method], func)
        for parts in found_parts:
            yield '/'.join(parts)

    def lookup(self, url, method):
        wildcards = []
        path, _, qs = url.partition('?')
        parts = path.strip('/').split('/') + ['']
        func = _lookup(parts, self.routing[method], wildcards)
        return (func, wildcards) if func else (None, [])

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
        if isinstance(val, dict):
            table[parts[0]][''] = func
        elif val is None:
            table[parts[0]] = {'': func}
        else:
            raise ValueError("original: \"{}\" new: \"{}\"".format(
                val[''].__name__,
                func.__name__))
    else:
        if val is None:
            table[parts[0]] = {}
        _route(parts[1:], table[parts[0]], func)


def _lookup(parts, table, wildcards):
    while True:
        sub_table = table.get(parts[0])
        if sub_table is None:
            if parts[0] == '':
                return
            sub_table = table.get('*')
            wildcards.append(parts[0])
            if sub_table is None:
                return

        if not isinstance(sub_table, dict):
            return sub_table

        parts = parts[1:]
        table = sub_table


def reconstruct_url(environ):
    """ Written by Ian Bicking """
    url = environ['wsgi.url_scheme'] + '://'

    if environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    else:
        url += environ['SERVER_NAME']

        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
                url += ':' + environ['SERVER_PORT']
        else:
            if environ['SERVER_PORT'] != '80':
                url += ':' + environ['SERVER_PORT']

    url += quote(environ.get('SCRIPT_NAME', ''))
    url += quote(environ.get('PATH_INFO', ''))
    if environ.get('QUERY_STRING'):
        url += '?' + environ['QUERY_STRING']


def _url_for(routing, func):
    for key, value in routing.items():
        if value == func:
            yield [key]
        elif isinstance(value, dict):
            for found in _url_for(value, func):
                yield [key] + found

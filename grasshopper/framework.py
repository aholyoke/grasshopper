from urllib import quote
import traceback

VALIDATOR_KEY = None

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
    def __init__(self, settings=None, **kwargs):
        self.routing = {verb: {} for verb in METHODS}
        if settings is None:
            settings = {}
        self.settings = settings
        self.validators = kwargs.get('validators', [])
        self.v_lookup = dict(self.validators)
        self.v_ordering = {k[0]: i for i, k in enumerate(self.validators)}

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
        func = self._lookup(parts, self.routing[method], wildcards)
        return (func, wildcards) if func else (None, [])

    def _lookup(self, parts, table, wildcards):
        for part in parts:
            sub_table = table.get(part)
            if sub_table is None:
                if part == '':
                    # end part should not match wildcard
                    return
                validators = table.get(VALIDATOR_KEY)
                if validators is None:
                    # wildcard did not match either
                    return
                result, sub_table = self._try_validators(validators, part)
                if result is None:
                    # all validators failed
                    return
                wildcards.append(result)

            if not isinstance(sub_table, dict):
                # sub_table is view function
                return sub_table

            table = sub_table

    def _try_validators(self, validators, part):
        assert validators is not None
        for v_string, sub_table in validators:
            # attempt to run validator on part
            try:
                result = self.v_lookup[v_string](part)
                return result, sub_table
            except:
                # validator was incorrect, try next one
                pass
        return None, None

    def route(self, url, func, methods=None):
        if methods is None:
            methods = METHODS
        parts = url.strip('/').split('/')
        try:
            for method in methods:
                self._route(parts, self.routing[method], func)
        except ValueError as e:
            raise ValueError("Path defined twice {} ({})".format(url, e.message))

    def _add_validator_part(self, table, part, sub_table):
        if VALIDATOR_KEY not in table:
            table[VALIDATOR_KEY] = []
        v_string = part[1:-1]
        # merge sub tables with the same validator key
        for key, existing_sub_table in table[VALIDATOR_KEY]:
            if key == v_string:
                existing_sub_table.update(sub_table)
                return

        # else insert new validator key in the order of self.validators
        for i, v in enumerate(table[VALIDATOR_KEY]):
            if self.v_ordering[v_string] < self.v_ordering[v[0]]:
                table[VALIDATOR_KEY].insert(i, (v_string, sub_table))
                return
        table[VALIDATOR_KEY].append((v_string, sub_table))

    def _route(self, parts, table, func):
        for i, part in enumerate(parts[:-1]):
            if _is_validator_part(part):
                # make sub table
                sub_table = {}
                self._route(parts[i + 1:], sub_table, func)
                self._add_validator_part(table, part, sub_table)
                return
            if part not in table:
                table[part] = {}
            table = table[part]

        part = parts[-1]
        if _is_validator_part(part):
            self._add_validator_part(table, part, {'': func})
            return
        if part not in table:
            # new endpoint
            table[part] = {'': func}
        else:
            if '' in table[part]:
                # table[part] is existing function
                raise ValueError("original: \"{}\" new: \"{}\"".format(
                    table[part][''].__name__,
                    func.__name__))
            # longer endpoint already exists
            table[part][''] = func

    def get(self, url, func):
        self.route(url, func, ['GET'])

    def post(self, url, func):
        self.route(url, func, ['POST'])

    def put(self, url, func):
        self.route(url, func, ['PUT'])

    def delete(self, url, func):
        self.route(url, func, ['DELETE'])


def _is_validator_part(part):
    return len(part) > 1 and part[0] == '<' and part[-1] == '>'


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

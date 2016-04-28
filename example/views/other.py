def index(request, response, **kwargs):
    response['body'] = 'index'


def hello(request, response, **kwargs):
    response['body'] = "hello"


def not_stats(request, response, **kwargs):
    response['body'] = 'not stats'

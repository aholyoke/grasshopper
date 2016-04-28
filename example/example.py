from grasshopper import Framework
from settings.local import settings

""" define views """


def index(request, response, **kwargs):
    response['body'] = 'index'


def hello(request, response, **kwargs):
    response['body'] = "hello"


def users(request, response, **kwargs):
    response['body'] = "users"


def user_profile(request, response, **kwargs):
    response['body'] = "user profile"


def user_stats(request, response, **kwargs):
    response['body'] = "user stats"


def not_stats(request, response, **kwargs):
    response['body'] = 'not stats'


def user_index(request, response, **kwargs):
    response['body'] = 'user index'


def new_user(request, response, **kwargs):
    response['body'] = 'new user'


def resource(request, response, **kwargs):
    response['body'] = 'resource'


def resource_list(request, response, **kwargs):
    response['body'] = 'resource_list'


""" Route endpoints to views """

app = Framework(settings)
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

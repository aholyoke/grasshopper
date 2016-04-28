from grasshopper import Framework
from settings.local import settings
from views.other import index, hello, not_stats
from views.resources import resource, resource_list
from views.users import users, user_profile, user_stats, user_index, new_user


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

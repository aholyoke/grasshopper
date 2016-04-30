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

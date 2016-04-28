def users(request, response, **kwargs):
    response['body'] = "users"


def user_profile(request, response, **kwargs):
    response['body'] = "user profile"


def user_stats(request, response, **kwargs):
    response['body'] = "user stats"


def user_index(request, response, **kwargs):
    response['body'] = 'user index'


def new_user(request, response, **kwargs):
    response['body'] = 'new user'

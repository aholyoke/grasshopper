def resource(request, response, **kwargs):
    response['body'] = 'resource'


def resource_list(request, response, **kwargs):
    response['body'] = 'resource_list'

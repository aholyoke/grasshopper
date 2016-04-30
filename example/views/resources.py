from jinja2 import Template
from helpers import read_template


def resource(request, response, settings, **kwargs):
    template = Template(read_template(settings['TEMPLATE_DIR'], 'resource.html'))
    response['body'] = template.render(variable=settings['A'])


def resource_list(request, response, **kwargs):
    response['body'] = 'resource_list'
    return 404

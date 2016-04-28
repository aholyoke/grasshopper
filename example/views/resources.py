from jinja2 import Template


def resource(request, response, settings, **kwargs):
    with open("{}/resource.html".format(settings['TEMPLATES_DIR'])) as f:
        template = Template(f.read())
    response['body'] = template.render(variable=settings['A'])


def resource_list(request, response, **kwargs):
    response['body'] = 'resource_list'

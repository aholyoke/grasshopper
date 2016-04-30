def read_template(template_dir, template_name):
    with open("{}/{}".format(template_dir, template_name)) as f:
        return f.read()

import os


def get_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_content(template):
    template_path = '{}/templates/{}'.format(get_path(), template)
    file_handler = open(template_path, "r")
    content = file_handler.read()
    return content


def get_template(template_name):
    return get_content(template_name)

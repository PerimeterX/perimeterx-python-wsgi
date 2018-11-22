import os


def get_path():
    return os.path.dirname(os.path.abspath(__file__))

def get_content(template):
    templatePath = "%s/templates/%s" % (get_path(), template)
    file = open(templatePath, "r")
    content = file.read()
    return content



def get_template(template_name):
    return get_content(template_name)

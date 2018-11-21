import pystache
import os


def get_path():
    return os.path.dirname(os.path.abspath(__file__))

def get_content(template):
    templatePath = "%s/templates/%s" % (get_path(), template)
    file = open(templatePath, "r")
    content = file.read()
    return content

def get_props(config, uuid, vid):
    return {
        'refId': uuid,
        'appId': config.get('app_id'),
        'vid': vid,
        'uuid': uuid,
        'customLogo': config.get('custom_logo'),
        'cssRef': config.get('css_ref'),
        'jsRef': config.get('js_ref'),
        'logoVisibility': 'visible' if config['custom_logo'] else 'hidden'
    }


def get_template(template_name):
    return get_content(template_name)

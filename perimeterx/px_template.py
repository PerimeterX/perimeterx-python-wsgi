import pystache
import os

def get_template(template, config, uuid, vid):
    template_content = get_content(template)
    props = get_props(config, uuid, vid)
    generatedHtml = pystache.render(template_content, props)
    return generatedHtml

def get_path():
    return os.path.dirname(os.path.abspath(__file__))

def get_content(template):
    file = open("%s/templates/%s.mustache" % (get_path(),template), "r")
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

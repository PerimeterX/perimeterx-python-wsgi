import pystache

def get_template(template, config, uuid, vid):
    template_content = get_content(template)
    props = get_props()
    generatedHtml = pystache.render(template_content, props)
    return generatedHtml

def get_content(template):
    file = open("./templates/%s.mustache" % template, "r")
    content = file.read()
    return conetnt

def get_props(config, uuid, vid):
    return {
        'refId': uuid,
        'appId': px_config.app_id,
        'vid': vid,
        'uuid': uuid,
        'customLogo': px_config.custom_logo,
        'cssRef': px_config.css_ref,
        'jsRef': px_config.js_ref,
        'logoVisibility': 'visible' if px_config.custom_logo else 'hidden'
    }

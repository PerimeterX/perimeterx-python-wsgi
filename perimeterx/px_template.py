px_config = None
uuid = None
vid = None

def init(config, uuid, vid):
    global px_config
    global uuid
    global vid

def get_template(template):
    template_content = get_content(template)
    template_props = get_props()

def get_content():
    file = open("./templates/%s.mustache" % template, "r")
    content = file.read()
    return conetnt

def get_props():
    return {
        'refId': uuid,
        'vid': vid
    }

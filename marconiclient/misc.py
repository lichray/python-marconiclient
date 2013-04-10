
from urllib import quote

def proc_template(template, **kwargs):
    """
    Processes a templated URL by substituting the
    dictionary args and returning the strings.
    """
    res = template

    for name, value in kwargs.iteritems():
        res = res.replace("{" + name + "}", quote(str(value)))

    return res

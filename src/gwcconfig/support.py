import logging
from xml.etree.ElementTree import TreeBuilder, tostring
from tempfile import mkstemp
import urllib
import urlparse

def url(base, seg, query=None):
    """
    Create a URL from a list of path segments and an optional dict of query
    parameters.
    """

    def clean_segment(segment):
        """
        Cleans the segment and encodes to UTF-8 if the segment is unicode.
        """
        segment = segment.strip('/')
        if isinstance(segment, unicode):
            segment = segment.encode('utf-8')
        return segment

    seg = (urllib.quote(clean_segment(s)) for s in seg)
    if query is None or len(query) == 0:
        query_string = ''
    else:
        query_string = "?" + urllib.urlencode(query)
    path = '/'.join(seg) + query_string
    adjusted_base = base.rstrip('/') + '/'
    return urlparse.urljoin(adjusted_base, path)

def xml_property(path, converter = lambda x: x.text, default=None):
    def getter(self):
        if path in self.dirty:
            return self.dirty[path]
        else:
            if self.dom is None:
                self.fetch()
            node = self.dom.find(path)
            return converter(self.dom.find(path)) if node is not None else default

    def setter(self, value):
        self.dirty[path] = value

    def delete(self):
        self.dirty[path] = None

    return property(getter, setter, delete)

def string_list(node):
    if node is not None:
        return [n.text for n in node.findall("string")]

def write_string(name):
    def write(builder, value):
        builder.start(name, dict())
        if (value is not None):
            builder.data(value)
        builder.end(name)
    return write

def write_bool(name):
    def write(builder, b):
        builder.start(name, dict())
        builder.data("true" if b and b != "false" else "false")
        builder.end(name)
    return write

def write_string_list(name):
    def write(builder, words):
        builder.start(name, dict())
        words = [w for w in words if len(w) > 0]
        for w in words:
            builder.start("string", dict())
            builder.data(w)
            builder.end("string")
        builder.end(name)
    return write
    
class ResourceInfo(object):
    def __init__(self):
        self.dom = None
        self.dirty = dict()

    def fetch(self):
        self.dom = self.server.get_xml(self.href)

    def clear(self):
        self.dirty = dict()

    def refresh(self):
        self.clear()
        self.fetch()

    def serialize(self, builder):
        # GeoServer will disable the resource if we omit the <enabled> tag,
        # so force it into the dirty dict before writing
        if hasattr(self, "enabled"):
            self.dirty['enabled'] = self.enabled

        if hasattr(self, "advertised"):
            self.dirty['advertised'] = self.advertised

        for k, writer in self.writers.items():
            if k in self.dirty:
                writer(builder, self.dirty[k])

    def message(self):
        builder = TreeBuilder()
        builder.start(self.resource_type, dict())
        self.serialize(builder)
        builder.end(self.resource_type)
        msg = tostring(builder.close())
        return msg

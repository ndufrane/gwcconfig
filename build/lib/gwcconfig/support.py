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

def write_parameterFilters(name):
    def write(builder, filters):
        builder.start(name, dict())
        for filter in filters:
            if isinstance(filter, StyleParameterFilter):
                filter.write(builder)
        builder.end(name)

    return write

class StyleParameterFilter(object):
    tag_name = "styleParameterFilter"

    def __init__(self, key, defaultValue, allowedStyles):
        self.key = key
        self.defaultValue = defaultValue
        self.allowedStyles =  allowedStyles

    def write(self,builder):
        builder.start(self.tag_name, dict())
        if self.key is not None:
            builder.start("key", dict())
            builder.data(self.key)
            builder.end("key")
        if self.defaultValue:
            builder.start("defaultValue", dict())
            builder.end("defaultValue")
        if self.allowedStyles is not None:
            builder.start("allowedStyles", dict())
            for style in self.allowedStyles:
                builder.start("string", dict())
                builder.data(style)
                builder.end("string")
            builder.end("allowedStyles")
        builder.end(self.tag_name)

def md_style_parameter_filter(node):
    key = node.find("key")
    key = key.text if key is not None else None
    defaultValue = node.find("defaultValue")
    defaultValue = True if defaultValue is not None else False
    allowedStyles = node.find("allowedStyles")
    if allowedStyles is not None:
        allowedStyles = string_list(allowedStyles)
    return StyleParameterFilter(key,defaultValue,allowedStyles)

def build_parameterFilters(node):
    if node is not None:
        #TODO Handle other types of Parameterfilter
        return [md_style_parameter_filter(n) for n in node.findall("styleParameterFilter")]

class GridSubSet(object):
    def __init__(self, gridSetName, zoomStart, zoomStop, extent_coords):
        self.gridSetName = gridSetName
        self.zoomStart = zoomStart
        self.zoomStop = zoomStop
        self.extent_coords = extent_coords


def md_grid_subset(node):
    name = node.find("gridSetName")
    name = name.text if name is not None else None
    zoomStart = node.find("zoomStart")
    zoomStart = zoomStart.text if zoomStart is not None else None
    zoomStop = node.find("zoomStop")
    zoomStop = zoomStop.text if zoomStop is not None else None
    extent_coords = None
    extent = node.find("extent")
    if extent is not None:
        coords = extent.find("coords")
        extent_coords = double_list(coords)
    return GridSubSet(name, zoomStart, zoomStop, extent_coords)


def build_gridSubsets(node):
    if node is not None:
        return [md_grid_subset(n) for n in node.findall("gridSubset")]

def write_gridSubsets(name):
    def write(builder, words):
        builder.start(name, dict())
        for gs in words:
            builder.start("gridSubset", dict())
            if gs.gridSetName is not None:
                builder.start("gridSetName", dict())
                builder.data(gs.gridSetName)
                builder.end("gridSetName")
            if gs.extent_coords is not None:
                builder.start("extent", dict())
                builder.start("coords", dict())
                for coord in gs.extent_coords:
                    builder.start("double", dict())
                    builder.data(coord)
                    builder.end("double")
                builder.end("coords")
                builder.end("extent")
            if gs.zoomStart is not None:
                builder.start("zoomStart", dict())
                builder.data(gs.zoomStart)
                builder.end("zoomStart")
            if gs.zoomStop is not None:
                builder.start("zoomStop", dict())
                builder.data(gs.zoomStop)
                builder.end("zoomStop")
            builder.end("gridSubset")
        builder.end(name)
    return write

def double_list(node):
    if node is not None:
        return [n.text for n in node.findall("double")]

def write_double_list(name):
    def write(builder, words):
        builder.start(name, dict())
        words = [w for w in words if len(w) > 0]
        for w in words:
            builder.start("double", dict())
            builder.data(w)
            builder.end("double")
        builder.end(name)
    return write

def string_list(node):
    if node is not None:
        return [n.text for n in node.findall("string")]

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

def int_list(node):
    if node is not None:
        return [n.text for n in node.findall("int")]

def write_int_list(name):
    def write(builder, words):
        builder.start(name, dict())
        words = [w for w in words if len(w) > 0]
        for w in words:
            builder.start("int", dict())
            builder.data(w)
            builder.end("int")
        builder.end(name)
    return write

def write_string(name):
    def write(builder, value):
        builder.start(name, dict())
        if (value is not None):
            builder.data(value)
        builder.end(name)
    return write

def write_numeric(name):
    def write(builder, value):
        builder.start(name, dict())
        if (value is not None):
            builder.data(str(value))
        builder.end(name)
    return write

def write_bool(name):
    def write(builder, b):
        builder.start(name, dict())
        builder.data("true" if b and b != "false" else "false")
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

    def serialize(self, builder, onlyDirty=False):
        # GeoServer will disable the resource if we omit the <enabled> tag,
        # so force it into the dirty dict before writing
        if hasattr(self, "enabled"):
            self.dirty['enabled'] = self.enabled
        # Mandatory
        if hasattr(self, "name"):
            self.dirty['name'] = self.name
        # Optional but more precise
        if hasattr(self, "id"):
            self.dirty['id'] = self.id

        for k, writer in self.writers.items():
            if onlyDirty:
                if k in self.dirty:
                    writer(builder, self.dirty[k])
            else:
                writer(builder, getattr(self, k))


    def message(self):
        builder = TreeBuilder()
        builder.start(self.resource_type, dict())
        self.serialize(builder)
        builder.end(self.resource_type)
        msg = tostring(builder.close())
        return msg

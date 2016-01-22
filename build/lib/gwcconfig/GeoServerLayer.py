
from gwcconfig.support import xml_property, url, ResourceInfo, write_string, string_list, write_string_list, write_numeric, write_int_list, int_list, write_bool, build_gridSubsets, write_gridSubsets, write_parameterFilters, build_parameterFilters

def geoserverLayer_from_index(server, node):
    name = node.find("name")
    return GeoServerLayer(server, name.text)

class GeoServerLayer(ResourceInfo):
    save_method = 'PUT' #WTF! Put for new configuration
    update_method = 'POST' #WTF! Post for replacing existing (so no verbs for update)

    resource_type = "GeoServerLayer"

    id =  xml_property("id")
    expireCache = xml_property("expireCache")
    expireClients = xml_property("expireClients")
    enabled = xml_property("enabled", lambda x: x.text == "true")
    mimeFormats = xml_property("mimeFormats", string_list)
    gutter = xml_property("gutter")
    metaWidthHeight = xml_property("metaWidthHeight", int_list)
    gridSubsets = xml_property("gridSubsets", build_gridSubsets)
    parameterFilters = xml_property("parameterFilters", build_parameterFilters)

    writers = dict(
                id = write_numeric("id"),
                expireCache = write_numeric("expireCache"),
                expireClients = write_numeric("expireClients"),
                enabled = write_bool("enabled"),
                name = write_string("name"),
                mimeFormats = write_string_list("mimeFormats"),
                gutter = write_numeric("gutter"),
                metaWidthHeight = write_int_list("metaWidthHeight"),
                gridSubsets = write_gridSubsets("gridSubsets"),
                parameterFilters = write_parameterFilters("parameterFilters"),
            )

    def __init__(self, server, name):
        super(GeoServerLayer, self).__init__()
        self.server = server
        self.name = name

    def __repr__(self):
        return "%s & %s" % (self.name, self.href)

    @property
    def href(self):
        return url(self.server.service_url, ["layers", self.name + ".xml"])

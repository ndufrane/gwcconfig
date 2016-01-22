
from gwcconfig.support import xml_property, url, ResourceInfo, write_string, string_list, write_string_list

def geoserverLayer_from_index(server, node):
    name = node.find("name")
    return GeoServerLayer(server, name.text)

class GeoServerLayer(ResourceInfo):
    save_method = 'PUT'
    update_method = 'POST'

    resource_type = "GeoServerLayer"

    id =  xml_property("id")
    expireCache = xml_property("expireCache")
    expireClients = xml_property("expireClients")
    enabled = xml_property("enabled")
    mimeFormats = xml_property("mimeFormats", string_list)

    writers = dict(
                id = write_string("id"),
                expireCache = write_string("expireCache"),
                expireClients = write_string("expireClients"),
                enabled = write_string("enabled"),
                name = write_string("name"),
                mimeFormats = write_string_list("mimeFormats"),
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

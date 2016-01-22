#!/usr/bin/python
# -*- coding: utf8 -*-

from xml.etree.ElementTree import TreeBuilder, tostring

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

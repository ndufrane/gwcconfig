#!/usr/bin/python
# -*- coding: utf8 -*-

import httplib2
import logging
import time
from datetime import datetime, timedelta
from urlparse import urlparse

from xml.etree.ElementTree import XML
from xml.parsers.expat import ExpatError

from gwcconfig.GeoServerLayer import geoserverLayer_from_index, GeoServerLayer

logger = logging.getLogger("gwcconfig.server")

class FailedRequestError(Exception):
    pass

class GeoWebCacheServer(object):
    """Base GeoWebCache server
        Sample service_url http://localhost:8080/geoserver/gwc/rest
    """
    def __init__(self, service_url, username="admin", password="geoserver", disable_ssl_certificate_validation=False):
        self.service_url =  service_url
        if self.service_url.endswith("/"):
            self.service_url =  self.service_url.strip("/")
        self.username = username
        self.password = password
        self.http = None
        self._cache = dict()
        self.disable_ssl_certificate_validation = disable_ssl_certificate_validation
        self.setup_connection()

    def setup_connection(self):
        self.http = httplib2.Http(disable_ssl_certificate_validation=self.disable_ssl_certificate_validation)
        self.http.add_credentials(self.username, self.password)
        netloc = urlparse(self.service_url).netloc
        self.http.authorizations.append(
            httplib2.BasicAuthentication(
                (self.username, self.password),
                netloc,
                self.service_url,
                {},
                None,
                None,
                self.http
            )
        )

    def get_xml(self, rest_url):
        logger.debug("GET %s", rest_url)

        cached_response = self._cache.get(rest_url)

        def is_valid(cached_response):
            return cached_response is not None and datetime.now() - cached_response[0] < timedelta(seconds=5)

        def parse_or_raise(xml):
            try:
                return XML(xml.decode('iso-8859-1').encode('utf-8'))
            except (ExpatError, SyntaxError), e:
                msg = "Geoserver gave non-XML response for [GET %s]: %s"
                msg = msg % (rest_url, xml)
                raise Exception(msg, e)

        if is_valid(cached_response):
            raw_text = cached_response[1]
            return parse_or_raise(raw_text)
        else:
            cpt = 0
            while cpt < 3:
                response, content = self.http.request(rest_url)
                if response.status == 200:
                    self._cache[rest_url] = (datetime.now(), content)
                    return parse_or_raise(content)
                else:
                    cpt = cpt + 1
                    time.sleep(1)
                    print("Tried to make a GET request to %s but got a %d status code: \n%s" % (rest_url, response.status, content))
            if cpt > 2:
                raise FailedRequestError("Tried to make a GET 3 Times request to %s but got a %d status code: \n%s" % (rest_url, response.status, content))

    def update(self, obj):
        return self.save(obj,update=True)

    def save(self, obj, update=False):
        """
        saves an object to the REST service

        gets the object's REST location and the XML from the object,
        then POSTS the request.
        """
        rest_url = obj.href
        message = obj.message()

        headers = {
            "Content-type": "application/xml",
            "Accept": "application/xml"
        }
        method = obj.save_method
        if(update):
            method = obj.update_method
        logger.debug("%s %s", method, obj.href)
        response = self.http.request(rest_url, method, message, headers)
        headers, body = response
        self._cache.clear()
        if 400 <= int(headers['status']) < 600:
            raise FailedRequestError("Error code (%s) from GeoServer: %s" %
                (headers['status'], body))
        return response

    def get_layers(self):
        layer_list_xml = self.get_xml("%s/layers" % self.service_url)
        return [geoserverLayer_from_index(self, node) for node in layer_list_xml.findall("layer")]

    def get_layer(self, name):
        try:
            lyr = GeoServerLayer(self, name)
            lyr.fetch()
            return lyr
        except FailedRequestError:
            return None

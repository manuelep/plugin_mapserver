#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
import os
from jsmin import jsmin

class ol(object):
    """ """

    @staticmethod
    def get_url(**vars):
        return URL("plugin_mapserver", "proxy", vars=vars)

    # TODO
#     SingleWFSLayerMap = """ """

    @classmethod
    def _swmsmap(cls, layer_name, extent, div, **vars):
        """ Returns a single WMS-layer map code """

        jscode = """var url = "%(url)s";
        var wmsTSource = new ol.source.TileWMS({
            url: url,
            serverType: 'mapserver',
            params: {'LAYERS': '%(layer_name)s', 'TILED': true},
        });
        var map = new ol.Map({
            "logo": null,
            "target": "%(div)s",
            "view": new ol.View({center: [0, 0], zoom: 2}),
            "layers": [
                new ol.layer.Tile({opacity: 0.3, source: new ol.source.OSM()}),
                new ol.layer.Tile({source: wmsTSource}),
            ]
        });
        map.getView().fit(%(extent)s,  map.getSize());
        """ % dict(
            url = cls.get_url(**vars),
            extent = extent,
            layer_name = layer_name,
            div = div
        )

        return jscode

    @classmethod
    def swmsmap(cls, row, extent, **kw):
        """ Returns a single WMS-layer map code and the related DOM element """
        div = dict({"_id": "map", "_style": "height: 500px;"}, **kw)
        mapfile = os.path.join(os.getcwd(), current.request.folder, "uploads", row.mapfile)
        return DIV(**div), jsmin(cls._swmsmap(row.opts["layer_name"], extent, div["_id"], map=mapfile))

#     @classmethod
#     def swmsmap(cls, _id, div="map", **kw):
#         """ Returns a single WMS-layer map """
#         row = db.mapfile[_id]
#         if row is None: raise HTTP(404, "This should never happen, why it happens?")
#         gprops = getGeomProps(tablename=row.slug.split(".")[1], epsg=3857)
#         mapfile = os.path.join(os.getcwd(), request.folder, "uploads", row.mapfile)
# #         sld_url = URL("bugger_tracker", "call", args=("xml", "pathStyler"), extension=False, scheme=True, host=True)
#         extent = json.dumps(gprops["extent"])
#         url = cls.get_url(map=mapfile, SLD=sld_url)
#         return (
#             DIV(_id=div, **dict(_style="height: 500px;", **kw)),
#             jsmin(cls.SingleWMSLayerMap % dict(locals(), **(row.opts or {}))),
#         )

# def wfs():
#     return dict(map=LOAD(request.controller, "_wfs.load", args=request.args, ajax=True))
# 
# def _wfs():
#     """ ATTENZIONE Problemi con la configurazione del layer WFS su mapserver """
#     _id = request.args(0, default=0, cast=int)
#     row = db.mapfile[_id]
#     mapfilepath = os.path.join(myconf.take("mapserver:mapfiles.path"), row.mapfile)
#     response.js = jsmin("""
#     var url = 'http://localhost/cgi-bin/mapserv?map=/home/manuele/mapserver/data/ciclabiliwfs.map&';
#     var vectorSource = new ol.source.Vector({
#       format: new ol.format.GeoJSON(),
#       url: function(extent) {
#           return url + 'service=WFS&' +
#           'version=1.1.0&request=GetFeature&typename=osm:ciclabili&' +
#           'outputFormat=application/json&srsname=EPSG:3857&' +
#           'bbox=' + extent.join(',') + ',EPSG:3857';
#       },
#       strategy: ol.loadingstrategy.tile(ol.tilegrid.createXYZ({}))
#     });
#     var wfs = new ol.layer.Vector({"source": vectorSource});
#     var map = new ol.Map({
#         "logo": null,
#         "target": "map",
#         "view": new ol.View({center: [0, 0], zoom: 2}),
#         "layers": [
#             new ol.layer.Tile({opacity: 0.3, source: new ol.source.OSM()}),
#             wfs
#         ]
#     });""")
#     print response.js
#     return dict(map=DIV(_id="map", _style="height: 500px;"))

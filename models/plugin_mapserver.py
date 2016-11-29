# -*- coding: utf-8 -*-

from urlparse import urlparse
if not "jsmin" in vars():
    from jsmin import jsmin
import cStringIO as StringIO
import os

def slugs():
    """ Returns catalog.table for each table that has a geometry column """
    for dbname, odb in odbs.iteritems():
        for row in odb(odb.geometry_columns.srid>=0).select(
            odb.geometry_columns.table_catalog, odb.geometry_columns.table_name
        ):
            yield "{table_catalog}.{table_name}".format(**row)

db.define_table("mapfile",
    Field("slug", required=True, requires=IS_IN_SET(slugs(), zero=None)),
    # Eventualmente potrebbe essere testo libero
    Field("layer_type", requires=IS_IN_SET(["wms", "wfs"])),
    Field("mapfile", "upload", writable=False, readable=False, autodelete=True),
    Field("body", "text", required=True, comment=T("Use python notation to introduce values in 'opts'")),
#     Field("template", "upload", rname='""', required=True),
    Field("opts", "json", default={})
)

response.menu += [
    (STRONG(SPAN(_class="glyphicon glyphicon-leaf", **{"_aria-hidden": "true"}),
            " ", T("Mapserver setup"), _style="color: yellow;"), False, URL("plugin_mapserver", "setup"), [],),
]

class mapfileCallbacks(object):

    @staticmethod
    def getUriParams(slug):
        dbname, _ = slug.split('.')
        dburi = (i._uri for i in odbs.values() if i._uri.endswith(dbname)).next()
        nfo = urlparse(dburi)
        return dict(user=nfo.username, password=nfo.password, dbname=nfo.path[1:], host=nfo.hostname)

    @classmethod
    def onInsert(cls, f):

        opts = dict(f.get('opts', {}), **cls.getUriParams(f["slug"]))

        stream = StringIO.StringIO(f["body"] % opts)
        filename = "%(slug)s_%(layer_type)s.map" % f
        f["mapfile"] = db.mapfile.mapfile.store(stream, filename)

    @classmethod
    def onUpdate(cls, s, f):
        for row in s.select():

            opts = dict(f.get('opts', row.opts or {}), **cls.getUriParams(f["slug"]))

            body = f["body"] if opts is None else f["body"] % opts
            with open(os.path.join(os.getcwd(), request.folder, "uploads", row.mapfile), "wb") as mapfile:
                mapfile.write(body)

    @classmethod
    def setup(cls):
        db.mapfile._before_insert.append(cls.onInsert)
        db.mapfile._after_update.append(cls.onUpdate)

mapfileCallbacks.setup()
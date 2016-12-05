# -*- coding: utf-8 -*-

def _plugin_mapserver(msdb):

    from plugin_mapserver import slugs, slug2uri, getUriParams
    import cStringIO as StringIO
    from gluon.tools import PluginManager
    if not "os" in vars():
        import os

    plugins = PluginManager('mapserver')

    msdb.define_table("mapfile",
        Field("slug", required=True, requires=IS_IN_SET(slugs(odbs), zero=None)),
        # Eventualmente potrebbe essere testo libero
        Field("layer_type", requires=IS_IN_SET(["wms", "wfs"])),
        Field("mapfile", "upload",
            uploadfolder = os.path.join(request.folder,'uploads/mapfiles'),
            writable=False, readable=False, autodelete=True
        ),
        Field("body", "text", required=True, comment=T("Use python notation to introduce values in 'opts'")),
    #     Field("template", "upload", rname='""', required=True),
        Field("opts", "json", default={})
    )

    def onInsert(f):

        opts = dict(f.get('opts', {}), **getUriParams(slug2uri(odbs, f["slug"])))

        stream = StringIO.StringIO(f["body"] % opts)
        filename = "%(slug)s_%(layer_type)s.map" % f
        f["mapfile"] = msdb.mapfile.mapfile.store(stream, filename)

    def onUpdate(s, f):

        for row in s.select():

            opts = dict(f.get('opts', row.opts or {}), **getUriParams(slug2uri(odbs, f["slug"])))
            body = f["body"] if opts is None else f["body"] % opts

            with open(os.path.join(os.getcwd(), request.folder, "uploads", row.mapfile), "wb") as mapfile:
                mapfile.write(body)

    msdb.mapfile._before_insert.append(onInsert)
    msdb.mapfile._after_update.append(onUpdate)

    response.menu += [
        (STRONG(SPAN(_class="glyphicon glyphicon-leaf", **{"_aria-hidden": "true"}),
                " ", T("Mapserver setup"), _style="color: yellow;"), False, URL("plugin_mapserver", "setup"), [],),
    ]

    return msdb

if not myconf.get("mapserver.custom_db"):
    msdb = _plugin_mapserver(db)


# -*- coding: utf-8 -*-

import requests

# try something like
def index(): return dict(message="hello from plugin_mapserver.py")

@auth.requires_login()
def setup():
    if "view" in request.args:
        db.mapfile.body.represent=lambda v,_: CODE(v)
    grid = SQLFORM.grid(db.mapfile.id>0,
#         links = [dict(header=T("Browse"), body=lambda row: row.layer_type and A(T("go"), _href=URL(request.controller, row.layer_type, args=(row.id,))))],
        csv=False, searchable=False,
        formname='mapfile_grid'
    )
    return dict(grid=grid)

@auth.requires_login()
def wms():
    return dict(map=LOAD(request.controller, "_wms.load", args=request.args, ajax=True))

@auth.requires_login()
def _wms():
    """ """
    row = db.mapfile[request.args(0, default=0, cast=int)]
    if row is None: raise HTTP(404, "This should never happen, why it happens?")
    gprops = getGeomProps(tablename=row.slug.split(".")[1], epsg=3857)
    extent = json.dumps(gprops["extent"])
    div, jscode = ol.swmsmap(row, extent)
    response.js = jscode
    return dict(map=div)

@auth.requires_login()
def proxy():

    session.forget(response)

    # https protocol is not managed because it would imply a double encryption
    url = myconf.take("mapserver.url")

    method = request.env.request_method.upper() if not 'force_method' in request.vars else request.vars.pop('force_method').upper()
    data = {
        'params' if method == 'GET' else 'data': dict(request.vars)
    }

    def _build_raw_cookie():
        """ """
        return "; ".join(["%s=%s" % (v.key, v.value) for k,v in request.cookies.items()])

    try:
        res = requests.request(method, url,
            allow_redirects = False,
            stream = True,
            # 2. In this way cookies are correctly managed and passed between the
            # client and the server and back again transparently to the user
            headers = dict(
                cookie=_build_raw_cookie()
            #   ^^^^^^ NOT "cookies"
            ),
            **data
        )
    except requests.exceptions.ConnectionError:
        raise HTTP(408)

    for k,v in (res.cookies or {}).iteritems():
        response.cookies[k] = v.strip('\"')
        response.cookies[k]['path'] = '/'

    if res.status_code == 200:
        for k,v in res.headers.iteritems():
            response.headers[k.title()] = v
        content = res.raw.read()
        # NOTA: LA riga seguente non da errore quindi probabilmente va anche bene
        # così ma da documentazione non sembra essere necessaria la chiusura.
        res.raw.close()
        return content
    elif res.status_code in (302, 303, ):
        redirect(URL(args=[dm_id])+res.headers['location'], how=res.status_code)
    else:
        raise HTTP(res.status_code)

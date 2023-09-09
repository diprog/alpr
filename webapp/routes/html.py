import os.path

from aiohttp import web

from webapp.constants import HTML_DIR

html_routes = web.RouteTableDef()


def html_response(path):
    fullpath = os.path.join(HTML_DIR, path)
    with open(fullpath, 'r', encoding='utf-8') as html_file:
        return web.Response(text=html_file.read(), content_type='text/html')


@html_routes.get('/')
async def index_page(request: web.Request):
    return html_response('index.html')

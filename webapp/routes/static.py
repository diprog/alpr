import os.path

from aiohttp import web

from webapp.constants import HTML_DIR


def folder(path):
    return web.static('/' + path, os.path.join(HTML_DIR, path))


static_routes = [
    folder('js'),
    folder('bootstrap'),
    folder('bootstrap-icons'),
    folder('jquery'),
    folder('tmpl'),
    folder('css'),
    folder('img'),
    folder('fonts')
]

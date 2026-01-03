from . import Application
from .util import Pipe
from aiohttp import web
from aridity.config import Config
from contextlib import ExitStack
from datetime import datetime
from diapyr import types
from flask import Flask, g, request
from http import HTTPStatus
from mimetypes import guess_type
from os.path import normpath, pardir
from pathlib import Path
from splut.actor import Spawn
from urllib.parse import urlencode
from urllib.request import urlopen
from werkzeug.http import parse_accept_header
import gzip, logging

log = logging.getLogger(__name__)

class SiteMeter:

    class Worker:

        def __init__(self, url, basedata):
            self.url = url
            self.basedata = basedata

        def send(self, info):
            with urlopen(self.url, urlencode(dict(self.basedata, info = info)).encode('ascii')):
                pass

    @types(Config, Spawn)
    def __init__(self, config, spawn):
        c = config.sitemeter
        args = c.url, dict(env = c.env, site = c.site)
        self.actor = spawn(*(self.Worker(*args) for _ in range(c.workers)))

    @web.middleware
    async def middleware(self, request, handler):
        hitinfo = f"{request.method} {request.path_qs} {request.headers.get('Referer')} {request.headers.get('X-Forwarded-For')} {request.headers.get('User-Agent')}"
        log.debug(hitinfo)
        self.actor.send(f"{datetime.now()} {hitinfo}").andforget(log)
        return await handler(request)

class AIOApplication(web.Application, Application):

    @staticmethod
    def htmlresponse(text, **kwargs):
        return web.Response(content_type = 'text/html', text = text, **kwargs)

def _before():
    g.exitstack = ExitStack().__enter__()

def _teardown(exc):
    try:
        if exc is not None: # Otherwise do it on response close.
            assert not g.exitstack.__exit__(type(exc), exc, exc.__traceback__), 'Cannot suppress exception.'
    except:
        log.exception('Cleanup failed:')

class FlaskApplication(Application):

    def __init__(self, *args, **kwargs):
        self.flask = flask = Flask(*args, **kwargs)
        flask.before_request(_before)
        flask.teardown_request(_teardown)
        class Response(flask.response_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.call_on_close(g.exitstack.close)
        flask.response_class = Response

    def __call__(self, environ, start_response):
        return self.flask(environ, start_response)

    def route(self, rule, view_func, **options):
        self.flask.add_url_rule(rule, view_func = view_func, **options)

    def stream(self, basepath, uri): # XXX: Validate hash in query?
        def response(isgz, ungz):
            def close():
                log.debug('Close file.')
                f.close()
            path = gzpath if isgz else ogpath
            t, enc = guess_type(path)
            assert ('gzip' if isgz else None) == enc
            f = gzip.open(path) if ungz else path.open('rb')
            g.exitstack.callback(close)
            r = self.toresponse(HTTPStatus.OK, None, f, mimetype = t)
            if isgz and not ungz:
                r.headers['Content-Encoding'] = enc
            return r # XXX: Add Cache-Control?
        relpath = Path(normpath(uri))
        assert pardir not in relpath.parts
        ogpath = basepath / relpath
        gzpath = ogpath.with_name(f"{ogpath.name}.gz")
        if parse_accept_header(request.headers.get('Accept-Encoding')).quality('gzip'):
            return response(True, False) if gzpath.exists() else response(False, False)
        return response(False, False) if ogpath.exists() else response(True, True)

    def toresponse(self, status, headersornone, payload, **kwargs):
        statusline = f"{status.value} {status.phrase}"
        log.debug("Send: %s", statusline)
        return self.flask.response_class(Pipe(payload) if hasattr(payload, 'read') else payload, statusline, headersornone, **kwargs)

from .util import canon, patch
from email.message import EmailMessage
from io import BytesIO
from werkzeug.datastructures import Headers, MultiDict
from werkzeug.http import _hop_by_hop_headers
from werkzeug.wrappers import Request

class Application: pass

@patch(Headers, classmethod)
def fromresponse(cls, response):
    headers = cls()
    for k, x in response.getheaders():
        if canon(k) not in _hop_by_hop_headers:
            headers.add(k, x)
    return headers

@patch(Headers)
def contentcharset(headers):
    msg = EmailMessage()
    msg['Content-Type'], = headers.getlist('content-type')
    return msg.get_content_charset()

@patch(Headers)
def safedict(headers):
    canonkeys = set()
    d = {}
    for realk, v in headers:
        canonk = canon(realk)
        assert canonk not in canonkeys
        canonkeys.add(canonk)
        d[realk] = v
    return d

@patch(MultiDict)
def uniqueornone(md, key):
    vals = md.getlist(key)
    if vals:
        val, = vals
        return val

@patch(Request)
def formpeek(request):
    request.get_data() # Cache the stream.
    return request.form

@patch(Request)
def streamorcached(request):
    try:
        cached = request._cached_data
    except AttributeError:
        assert 'form' not in request.__dict__, 'Stream consumed without being cached.'
        return request.stream
    return BytesIO(cached)

from concurrent.futures import ThreadPoolExecutor
from diapyr import types
from functools import lru_cache
from splut.actor import Spawn
import asyncio, logging

log = logging.getLogger(__name__)

@lru_cache(maxsize = 128)
def canon(k):
    return k.lower()

def patch(cls, deco = lambda x: x):
    return lambda f: setattr(cls, f.__name__, deco(f))

class Pipe:

    bufsize = 16 * 1024

    def __init__(self, f):
        self.f = f

    def __iter__(self):
        n = 0
        while True:
            v = self.f.read(self.bufsize)
            if not v:
                break
            yield v
            n += len(v)
        log.debug("Piped: %s", n)

async def _transfer(f, g):
    try:
        x = f.result()
    except BaseException as e:
        g.set_exception(e)
    else:
        g.set_result(x)

class ThreadPool:

    @types()
    def __init__(self):
        self.e = ThreadPoolExecutor()

    @types(this = Spawn)
    def spawnfactory(self):
        return Spawn(self.e)

    def bg(self, task, *args, **kwargs):
        loop = asyncio.get_running_loop()
        g = loop.create_future()
        self.e.submit(task, *args, **kwargs).add_done_callback(lambda f: asyncio.run_coroutine_threadsafe(_transfer(f, g), loop))
        return g

    def dispose(self):
        self.e.shutdown()

'Website entrypoint.'
from aiohttp import web
from aridity.config import ConfigCtrl
from diapyr import DI
from pathlib import Path
from weeaboo import Application
import logging, os

def main():
    logging.basicConfig(format = "%(levelname)s %(message)s", level = logging.DEBUG)
    cc = ConfigCtrl()
    cc.load('/site/deploy/LOADME.arid')
    deployconf = cc.node
    stat = Path(deployconf.img.root).stat()
    os.setgid(stat.st_gid)
    os.setuid(stat.st_uid)
    del os.environ['HOME']
    cc = ConfigCtrl()
    cc.load('/site/etc/LOADME.arid')
    appconf = cc.node
    di = DI()
    di.add(appconf)
    for cls in appconf.applicationcls:
        di.add(cls)
    web.run_app(di(Application), port = deployconf.listenport)

if '__main__' == __name__:
    main()

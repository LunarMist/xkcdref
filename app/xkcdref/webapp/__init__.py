import logging

logging.basicConfig()

import coloredlogs

coloredlogs.install(
    fmt='[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
    field_styles={
        'hostname': {'color': 'magenta'},
        'programname': {'color': 'cyan'},
        'name': {'color': 'blue'},
        'levelname': {'color': 'magenta'},
        'asctime': {'color': 'green'}
    }
)

from flask import Flask

app = Flask(__name__)

from xkcdref import settings

from xkcdref.core.datastore.sitedatastore import SiteDataStore

db = SiteDataStore(settings.XKCD_DB_LOCATION)

from xkcdref.core.datastore.sitecache import SiteCache

cache = SiteCache(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

from xkcdref.webapp import views, api, filters

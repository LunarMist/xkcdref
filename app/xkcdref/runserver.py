# Must be the first lines to ensure concurrency
from gevent.monkey import patch_all
patch_all()

import logging

from gevent.pywsgi import WSGIServer
from gevent.pool import Pool

from xkcdref.webapp import app
from xkcdref import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run():
    args, _ = settings.args_parser.parse_known_args()

    # Start the webserver
    if args.debug:
        logger.warn('Running in debug mode')
        app.run(debug=args.debug, port=args.port, host=args.host, use_reloader=True)
    else:
        logger.info('Running with gevent')
        http_server = WSGIServer((args.host, args.port), app, spawn=Pool(settings.MAX_CONNECTIONS))
        http_server.serve_forever()


if __name__ == '__main__':
    run()

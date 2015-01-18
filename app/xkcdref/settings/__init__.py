import argparse
import logging

from base import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Build cli args parser
args_parser = argparse.ArgumentParser()
args_parser.add_argument('--settings', help='[dev-mac, dev-win, prod] (default: prod)', default='prod')
args_parser.add_argument('--debug', help='enable debug mode (default: false)', action='store_true')
args_parser.add_argument('--host', help='host (default: ' + DEFAULT_BIND_HOST + ')', default=DEFAULT_BIND_HOST)
args_parser.add_argument('--port', help='port (default: ' + str(DEFAULT_BIND_PORT) + ')', type=int,
                         default=DEFAULT_BIND_PORT)

# Parse the args
args, _ = args_parser.parse_known_args()

# Load the appropriate settings
if args.settings == 'dev-mac':
    logger.info('Loading dev-mac settings')
    from dev_mac import *
elif args.settings == 'dev-win':
    logger.info('Loading dev-win settings')
    from dev_win import *
elif args.settings == 'prod':
    logger.info('Loading prod settings')
    from prod import *
else:
    logger.warn('Using BASE settings')

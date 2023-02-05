import logging
import os


__version__ = os.getenv('APP_VERSION', 'dev')
logging.basicConfig(level=logging.DEBUG)

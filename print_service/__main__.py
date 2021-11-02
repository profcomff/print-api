import logging
import sys

from print_service.cli import main


logging.basicConfig(level=logging.DEBUG)

sys.exit(main(obj={}))

import logging
import logging.config
import os

from huey import SqliteHuey

from utils import get_example_notebooks


class HueyConfig(object):
    BROKER_URL = os.environ.get('BROKER_URL', '/tmp/db.sqlite')


class AppConfig(object):
    DEFAULT_OUTPUT_DESTINATION = os.path.join(
        os.path.abspath(os.path.dirname(__name__)),
        'jobs'
    )

    OUTPUT_DESTINATION = os.environ.get(
            'OUTPUT_DESTINATION', DEFAULT_OUTPUT_DESTINATION)

    if not os.path.exists(OUTPUT_DESTINATION):
        os.mkdir(OUTPUT_DESTINATION)

    NOTEBOOKS_DIR = os.path.join(
            os.path.dirname(os.path.abspath(__name__)), 'notebooks')
    EXAMPLES_NOTEBOOKS = get_example_notebooks(NOTEBOOKS_DIR)


huey = SqliteHuey(filename=HueyConfig.BROKER_URL)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('notebooks')

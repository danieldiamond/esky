import glob
import logging
import logging.config
import os

from huey import SqliteHuey


def get_example_notebooks(directory):
    files = glob.glob(os.path.join(directory, '*'))
    notebooks = {}
    for path in files:
        key = os.path.basename(path)
        notebooks[key] = path

    return notebooks


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

    EXAMPLES_DIR = os.path.join(
            os.path.dirname(os.path.abspath(__name__)), 'examples')
    EXAMPLES_NOTEBOOKS = get_example_notebooks(EXAMPLES_DIR)


huey = SqliteHuey(filename=HueyConfig.BROKER_URL)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('notebooks')

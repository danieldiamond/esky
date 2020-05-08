import glob
import os

from nbconvert.nbconvertapp import NbConvertApp
from nbconvert.writers import FilesWriter
from nbconvert.exporters.html import HTMLExporter


def get_example_notebooks(directory):
    files = glob.glob(os.path.join(directory, '*'))
    notebooks = {}
    for path in files:
        key = os.path.basename(path)
        notebooks[key] = path

    return notebooks


def send_to_s3(origin, destination):
    pass


def write_nb_to_html(filename):
    nbc = NbConvertApp()
    nbc.exporter = HTMLExporter()
    nbc.writer = FilesWriter()
    nbc.convert_single_notebook(filename)

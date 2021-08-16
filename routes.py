__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

from controller import plag_detection
from controller import document
from controller import announcement


def add_prefix(uri):
    return "{}{}".format('/api/v1/plagiarism', uri)


def register_urls(api):
    """
    Maps all the endpoints with controllers.
    """
    api.add_resource(plag_detection.PlagiarismDetection, add_prefix('/detect'))
    api.add_resource(document.Document, add_prefix('/documents'))
    api.add_resource(announcement.Announcement, add_prefix('/announcement'))

__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

from controller import document, announcement, plag_detection, analysisHistory, commonPhraseController, similarDocumentController


def add_prefix(uri):
    return "{}{}".format('/api/v1/plagiarism', uri)


def register_urls(api):
    """
    Maps all the endpoints with controllers.
    """
    api.add_resource(plag_detection.PlagiarismDetection, add_prefix('/detect'))
    api.add_resource(document.Document, add_prefix('/documents'))
    api.add_resource(announcement.Announcement, add_prefix('/announcement'))
    api.add_resource(analysisHistory.AnalysisHistory, add_prefix('/analysisHistory'))
    api.add_resource(commonPhraseController.CommonPhraseController, add_prefix('/commonPhrase'))
    api.add_resource(similarDocumentController.SimilarDocumentController, add_prefix('/similarDocument'))

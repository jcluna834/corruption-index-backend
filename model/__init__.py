__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

from model.document import Document
from model.announcement import Announcement
from model.analysisHistory import AnalysisHistory
from model.commonPhrase import CommonPhrase

# Import and register all the models here.
__all__ = ["Document", "Announcement", "AnalysisHistory", "CommonPhrase"]

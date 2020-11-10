import datetime

__author__ = "Julio Luna"
__email__ = "jcluna@unicauca.edu.co"

from controller.base import BaseController
import pylev
from difflib import SequenceMatcher

class FunctionsPlagiarism(BaseController):

    # Retorna el valor de la distacia de levenschtein entre dos cadenas
    def getLevenshteinDistance(self, a, b):
        a = a.split(" ")
        b = b.split(" ")
        return pylev.levenshtein(a, b)

    # Retorna el valor del ratio similitud entre dos cadenas
    def getRatioSequenceMatcher(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    # Retorna las palabras diferentes emtre dos cadenas - Retorna las diferentes en B
    def getUncommonWords(self, a, b):
        un_comm = [i for i in "".join(b).split() if i not in "".join(a).split()]
        return un_comm
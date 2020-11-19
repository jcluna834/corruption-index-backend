import datetime

__author__ = "Julio Luna"
__email__ = "jcluna@unicauca.edu.co"

from controller.base import BaseController
import pylev
from difflib import SequenceMatcher
import re
from nltk.corpus import stopwords
import requests
from bs4 import BeautifulSoup
from nltk.stem import SnowballStemmer
from model.uncommon_word import Uncommon_word
from nltk import word_tokenize
import lxml

stemmer = SnowballStemmer('spanish')
stop_words = set(stopwords.words('spanish'))


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

    # Retorna una cadena de texto limpia, sin caracteres especiales
    def getStringClean(self, string):
        return re.sub(r'[^ \nA-Za-z0-9À-ÖØ-öø-ÿ]+', '', string)

    # Se obtiene el performance de cada Uncommon word
    def getHighlightPerformance(self, uncommon_words, stemmed_text):
        uncommon_words = [each_string.lower() for each_string in uncommon_words]
        # se aplica stopwords
        #print(uncommon_words)
        filtered_sentence = [w for w in uncommon_words if not w in stop_words]
        #se aplica stem
        stemmed_text = [stemmer.stem(i) for i in word_tokenize(stemmed_text)]
        #print(filtered_sentence)
        # Se aplica stem
        uncommon_words_stemmed = [stemmer.stem(i) for i in uncommon_words]
        #print(uncommon_words_stemmed)
        # Se crean los objetos
        my_uncommon_words = []
        for i in range(len(uncommon_words_stemmed)):
            my_uncommon_words.append(Uncommon_word(uncommon_words[i], uncommon_words_stemmed[i], 'None'))

        # Se eliminan las palabras stem
        #print("------------------Se revisan de uncommon_words las stem---------------------")
        for obj in my_uncommon_words:
            if obj.uncommon_word_stem in stemmed_text:
                obj.alerta = "naranja"

        for word in filtered_sentence:
            #print(word)
            try:
                sinonimos, sinonimos_stem = self.getSynoymsWordReference(word)
                #print(sinonimos)
                for sinonimo_stem in sinonimos_stem:
                    if sinonimo_stem in stemmed_text:
                        obj = [x for x in my_uncommon_words if x.uncommon_word == word]
                        obj[0].alerta = "amarillo"
            except:
                print("Error to get synonyms")

        return self.get_to_dict(my_uncommon_words)

    def get_to_dict(self, my_uncommon_words):
        my_uncommon_response = []
        for my_uncommon in my_uncommon_words:
            res_my_uncommon_data = {
                'uncommon_word': my_uncommon.uncommon_word,
                'alerta': my_uncommon.alerta,
            }
            my_uncommon_response.append(res_my_uncommon_data)
        return my_uncommon_response

    # Sinonimos mediante wordreference
    def getSynoymsWordReference(self, word):
        try:
            # URL de wordreference donde se buscaran los sinonimos
            url = 'http://www.wordreference.com/sinonimos/'
            buscar = url + word
            resp = requests.get(buscar)
            bs = BeautifulSoup(resp.text, 'lxml')
            lista = bs.find_all(class_='trans clickable')
            for sin in lista:
                sinonim = sin.find_all('li')
                for fin in sinonim[0]:
                    sinonimos = fin.split(',  ')
                    filtered_sentence = [stemmer.stem(i) for i in sinonimos]
                    return sinonimos, filtered_sentence
        except:
            return [], []

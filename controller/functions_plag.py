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
from model.uncommon_word import Uncommon_word, Similar_word
from nltk import word_tokenize
import lxml

#Se descarga sinonimos al inicio
'''import nltk
nltk.download('stopwords')
'''
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
        uncommon_words = [i for i in "".join(b).split() if i not in "".join(a).split()]
        filtered_sentence = [w for w in uncommon_words if not w.lower() in stop_words]
        return filtered_sentence

    # Retorna las palabras diferentes emtre dos cadenas - Retorna las diferentes en B
    def getCommonWords(self, a, b):
        common_words = [i for i in "".join(b).split() if i in "".join(a).split()]
        filtered_sentence = [w for w in common_words if not w.lower() in stop_words]
        filtered_sentence_remove_d = list(dict.fromkeys(filtered_sentence))
        return filtered_sentence_remove_d

    # Retorna una cadena de texto limpia, sin caracteres especiales
    def getStringClean(self, string):
        return re.sub(r'[^ \nA-Za-z0-9À-ÖØ-öø-ÿ]+', '', string)

    # Se obtiene el performance de cada Uncommon word
    def getHighlightPerformance(self, uncommon_words, stemmed_text):
        uncommon_words = [each_string.lower() for each_string in uncommon_words]
        # se aplica stopwords al highlight
        filtered_sentence = [w for w in uncommon_words if not w in stop_words]
        #se aplica stem a la frase entrante
        # se aplica stopwords a la frase entrante
        stemmed_text_list = [w for w in word_tokenize(stemmed_text) if not w in stop_words]
        stemmed_text = [stemmer.stem(i) for i in stemmed_text_list]

        my_similar_words = []
        for i in range(len(stemmed_text_list)):
            my_similar_words.append(Similar_word(stemmed_text_list[i], stemmed_text[i]))

        # Se aplica stem
        uncommon_words_stemmed = [stemmer.stem(i) for i in uncommon_words]
        # Se crean los objetos
        my_uncommon_words = []
        #Se listan las palabras que no tienen relación
        for i in range(len(uncommon_words_stemmed)):
            my_uncommon_words.append(Uncommon_word(uncommon_words[i], uncommon_words_stemmed[i], '', 'None'))

        # Se revisa si la palabra fue parafraseada (steam)
        for obj in my_uncommon_words:
            similar_word = next((w for w in my_similar_words if w.similar_word_stem == obj.uncommon_word_stem), None)
            if (similar_word is not None):
                obj.alerta = "naranja"
                obj.similar_word = similar_word.similar_word

        for word in filtered_sentence:
            try:
                sinonimos, sinonimos_stem = self.getSynoymsWordReference(word)
                for sinonimo_stem in sinonimos_stem:
                    similar_word = next((w for w in my_similar_words if w.similar_word_stem == sinonimo_stem), None)
                    if (similar_word is not None):
                        obj = [x for x in my_uncommon_words if x.uncommon_word == word]
                        obj[0].alerta = "amarillo"
                        obj[0].similar_word = similar_word.similar_word
            except:
                print("Error to get synonyms")

        return self.get_to_dict(my_uncommon_words)

    def get_to_dict(self, my_uncommon_words):
        my_uncommon_response = []
        for my_uncommon in my_uncommon_words:
            res_my_uncommon_data = {
                'uncommon_word': my_uncommon.uncommon_word,
                'alerta': my_uncommon.alerta,
                'similar_word': my_uncommon.similar_word,
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

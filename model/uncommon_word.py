__author__ = "Julio Luna"
__email__ = "jcluna@unicauca.edu.co"

import json

class Similar_word:
    def __init__(self, similar_word, similar_word_stem):
            self.similar_word = similar_word
            self.similar_word_stem = similar_word_stem

    def __str__(self):
        return self.similar_word

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'similar_word': self.similar_word,
            'similar_word_stem': self.similar_word_stem
        }

class Uncommon_word:
    def __init__(self, uncommon_word, uncommon_word_stem, similar_word, alerta):
        self.uncommon_word = uncommon_word
        self.uncommon_word_stem = uncommon_word_stem
        self.similar_word = similar_word
        self.alerta = alerta

    def __str__(self):
        return self.uncommon_word

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'uncommon_word': self.uncommon_word,
            'uncommon_word_stem': self.uncommon_word_stem,
            'similar_word': self.similar_word,
            'alerta': self.alerta
        }

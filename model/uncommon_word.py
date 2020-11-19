__author__ = "Julio Luna"
__email__ = "jcluna@unicauca.edu.co"

import json


class Uncommon_word:
    def __init__(self, uncommon_word, uncommon_word_stem, alerta):
        self.uncommon_word = uncommon_word
        self.uncommon_word_stem = uncommon_word_stem
        self.alerta = alerta

    def __str__(self):
        return self.title

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'uncommon_word': self.uncommon_word,
            'uncommon_word_stem': self.uncommon_word_stem,
            'alerta': self.alerta
        }

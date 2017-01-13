import re

import nltk
import hunspell
from django.core.exceptions import ValidationError
from django.conf import settings

from .utils import ContractionlessTokenizer


class SpellingError(ValidationError):
    pass


class SpellingValidator:

    CHARACTER_START = re.compile(r'^\w')

    def __init__(self, language):
        self.language = language
        self.hunspell = hunspell.HunSpell(settings.HUNSPELL[language]['DIC'],
                                          settings.HUNSPELL[language]['AFF'])
        self.tokenizer = ContractionlessTokenizer()

    def __call__(self, text):
        tokens = [token
                  for sentence in nltk.tokenize.sent_tokenize(text)
                  for token in self.tokenizer.tokenize(sentence)
                  if self.CHARACTER_START.search(token) is not None]
        mispelled = [token for token in tokens
                     if not self.hunspell.spell(token)]

        if len(mispelled) > 0:
            raise SpellingError("Mispellings: {}"
                                .format(", ".join(mispelled)))


class PunctuationError(ValidationError):
    pass


class PunctuationValidator:

    NOREPEATS = re.compile(r'([,.;:!?] *){2,}')
    EXCLUDED = re.compile(r'[\][{}<>\\|/+=_*&^%$#@~`]')

    def __call__(self, text):
        if self.NOREPEATS.search(text):
            raise PunctuationError("RepeatedPunctuation")

        if self.EXCLUDED.search(text):
            raise PunctuationError("ExcludedPunctuation")

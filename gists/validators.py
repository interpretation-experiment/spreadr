import re

import nltk
import hunspell
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.conf import settings

from .utils import ContractionlessTokenizer


class SpellingError(ValidationError):
    pass


@deconstructible
class SpellingValidator:

    CHARACTER_START = re.compile(r'^\w')

    def __init__(self, language):
        self.language = language
        self.hunspellers = [hunspell.HunSpell(dicts['DIC'], dicts['AFF'])
                            for dicts in settings.HUNSPELL[language]]
        self.tokenizer = ContractionlessTokenizer()

    def __call__(self, text):
        from .models import GistsConfiguration
        if GistsConfiguration.get_solo().jabberwocky_mode:
            # Spell-checking deactivated for Jabberwockies
            return

        tokens = [token
                  for sentence in nltk.tokenize.sent_tokenize(text)
                  for token in self.tokenizer.tokenize(sentence)
                  if self.CHARACTER_START.search(token) is not None]
        mispelled = [token for token in tokens
                     if not sum([speller.spell(token)
                                 for speller in self.hunspellers])]

        if len(mispelled) > 0:
            raise SpellingError("SpellingError: {}"
                                .format(", ".join(mispelled)))

    def __eq__(self, other):
        return self.language == other.language


class PunctuationError(ValidationError):
    pass


@deconstructible
class PunctuationValidator:

    REPEATS = re.compile(r'([,.;:!?-] *){2,}')
    EXCLUDED = re.compile(r'[\][{}<>\\|/+=_*&^%$#@~`]+')

    def __call__(self, text):
        repeats = self.REPEATS.search(text)
        if repeats is not None:
            raise PunctuationError("PunctuationRepeatedError: "
                                   + repeats.group(0))

        excluded = self.EXCLUDED.search(text)
        if excluded is not None:
            raise PunctuationError("PunctuationExcludedError: "
                                   + excluded.group(0))

    def __eq__(self, other):
        return True

import re

import nltk


class ContractionlessTokenizer(nltk.tokenize.treebank.TreebankWordTokenizer):
    """Treebank tokenizer which ignores contractions.

    This is near-identical to the original TreebankWordTokenizer, but with a
    few regexes changed: we restrict the ENDING_QUOTES regexes to only those
    not involving contractions, and empty out all the CONTRACTIONS* regexes.

    """

    ENDING_QUOTES = [
        (re.compile(r'"'), " '' "),
        (re.compile(r'(\S)(\'\')'), r'\1 \2 '),
    ]
    CONTRACTIONS2 = []
    CONTRACTIONS3 = []
    CONTRACTIONS4 = []


def memoize(func):
    cache = {}

    def inner(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return inner


def levenshtein(s1, s2):
    """Compute levenshtein distance between `s1` and `s2`."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s2:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # previous_row and current_row are one character longer than s2,
            # hence the 'j + 1'
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

import contextlib
import os
import unicodedata
from pathlib import Path

import fasttext

import ftfy
import langcodes


FT_LANGUAGES = [
    'af', 'als', 'am', 'an', 'ar', 'arz', 'as', 'ast', 'av', 'az', 'azb', 'ba',
    'bar', 'bcl', 'be', 'bg', 'bh', 'bn', 'bo', 'bpy', 'br', 'bs', 'bxr', 'ca',
    'cbk', 'ce', 'ceb', 'ckb', 'co', 'cs', 'cv', 'cy', 'da', 'de', 'diq',
    'dsb', 'dty', 'dv', 'el', 'eml', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi',
    'fr', 'frr', 'fy', 'ga', 'gd', 'gl', 'gn', 'gom', 'gu', 'gv', 'he', 'hi',
    'hif', 'hr', 'hsb', 'ht', 'hu', 'hy', 'ia', 'id', 'ie', 'ilo', 'io', 'is',
    'it', 'ja', 'jbo', 'jv', 'ka', 'kk', 'km', 'kn', 'ko', 'krc', 'ku', 'kv',
    'kw', 'ky', 'la', 'lb', 'lez', 'li', 'lmo', 'lo', 'lrc', 'lt', 'lv', 'mai',
    'mg', 'mhr', 'min', 'mk', 'ml', 'mn', 'mr', 'mrj', 'ms', 'mt', 'mwl', 'my',
    'myv', 'mzn', 'nah', 'nap', 'nds', 'ne', 'new', 'nl', 'nn', 'no', 'oc',
    'or', 'os', 'pa', 'pam', 'pfl', 'pl', 'pms', 'pnb', 'ps', 'pt', 'qu', 'rm',
    'ro', 'ru', 'rue', 'sa', 'sah', 'sc', 'scn', 'sco', 'sd', 'sh', 'si', 'sk',
    'sl', 'so', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tk',
    'tl', 'tr', 'tt', 'tyv', 'ug', 'uk', 'ur', 'uz', 'vec', 'vep', 'vi', 'vls',
    'vo', 'wa', 'war', 'wuu', 'xal', 'xmf', 'yi', 'yo', 'yue', 'zh'
]


SPACY_LANGUAGES = [
    'af', 'am', 'ar', 'az', 'bg', 'bn', 'ca', 'cs', 'da', 'de',
    'el', 'en', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'ga', 'grc', 'gu',
    'he', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'kn', 'ko', 'ky',
    'lb', 'lij', 'lt', 'lv', 'mk', 'ml', 'mr', 'nb', 'ne', 'nl',
    'pl', 'pt', 'ro', 'ru', 'sa', 'si', 'sk', 'sl', 'sq', 'sr', 'sv',
    'ta', 'te', 'th', 'ti', 'tl', 'tn', 'tt', 'uk', 'ur', 'vi', 'yo', 'zh'
]


def data_file(path):
    """
    Get a path to a file in the local 'data' directory.
    """
    my_location = Path(__file__).parent
    return str(my_location / 'data' / path)


def align_language_to_spacy(language):
    """
    Given a language code, get the closest-matching language code that
    spaCy supports, or 'und' if there is no match.

    >>> align_language_to_spacy('fr')
    'fr'
    >>> align_language_to_spacy('iw')  # old language code for Hebrew
    'he'
    >>> align_language_to_spacy('zz')  # not a language
    'und'
    >>> align_language_to_spacy('nan')
    'zh'
    >>> align_language_to_spacy('no')
    'nb'
    """
    matched_language, _dist = langcodes.closest_match(language, SPACY_LANGUAGES)
    return matched_language


def clean_text(text):
    """
    Clean text for better language detection, keeping only letters, 'marks',
    and whitespace. (Marks are used in some languages for diacritical marks
    that appear over letters.)
    """
    cleaned_text = ftfy.fix_text(text, normalization='NFKC').casefold()

    # Keep only letters (L), marks (M), and whitespace (Z)
    kept_chars = [ch for ch in cleaned_text if unicodedata.category(ch)[0] in 'LMZ']
    cleaned_text = ''.join(kept_chars)

    # Remove extra whitespaces
    cleaned_text = ' '.join(cleaned_text.split())

    return cleaned_text


class LanguageIdentifier:
    def __init__(self, name='lid.176.ftz'):
        """
        Create a LanguageIdentifier object that stores a loaded language-ID
        model and uses it to identify languages.

        The optional 'name' is the filename of the model that should be looked
        for in this module's standard paths.
        """
        # Open a FastText model without sending a useless warning to stderr
        with open(os.devnull, "w") as f, contextlib.redirect_stderr(f):
            self.ft_model = fasttext.load_model(data_file(name))

    def detect_language(self, text):
        """
        Predict the language of a text using fastText.

        Returns a pair of the detected language code and its confidence (from
        0 to 1). The confidence is a softmax that's meant to be a probability,
        but it is too overconfident to accurately represent a probability.
        """
        cleaned = clean_text(text)
        prediction_struct = self.ft_model.predict(cleaned)

        # The structure returned by fastText looks like:
        # (('__label__en',), array([0.99047953]))

        language_struct, confidence_struct = prediction_struct

        # Extract the predicted language code from this:
        label_size = len('__label__')
        pred_language = align_language_to_spacy(
            language_struct[0][label_size:]
        )

        # Once we can depend on Python 3.9, the above would be:
        # language_struct[0].removeprefix('__label__')

        # And then the confidence in the prediction:
        pred_confidence = confidence_struct[0]
        return (pred_language, pred_confidence)

from functools import lru_cache
from langcodes import Language, closest_match


def _language_in_list(language, targets, max_distance=10):
    """
    A helper function to determine whether this language matches one of the
    target languages, with a match score above a certain threshold.

    The languages can be given as strings (language tags) or as Language
    objects. `targets` can be any iterable of such languages.
    """
    matched = closest_match(language, targets, max_distance=max_distance)
    return matched[0] != 'und'


@lru_cache(maxsize=None)
def get_language_info(language):
    """
    Looks up the things we need to know about how to handle text in a given
    language. This will return a dictionary with the following fields:

    'script': a BCP 47 script code such as 'Latn', 'Cyrl', 'Arab'...

        Indicates the script that tokens in this language should be in,
        _after_ our preprocessing.

    'normal_form': 'NFC' or 'NFKC'

        How "should" Unicode be normalized when comparing text in this
        language? This is not a standard, it's just based on experience.
        Many languages need NFKC normalization for text comparisons to work
        properly, but in many European languages, NFKC normalization is
        excessive and loses information.

    'dotless_i': True or False

        Is "ı" the lowercase of "I" in this language, as in Turkish?

    'diacritics_under': 'cedillas', 'commas', or None

        Should we convert any diacritics that are under the letters "s" and
        "t" in this language? 'cedillas' means we should convert commas to
        cedillas, and 'commas' means we should convert cedillas to commas.

    'transliteration': 'sr-Latn', 'az-Latn', or None

        Indicates a type of transliteration that we should use for normalizing
        a multi-script language. 'sr-Latn' means to use Serbian romanization,
        and 'az-Latn' means to use Azerbaijani romanization.
    """
    # The input is probably a string, so parse it into a Language. If it's
    # already a Language, it will pass through.
    language = Language.get(language)

    # Assume additional things about the language, such as what script it's in,
    # using the "likely subtags" table
    language_full = language.maximize()

    # Start the `info` dictionary with default values, including the 'script'
    # value that we now know from `language_full`.
    info = {
        'script': language_full.script,
        'tokenizer': 'regex',
        'normal_form': 'NFKC',
        'remove_marks': False,
        'dotless_i': False,
        'diacritics_under': None,
        'transliteration': None,
        'lookup_transliteration': None
    }

    # Cased alphabetic scripts get NFC normal form
    if info['script'] in ['Latn', 'Grek', 'Cyrl']:
        info['normal_form'] = 'NFC'

    if _language_in_list(language, ['tr', 'az', 'kk']):
        info['dotless_i'] = True
        info['diacritics_under'] = 'cedillas'
    elif _language_in_list(language, ['ro']):
        info['diacritics_under'] = 'commas'

    if _language_in_list(language, ['sr']):
        info['transliteration'] = 'sr-Latn'
    elif _language_in_list(language, ['az']):
        info['transliteration'] = 'az-Latn'
    elif _language_in_list(language, ['kk']):
        info['transliteration'] = 'kk-Latn'

    return info

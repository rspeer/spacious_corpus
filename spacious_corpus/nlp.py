"""
Utilities for doing multilingual NLP.

`normalize_text` puts text in a standard form that includes Unicode
normalization and case-folding, plus other fixes that are specific to the
language.

`make_nlp_stack` gets a simple spaCy NLP stack that is appropriate to the
language.
"""

from ftfy.fixes import uncurl_quotes
import re
import spacy
import unicodedata

from .language_info import get_language_info
from .transliterate import transliterate

MAX_LINE_LENGTH = 1_000_000


MARK_RE = re.compile(
    "["
    "\u0591-\u05c7"  # Hebrew marks
    "\u0610-\u061a\u064b-\u065f\u06d6-\u06ed"  # Arabic marks
    "\N{ARABIC TATWEEL}"
    "]"
)


def make_nlp_stack(lang):
    """
    Get a simple spaCy NLP stack that is appropriate to the language.
    """
    if lang == "ko":
        return spacy.blank(
            "ko", config={"nlp": {"tokenizer": {"@tokenizers": "spacy.Tokenizer.v1"}}}
        )
    else:
        return spacy.blank(lang)


def normalize_text(text, language):
    """
    This function applies pre-processing steps that convert forms of words
    considered equivalent into one standardized form.

    As one straightforward step, it case-folds the text. For the purposes of
    wordfreq and related tools, a capitalized word shouldn't have a different
    frequency from its lowercase version.

    The steps that are applied in order, only some of which apply to each
    language, are:

    - NFC or NFKC normalization, as needed for the language
    - Transliteration of multi-script languages
    - Abjad mark removal
    - Case folding
    - Fixing of diacritics

    We'll describe these steps out of order, to start with the more obvious
    steps.


    Case folding
    ------------

    The most common effect of this function is that it case-folds alphabetic
    text to lowercase:

    >>> normalize_text('Word', 'en')
    'word'

    This is proper Unicode-aware case-folding, so it eliminates distinctions
    in lowercase letters that would not appear in uppercase. This accounts for
    the German ß and the Greek final sigma:

    >>> normalize_text('groß', 'de')
    'gross'
    >>> normalize_text('λέξις', 'el')
    'λέξισ'

    In Turkish (and Azerbaijani), case-folding is different, because the
    uppercase and lowercase I come in two variants, one with a dot and one
    without. They are matched in a way that preserves the number of dots, which
    the usual pair of "I" and "i" do not.

    >>> normalize_text('HAKKINDA İSTANBUL', 'tr')
    'hakkında istanbul'


    Fixing of diacritics
    --------------------

    While we're talking about Turkish: the Turkish alphabet contains letters
    with cedillas attached to the bottom. In the case of "ş" and "ţ", these
    letters are very similar to two Romanian letters, "ș" and "ț", which have
    separate _commas_ below them.

    (Did you know that a cedilla is not the same as a comma under a letter? I
    didn't until I started dealing with text normalization. My keyboard layout
    even inputs a letter with a cedilla when you hit Compose+comma.)

    Because these letters look so similar, and because some fonts only include
    one pair of letters and not the other, there are many cases where the
    letters are confused with each other. We normalize these Turkish and
    Romanian letters to the letters each language prefers.

    >>> normalize_text('kișinin', 'tr')   # comma to cedilla
    'kişinin'
    >>> normalize_text('ACELAŞI', 'ro')   # cedilla to comma
    'același'


    Unicode normalization
    ---------------------

    Unicode text is NFC normalized in most languages, removing trivial
    distinctions between strings that should be considered equivalent in all
    cases:

    >>> word = normalize_text('natu\N{COMBINING DIAERESIS}rlich', 'de')
    >>> word
    'natürlich'
    >>> '\N{LATIN SMALL LETTER U WITH DIAERESIS}' in word
    True

    NFC normalization is sufficient (and NFKC normalization is a bit too strong)
    for many languages that are written in cased, alphabetic scripts.
    Languages in other scripts tend to need stronger normalization to properly
    compare text. So we use NFC normalization when the language's script is
    Latin, Greek, or Cyrillic, and we use NFKC normalization for all other
    languages.

    Here's an example in Japanese, where normalization changes the width (and
    the case) of a Latin letter that's used as part of a word:

    >>> normalize_text('Ｕターン', 'ja')
    'uターン'

    In Korean, NFKC normalization is important because it aligns two different
    ways of encoding text -- as individual letters that are grouped together
    into square characters, or as the entire syllables that those characters
    represent:

    >>> word = '\u1102\u1161\u11c0\u1106\u1161\u11af'
    >>> word
    '낱말'
    >>> len(word)
    6
    >>> word = normalize_text(word, 'ko')
    >>> word
    '낱말'
    >>> len(word)
    2


    Abjad mark removal
    ------------------

    There are many abjad languages, such as Arabic, Hebrew, Persian, and Urdu,
    where words can be marked with vowel points but rarely are. We remove characters
    classified as "marks" in Arabic and Hebrew scripts. We also remove an Arabic
    character called the tatweel, which is used to visually lengthen a word.

    >>> normalize_text("كَلِمَة", 'ar')
    'كلمة'
    >>> normalize_text("الحمــــــد", 'ar')
    'الحمد'

    Transliteration of multi-script languages
    -----------------------------------------

    Serbian, Azerbaijani, and Kazakh can be written in either Cyrillic or
    Latin letters.

    In Serbian, there is a well-established mapping from Cyrillic letters to
    Latin letters. We apply this mapping so that Serbian is always represented
    in Latin letters.

    >>> normalize_text('схваташ', 'sr')
    'shvataš'

    The transliteration is more complete than it needs to be to cover just
    Serbian, so that -- for example -- borrowings from Russian can be
    transliterated, instead of coming out in a mixed script.

    >>> normalize_text('культуры', 'sr')
    "kul'tury"

    Azerbaijani (Azeri) has a similar transliteration step to Serbian,
    and then the Latin-alphabet text is handled similarly to Turkish.

    >>> normalize_text('бағырты', 'az')
    'bağırtı'
    """
    # NFC or NFKC normalization, as needed for the language
    info = get_language_info(language)
    text = text.replace("\n", " ").replace("\t", " ").strip()
    text = unicodedata.normalize(info["normal_form"], text)

    # Transliteration of multi-script languages
    if info["transliteration"] is not None:
        text = transliterate(info["transliteration"], text)

    # Abjad mark removal
    text = remove_marks(text)

    # Case folding
    if info["dotless_i"]:
        text = casefold_with_i_dots(text)
    else:
        text = text.casefold()

    # Fixing of diacritics
    if info["diacritics_under"] == "commas":
        text = cedillas_to_commas(text)
    elif info["diacritics_under"] == "cedillas":
        text = commas_to_cedillas(text)

    # curly apostrophes become straight
    text = uncurl_quotes(text)

    return text


def remove_marks(text):
    """
    Remove decorations from words in abjad scripts:

    - Combining marks of class Mn, which tend to represent non-essential
      vowel markings.
    - Tatweels, horizontal segments that are used to extend or justify an
      Arabic word.
    """
    return MARK_RE.sub("", text)


def casefold_with_i_dots(text):
    """
    Convert capital I's and capital dotted İ's to lowercase in the way
    that's appropriate for Turkish and related languages, then case-fold
    the rest of the letters.
    """
    text = unicodedata.normalize("NFC", text).replace("İ", "i").replace("I", "ı")
    return text.casefold()


def commas_to_cedillas(text):
    """
    Convert s and t with commas (ș and ț) to cedillas (ş and ţ), which is
    preferred in Turkish.

    Only the lowercase versions are replaced, because this assumes the
    text has already been case-folded.
    """
    return text.replace(
        "\N{LATIN SMALL LETTER S WITH COMMA BELOW}",
        "\N{LATIN SMALL LETTER S WITH CEDILLA}",
    ).replace(
        "\N{LATIN SMALL LETTER T WITH COMMA BELOW}",
        "\N{LATIN SMALL LETTER T WITH CEDILLA}",
    )


def cedillas_to_commas(text):
    """
    Convert s and t with cedillas (ş and ţ) to commas (ș and ț), which is
    preferred in Romanian.

    Only the lowercase versions are replaced, because this assumes the
    text has already been case-folded.
    """
    return text.replace(
        "\N{LATIN SMALL LETTER S WITH CEDILLA}",
        "\N{LATIN SMALL LETTER S WITH COMMA BELOW}",
    ).replace(
        "\N{LATIN SMALL LETTER T WITH CEDILLA}",
        "\N{LATIN SMALL LETTER T WITH COMMA BELOW}",
    )

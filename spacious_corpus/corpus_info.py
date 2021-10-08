from typing import Optional
import langcodes


LANGUAGE_MAPS = {
    'google-ngrams': {
        'de': 'ger',
        'en': 'eng',
        'es': 'spa',
        'fr': 'fre',
        'he': 'heb',
        'it': 'ita',
        'ru': 'rus',
        'zh-Hans': 'chi_sim',
    },
    'opensubtitles': {
        'pt-PT': 'pt',
        'pt-BR': 'pt_br',
        'zh-Hans': 'zh_cn',
        'zh-Hant': 'zh_tw',
    },
    'globalvoices': {
        'ja': 'jp',
        'zh-Hans': 'zhs',
        'zh-Hant': 'zht'
    },
    'oscar': {
        'bs': 'sh',
        'hr': 'sh',
        'sr': 'sh',
    },
}


def match_source_language(source: str, lcode: str) -> Optional[str]:
    """
    Given a source name and a language code, get a matching language code
    supported by that source, or None if there is no match.

    If the result is not None, this is the language code that should be used
    to refer to the built corpus in that language.

    This function helps smooth over inconsistencies in lists of languages,
    such as 'nb' versus 'no' or 'zh-Hans' versus 'zh'.
    """
    supported = SOURCE_LANGUAGES[source]
    return langcodes.closest_supported_match(lcode, supported)


def upstream_source_language(source: str, lcode: str) -> str:
    """
    Given a source name and a language code, return the equivalent language
    code used by that source.

    For example, `map_source_language("google", "zh-Hans")` returns "chi_sim"
    for some godforsaken reason.

    This is needed in the Snakefile when downloading resources from their
    original locations, but should not be used to name outputs. For example,
    tokenized GlobalVoices in Simplified Chinese goes in
    `data/tokens/globalvoices/zh-Hans.zip`, not
    `data/tokens/globalvoices/zhs.zip`.
    """
    if source in LANGUAGE_MAPS:
        return LANGUAGE_MAPS[source].get(lcode, lcode)
    else:
        return lcode


SOURCE_LANGUAGES = {
    # GlobalVoices (LREC 2012), from OPUS -- languages with over 100,000 sentences
    #
    # GlobalVoices is multilingual news with a more left activist perspective than
    # the usual news sources. (If you're worried about the effect of this, consider
    # the effect of the decades that we've been doing the opposite by training NLP
    # on the Wall Street Journal.)
    'globalvoices': [
        'ar',
        'bn',
        'ca',
        'de',
        'el',
        'en',
        'es',
        'fr',
        'it',
        'ja',
        'mg',
        'pl',
        'pt',
        'ru',
        'sw',
        'zh-Hans',
        'zh-Hant',
    ],

    # Google Ngrams 2019
    'google-ngrams': [
        'de',
        'en',
        'es',
        'fr',
        'he',
        'it',
        'ru',
        'zh-Hans',
    ],

    # Jieba's built-in wordlist (supposedly MIT licensed?)
    'jieba': ['zh-Hans'],

    # NewsCrawl 2014, from the EMNLP Workshops on Statistical Machine Translation
    'newscrawl': ['cs', 'de', 'en', 'fi', 'fr', 'ru'],

    # OPUS's data files of OpenSubtitles 2018
    #
    # Include languages with at least 400 subtitle files, but skip 'ze', which is
    # not a real language code
    # (it seems to represent mixed Chinese and English in some form)
    'opensubtitles': [
        'ar',
        'bg',
        'bn',
        'bs',
        'ca',
        'cs',
        'da',
        'de',
        'el',
        'en',
        'es',
        'et',
        'eu',
        'fa',
        'fi',
        'fr',
        'gl',
        'he',
        'hr',
        'hu',
        'id',
        'is',
        'it',
        'ja',
        'ko',
        'lt',
        'lv',
        'mk',
        'ml',
        'ms',
        'nl',
        'nb',
        'pl',
        'pt-PT',
        'pt-BR',
        'pt',
        'ro',
        'ru',
        'si',
        'sk',
        'sl',
        'sq',
        'sr',
        'sv',
        'th',
        'tr',
        'uk',
        'vi',
        'zh-Hans',
        'zh-Hant',
        # TODO: merge pt-PT and pt-BR
    ],
    'oscar': [
        'ar',
        'az',
        'be',
        'bn',
        'bg',
        'bs',
        'ca',
        'cs',
        'da',
        'de',
        'el',
        'en',
        'es',
        'et',
        'fa',
        'fi',
        'fr',
        'gu',
        'he',
        'hi',
        'hr',
        'hu',
        'hy',
        'id',
        'is',
        'it',
        'ja',
        'ka',
        'kk',
        'ko',
        'lt',
        'lv',
        'mk',
        'ml',
        'mn',
        'mr',
        'nl',
        'no',
        'pl',
        'pt',
        'ro',
        'sk',
        'sl',
        'sq',
        'sr',
        'sv',
        'sw',
        'ta',
        'te',
        'th',
        'tl',
        'tr',
        'uk',
        'ur',
        'vi',
        'zh',

        # Removed languages that are less than 80% correct when audited:
        # gl, ne, mr
        #
        # based on Caswell et al. (2021), https://arxiv.org/pdf/2103.12028.pdf
    ],

    # Sufficiently large, non-spammy Wikipedias.
    # See https://meta.wikimedia.org/wiki/List_of_Wikipedias -- we're looking
    # for Wikipedias that have at least 100,000 articles and a "depth" measure
    # of 20 or more (indicating that they're not mostly written by bots).
    # Some Wikipedias with a depth of 10 or more are grandfathered into this list.
    'wikipedia': [
        'ar',
        'bg',
        'bs',
        'ca',
        'cs',
        'cy',
        'da',
        'de',
        'el',
        'en',
        'eo',
        'es',
        'et',
        'eu',
        'fa',
        'fi',
        'fr',
        'gl',
        'he',
        'hi',
        'hu',
        'hr',
        'hy',
        'id',
        'it',
        'ja',
        'ka',
        'ko',
        'la',
        'lt',
        'lv',
        'ms',
        'nn',
        'nb',
        'nl',
        'pl',
        'pt',
        'ro',
        'ru',
        'sk',
        'sl',
        'sv',
        'sr',
        'ta',
        'th',
        'tr',
        'uk',
        'ur',
        'uz',
        'vi',
        'zh',

        # Smaller but high-quality, high-depth Wikipedias
        'bn',
        'is',
        'ku',
        'mk',
        'my',
        'ml',
        'mn',
        'mr',
        'my',
        'or',
        'si',
        'te',
    ],
}

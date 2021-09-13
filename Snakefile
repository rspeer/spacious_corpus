import os
from collections import defaultdict

# A path to the directory where the data build should happen
DATA = 'data'

# Update this to be a currently-available date stamp for a Wikipedia export
# (TODO: automatically determine what the correct version is)
WP_VERSION = '20210901'

# What languages does SpaCy currently support? This is information we might need
# when building SpaCy-specific targets.
#
# Lists of languages would take up too much space in the autoformatted "one per
# line" standard. We group them here by the AEHLRU convention -- each of those
# letters is an initial letter that starts a new line. This convention allows
# for less scrolling without constantly reformatting when changing the lists.
SPACY_LANGUAGES = {
    'ca', 'da', 'de',
    'el', 'en', 'es', 'fr',
    'it', 'ja',
    'lt', 'mk', 'no', 'pl', 'pt',
    'ro', 'ru',
    'zh',
}


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
    }
}


def map_source_language(source, lcode):
    """
    Given a source name and a language code, return the equivalent language
    code used by that source.
    
    For example, `map_source_language("google", "zh-Hans")` returns "chi_sim"
    for some godforsaken reason.
    """
    if source in LANGUAGE_MAPS:
        return LANGUAGE_MAPS[source].get(lcode, lcode)
    else:
        return lcode


SOURCE_LANGUAGES = {
    # GlobalVoices (LREC 2012), from OPUS -- languages with over 500,000 tokens
    'globalvoices': [
        'ar', 'bn', 'ca', 'de',
        'en', 'es', 'fr',
        'it', 'ja',
        'mg', 'mk', 'nl', 'pl', 'pt',
        'ru', 'sw',
        'zh-Hans', 'zh-Hant', 'zh'
    ],

    # Google Ngrams 2012
    'google-ngrams': [
        'de',
        'en', 'es', 'fr',
        'he', 'it',
        'ru',
        'zh-Hans', 'zh', 
    ],

    # Jieba's built-in wordlist (supposedly MIT licensed?)
    'jieba': ['zh'],

    # NewsCrawl 2014, from the EMNLP Workshops on Statistical Machine Translation
    'newscrawl': ['cs', 'de', 'en', 'fi', 'fr', 'ru'],

    # OPUS's data files of OpenSubtitles 2018
    #
    # Include languages with at least 400 subtitle files, but skip:
    # - 'ze' because that's not a real language code
    #   (it seems to represent code-switching Chinese and English)
    # - 'th' because we don't know how to tokenize it
    'opensubtitles': [
        'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'da', 'de',
        'el', 'en', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'gl',
        'he', 'hr', 'hu', 'id', 'is', 'it', 'ja', 'ko',
        'lt', 'lv', 'mk', 'ml', 'ms', 'nl', 'nb', 'pl', 'pt-PT', 'pt-BR', 'pt',
        'ro', 'ru', 'si', 'sk', 'sl', 'sq', 'sr', 'sv', 'tr',
        'uk', 'vi', 'zh-Hans', 'zh-Hant', 'zh'
    ],

    'oscar': [
        'ar', 'az', 'be', 'bn', 'bg', 'bs', 'ca', 'cs', 'da', 'de',
        'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu',
        'he', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'ka', 'kk', 'ko', 
        'lt', 'lv', 'mk', 'ml', 'mn', 'mr', 'nl', 'no', 'pl', 'pt',
        'ro', 'sk', 'sl', 'sq', 'sr', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr',
        'uk', 'ur', 'vi', 'zh',

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
        'ar', 'bg', 'bs', 'ca', 'cs', 'cy', 'da', 'de',
        'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'gl',
        'he', 'hi', 'hu', 'hr', 'hy', 'id', 'it', 'ja', 'ka', 'ko',
        'la', 'lt', 'lv', 'ms', 'nn', 'nb', 'nl', 'pl', 'pt',
        'ro', 'ru', 'sk', 'sl', 'sv', 'sr', 'ta', 'th', 'tr',
        'uk', 'ur', 'uz', 'vi', 'zh',

        # Smaller but high-quality, high-depth Wikipedias
        'bn',
        'is', 'ku',
        'mk', 'my', 'ml', 'mn', 'mr', 'my',
        'or',
        'si', 'te',
    ],

}

COUNT_SOURCES = [
    'opensubtitles', 'wikipedia', 'google-ngrams', 'jieba', 'oscar'
]

FULL_TEXT_SOURCES = [
    'wikipedia', 'opensubtitles',
    'newscrawl', 'globalvoices'
]
MERGED_SOURCES = {
    'news': ['newscrawl', 'globalvoices'],
}

GOOGLE_NUM_1GRAM_SHARDS = {
    'en': 24,
    'zh-Hans': 1,
    'fr': 6,
    'de': 8,
    'he': 1,
    'it': 2,
    'ru': 2,
    'es': 3
}

# Google Books 2012 unigrams are sharded by the first letter or digit of the token,
# or 'other'.
GOOGLE_1GRAM_SHARDS = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'other',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]

# These are the shard names for Google Books data, which I'm interested in
# using as evidence about interesting phrases. I'm skipping numbers and 'other'
# for now; the remaining files are split by the two-letter prefix of the first
# token.
#
# Unfortunately, the 2-letter prefixes that never occur in any tokens in the
# vocabulary correspond to files that simply don't exist. In order to avoid
# errors, we need to exclude those prefixes: 'zq' from the 2grams, and four
# additional prefixes from 3grams.

GOOGLE_2GRAM_SHARDS = [
    _c1 + _c2
    for _c1 in 'abcdefghijklmnopqrstuvwxyz'
    for _c2 in 'abcdefghijklmnopqrstuvwxyz_'
    if _c1 + _c2 != 'zq'
]
GOOGLE_3GRAM_SHARDS = [
    _c1 + _c2
    for _c1 in 'abcdefghijklmnopqrstuvwxyz'
    for _c2 in 'abcdefghijklmnopqrstuvwxyz_'
    if _c1 + _c2 not in {'qg', 'qz', 'xg', 'xq', 'zq'}
]


LANGUAGE_SOURCES = defaultdict(list)
for _source in COUNT_SOURCES:
    for _lang in SOURCE_LANGUAGES[_source]:
        LANGUAGE_SOURCES[_lang].append(_source)

# Determine which languages we can support and which languages we can build a
# full-size list for. We want to have sources from 5 different registers of
# language to build a full list, but we give Dutch a pass -- it used to have 5
# sources before we took out Common Crawl and considered OpenSubtitles and
# SUBTLEX to count as the same source.

SUPPORTED_LANGUAGES = sorted([_lang for _lang in LANGUAGE_SOURCES if len(LANGUAGE_SOURCES[_lang]) >= 3])
LARGE_LANGUAGES = sorted([_lang for _lang in LANGUAGE_SOURCES if len(LANGUAGE_SOURCES[_lang]) >= 5 or _lang == 'nl'])



def language_count_sources(lang):
    """
    Get all the sources of word counts we have in a language.
    """
    return [
        DATA + "/counts/{source}/{lang}.txt".format(source=source, lang=lang)
        for source in LANGUAGE_SOURCES[lang]
    ]


def language_text_sources(lang):
    """
    Get all the sources of tokenized text we have in a language.
    """
    return [
        DATA + "/tokenized/{source}/{lang}.txt".format(source=source, lang=lang)
        for source in LANGUAGE_SOURCES[lang]
        if source in FULL_TEXT_SOURCES
    ]


def _count_filename(source, lang):
    if '/' in source:
        return DATA + "/counts/{source}.{lang}.txt".format(source=source,
                                                         lang=lang)
    else:
        return DATA + "/counts/{source}/{lang}.txt".format(source=source,
                                                       lang=lang)


def multisource_counts_to_merge(multisource, lang):
    """
    Given a multi-source name like 'news' and a language code, find which sources
    of counts should be merged to produce it.
    """
    result = [
        _count_filename(source, lang)
        for source in MERGED_SOURCES[multisource]
        if lang in SOURCE_LANGUAGES[source]
    ]
    return result


# Top-level rules
# ===============

rule wordfreq:
    input:
        expand(DATA + "/wordfreq/small_{lang}.msgpack.gz",
               lang=SUPPORTED_LANGUAGES),
        expand(DATA + "/wordfreq/large_{lang}.msgpack.gz",
               lang=LARGE_LANGUAGES),
        DATA + "/wordfreq/jieba_zh.txt"

rule frequencies:
    input:
        expand(DATA + "/freqs/{lang}.txt", lang=SUPPORTED_LANGUAGES)


# Downloaders
# ===========

rule download_google_1grams:
    resources:
        download=1
    output:
        DATA + "/downloaded/google/1grams-{lang}.txt"
    run:
        source_lang = GOOGLE_LANGUAGE_MAP.get(wildcards.lang, wildcards.lang)
        nshards = GOOGLE_NUM_1GRAM_SHARDS[wildcards.lang]
        for shard in range(nshards):
            url = f'http://storage.googleapis.com/books/ngrams/books/20200217/{source_lang}/1-{shard:>05}-of-{nshards:>05}.gz'
            shell("curl -Lf '{url}' | gunzip -c | awk -f scripts/google-sum-columns.awk >> {output}")


rule download_opensubtitles:
    output:
        DATA + "/downloaded/opensubtitles/{lang}.txt.gz"
    resources:
        download=1, opusdownload=1
    priority: 0
    run:
        source_lang = map_source_language('opensubtitles', wildcards.lang)
        shell("wget 'http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.{source_lang}.gz' -O {output}")


rule download_wikipedia:
    output:
        DATA + "/downloaded/wikipedia/wikipedia_{lang}.xml.bz2"
    resources:
        download=1, wpdownload=1
    priority: 0
    run:
        source_lang = map_source_language('wikipedia', wildcards.lang)
        version = WP_VERSION
        shell("wget 'https://dumps.wikimedia.org/{source_lang}wiki/{version}/{source_lang}wiki-{version}-pages-articles.xml.bz2' -O {output}")

rule download_newscrawl:
    output:
        DATA + "/downloaded/newscrawl-2014-monolingual.tar.gz"
    resources:
        download=1
    run:
        shell("wget 'http://www.statmt.org/wmt15/training-monolingual-news-2014.tgz' -O {output}")


def show_language_stats():
    import langcodes
    languages = set()
    for source_type in COUNT_SOURCES:
        for language in SOURCE_LANGUAGES[source_type]:
            languages.add(language)

    for language in sorted(languages):
        count = len(language_count_sources(language))
        if count >= 2:
            print("{}\t{}\t{}".format(
                language, 
                count,
                langcodes.get(language).display_name(),
            ))

show_language_stats()


# Extracting downloaded data
# ==========================


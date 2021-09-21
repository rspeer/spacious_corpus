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
# line" standard. We group them here by the AEHLPT convention -- each of those
# letters is an initial letter that starts a new line. This convention allows
# for less scrolling without constantly reformatting when changing the lists.


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
    # GlobalVoices (LREC 2012), from OPUS -- languages with over 100,000 sentences
    #
    # GlobalVoices is multilingual news with a more left activist perspective than
    # the usual news sources. (If you're worried about the effect of this, consider
    # the effect of the decades that we've been doing the opposite by training NLP
    # on the Wall Street Journal.)
    'globalvoices': [
        'ar', 'bn', 'ca', 'de',
        'el', 'en', 'es', 'fr',
        'it', 'ja',
        'mg',
        'pl', 'pt', 'ru', 'sw',
        'zh-Hans', 'zh-Hant',
    ],

    # Google Ngrams 2012
    'google-ngrams': [
        'de',
        'en', 'es', 'fr',
        'he', 'it',
        'ru',
        'zh-Hans', 
    ],

    # Jieba's built-in wordlist (supposedly MIT licensed?)
    'jieba': ['zh'],

    # NewsCrawl 2014, from the EMNLP Workshops on Statistical Machine Translation
    'newscrawl': ['cs', 'de', 'en', 'fi', 'fr', 'ru'],

    # OPUS's data files of OpenSubtitles 2018
    #
    # Include languages with at least 400 subtitle files, but skip 'ze', which is
    # not a real language code
    # (it seems to represent mixed Chinese and English in some form)
    'opensubtitles': [
        'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'da', 'de',
        'el', 'en', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'gl',
        'he', 'hr', 'hu', 'id', 'is', 'it', 'ja', 'ko',
        'lt', 'lv', 'mk', 'ml', 'ms', 'nl', 'nb',
        'pl', 'pt-PT', 'pt-BR', 'pt', 'ro', 'ru', 'si', 'sk', 'sl', 'sq', 'sr', 'sv',
        'th', 'tr', 'uk', 'vi', 'zh-Hans', 'zh-Hant',
        # TODO: merge pt-PT and pt-BR
    ],

    'oscar': [
        'ar', 'az', 'be', 'bn', 'bg', 'bs', 'ca', 'cs', 'da', 'de',
        'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu',
        'he', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'ka', 'kk', 'ko', 
        'lt', 'lv', 'mk', 'ml', 'mn', 'mr', 'nl', 'no',
        'pl', 'pt', 'ro', 'sk', 'sl', 'sq', 'sr', 'sv', 'sw',
        'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh',

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
        'la', 'lt', 'lv', 'ms', 'nn', 'nb', 'nl',
        'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'sr',
        'ta', 'th', 'tr', 'uk', 'ur', 'uz', 'vi', 'zh',

        # Smaller but high-quality, high-depth Wikipedias
        'bn',
        'is', 'ku',
        'mk', 'my', 'ml', 'mn', 'mr', 'my',
        'or',
        'si',
        'te',
    ],
}

SAMPLED_REDDIT_SHARDS = [
    '2009-02',
    '2011-03',
    '2013-04',
    '2015-05',
    '2017-06',
    '2019-07',
]

COUNT_SOURCES = [
    'opensubtitles', 'wikipedia', 'news', 'google-ngrams', 'jieba', 'oscar',
]

FULL_TEXT_SOURCES = [
    'wikipedia', 'opensubtitles', 'newscrawl', 'globalvoices',
]
MERGED_SOURCES = {
    'news': ['newscrawl', 'globalvoices'],
}


# Add merged sources like 'news' to the source list
for merged in MERGED_SOURCES:
    source_set = set()
    for source in MERGED_SOURCES[merged]:
        source_set |= set(SOURCE_LANGUAGES[source])
    SOURCE_LANGUAGES[merged] = sorted(source_set)



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


def plain_text_input(source, lang):
    """
    Define which file or files contain compressed plain text, for the given
    source and the given language.
    """
    if source == 'globalvoices':
        return [f"{DATA}/downloaded/{source}/{lang}.txt.gz"]
    elif source == 'news':
        inputs = []
        if lang in SOURCE_LANGUAGES['newscrawl']:
            inputs.append(f"{DATA}/extracted/newscrawl/{lang}.txt.br")
        if lang in SOURCE_LANGUAGES['globalvoices']:
            inputs.append(f"{DATA}/downloaded/globalvoices/{lang}.txt.gz")
        assert inputs, f"No news sources found for {lang}"
    else:
        return [f"{DATA}/extracted/{source}/{lang}.txt.br"]


def counts_input(source, lang):
    return f"{DATA}/counts/{source}/{lang}.txt"


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
# This stage is mostly about locating resources on external sites, and downloading them
# in their original format.
#
# There is no downloader for OSCAR, because HuggingFace abstracts over the format and
# provides a streaming interface to it.


# The original format of Google Ngrams is messy and unhelpful, so as we download it,
# we process it with an awk script to convert it to a more useful form.
rule download_google_1grams:
    resources:
        download=1
    output:
        DATA + "/downloaded/google-ngrams/1grams-{lang}.txt"
    run:
        source_lang = map_source_language('google-ngrams', wildcards.lang)
        nshards = GOOGLE_NUM_1GRAM_SHARDS[wildcards.lang]
        
        # Make sure we're not appending to an existing file
        shell("rm -f {output}")
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


rule download_globalvoices:
    output:
        DATA + "/downloaded/globalvoices/{lang}.txt.gz"
    resources:
        download=1, opusdownload=1
    priority: 0
    run:
        source_lang = map_source_language('globalvoices', wildcards.lang)
        shell("wget 'http://opus.nlpl.eu/download.php?f=GlobalVoices/v2018q4/mono/{source_lang}.txt.gz' -O {output}")


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
    shell:
        "wget 'http://www.statmt.org/wmt15/training-monolingual-news-2014.tgz' -O {output}"


# For possible future use: an enormous book corpus maintained by Shawn Presser.
# Apparently this emulates a book corpus that LLMs are trained on. I don't know
# yet if we want to use it.
rule download_books3:
    output:
        DATA + "/downloaded/books3/books3.tar.gz"
    resources:
        download=1
    shell:
        "wget 'https://the-eye.eu/public/AI/pile_preliminary_components/books3.tar.gz' -O {output}"


# Extracting downloaded data
# ==========================
#
# In this stage, our goal is to produce individual files of compressed plain
# text from each resource.
#
# If a resource is already in the form of .txt.gz files that need no
# preprocessing, we use it as is. Otherwise, we preprocess the resource to
# produce .txt.br files. (All else being equal, we use brotli compression,
# which is very fast and effective at compressing plain text.)

rule extract_wikipedia:
    input:
        DATA + "/downloaded/wikipedia/wikipedia_{lang}.xml.bz2"
    output:
        DATA + "/extracted/wikipedia/{lang}.txt.br"
    shell:
        # uses the 'wiki2text' command from rspeer's wikiparsec
        "bunzip2 -c {input} | wiki2text | brotli -c > {output}"


def inputs_for_extract_opensubtitles(wildcards):
    lang = wildcards.lang
    if lang == 'pt':
        return [
            f"{DATA}/downloaded/opensubtitles/pt-BR.txt.gz",
            f"{DATA}/downloaded/opensubtitles/pt-PT.txt.gz",
        ]
    else:
        return [f"{DATA}/downloaded/opensubtitles/{lang}.txt.gz"]


rule extract_opensubtitles:
    input:
        inputs_for_extract_opensubtitles
    output:
        DATA + "/extracted/opensubtitles/{lang}.txt.br"
    shell:
        # minimal pre-processing: remove lines that start and end with parentheses,
        # as those are usually filler subtitles like (Music).
        # Replace acute accents over nothing with apostrophes.
        """zcat {input} | egrep -v '^[(].*[)]$' | sed "s/´/'/g" | brotli -c > {output}"""


rule extract_newscrawl:
    input:
        DATA + "/downloaded/newscrawl-2014-monolingual.tar.gz"
    output:
        expand(
            temp(DATA + "/extracted/newscrawl/{lang}.txt.br"),
            lang=SOURCE_LANGUAGES['newscrawl']
        )
    run:
        ex_dir = f"{DATA}/extracted/newscrawl/training-monolingual-news-2014/"
        shell("tar xf {input} -C {DATA}/extracted/newscrawl")

        # Re-compress each file individually, using brotli
        for lang in SOURCE_LANGUAGES['newscrawl']:
            shell(
                "brotli -c {ex_dir}/news.2014.{lang}.shuffled > "
                "{DATA}/extracted/newscrawl/{lang}.txt.br && "
                "rm {ex_dir}/news.2014.{lang}.shuffled"
            )


rule concatenate_news:
    input:
        inputs_for_news
        DATA + "/extracted/newscrawl/{lang}.txt.br",
        DATA + "/downloaded/globalvoices/{lang}.txt.gz"
    output:
        DATA + "/extracted/news/{lang}.txt.br"
    run:
        newscrawl, globalvoices = input
        tmp_output = f"{DATA}/extracted/news/{wildcards.lang}.txt"
        shell("rm -f {output}")
        shell("brotli -dc {newscrawl} >> {tmp_output}")
        shell("gunzip -c {globalvoices} >> {tmp_output}")
        shell("brotli {tmp_output}")


rule extract_reddit:
    output:
        DATA + "/mixed-languages/reddit/"


# Diagnostics
# ===========

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

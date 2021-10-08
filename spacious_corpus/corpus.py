from .run import build_targets
from .storage import DocZip

import spacy
from spacy.util import registry
from spacy.tokens import Doc
from spacy.language import Language

from .corpus_info import match_source_language, SOURCE_LANGUAGES

import itertools
from typing import Callable, Iterable, Iterator, Optional, Union
from pathlib import Path


def tokenized_corpus_filename(source, lang):
    matched_lang = match_source_language(source, lang)
    if matched_lang is None:
        supported = SOURCE_LANGUAGES[source]
        raise ValueError(
            f"In spacious_corpus, the corpus '{source}' does not support "
            f"the language '{lang}'. Available languages are:\n{supported}"
        )

    return f"data/tokens/{source}/{matched_lang}.zip"


@registry.readers("spacious_corpus.SpaciousCorpus.v1")
def corpus_reader(
    corpus_name: str,
    lang: str,
    workdir: Union[Path, str],
    start_at: Optional[int] = None,
    limit: Optional[int] = None
) -> Callable[[Language], Iterable[Doc]]:
    """
    Run the Snakemake build to acquire a corpus if necessary, then iterate
    over its documents.

    The corpus will be looked up in the Snakemake working directory `workdir`,
    or built in that directory if necessary.
    """
    workdir = Path(workdir)

    # Look up the language code of the nlp object, and reuse it to
    # choose a filename corresponding to the correct language within
    # a multilingual source.
    corpus_subpath = tokenized_corpus_filename(corpus_name, lang)
    build_targets([corpus_subpath], str(workdir))

    absolute_corpus_path = workdir / corpus_subpath
    def corpus_iterator(nlp: Language) -> Iterator[Doc]:
        corpus = DocZip.open(absolute_corpus_path, nlp.lang)
        if limit is not None:
            if start_at is not None:
                corpus = itertools.islice(corpus, start_at, start_at + limit)
            else:
                corpus = itertools.islice(corpus, limit)
        return corpus
    
    return corpus_iterator


def iterate_corpus(
    corpus_name: str,
    lang: str,
    workdir: Union[Path, str],
    start_at: Optional[int] = None,
    limit: Optional[int] = None
) -> Iterator[Doc]:
    """
    Provides a way to access the documents of a particular corpus from outside
    of a spaCy pipeline. Returns an iterator of Doc objects.
    """
    nlp = spacy.blank(lang)
    reader = corpus_reader(corpus_name, lang, workdir, start_at, limit)
    return reader(nlp)

from .run import build_targets
from .storage import DocZip

from spacy.util import registry
from spacy.tokens import Doc
from spacy.language import Language

import itertools
from typing import Callable, Iterable, Iterator, Optional, Union
from pathlib import Path


@registry.readers("spacious_corpus.SpaciousCorpus.v1")
def corpus_reader(
    corpus_name: str,
    workdir: Union[Path, str],
    limit: Optional[int] = None,
) -> Callable[[Language], Iterable[Doc]]:
    """
    Run the Snakemake build to acquire a corpus if necessary, then iterate
    over its documents.

    The corpus will be looked up in the Snakemake working directory `workdir`,
    or built in that directory if necessary.
    """
    workdir = Path(workdir)

    def corpus_iterator(nlp: Language) -> Iterator[Doc]:
        # TODO: align languages or allow language codes to be overridden
        lang = nlp.lang

        corpus_subpath = f"data/tokens/{corpus_name}/{lang}.zip"
        build_targets([corpus_subpath], str(workdir))

        absolute_corpus_path = workdir / corpus_subpath
        corpus = DocZip.open(absolute_corpus_path, lang)
        if limit is not None:
            corpus = itertools.islice(corpus, limit)

        return corpus
    
    return corpus_iterator

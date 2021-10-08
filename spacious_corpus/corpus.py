from .run import build_targets
from .storage import DocZip

from spacy.util import registry
from spacy.tokens import Doc
from spacy.language import Language

import itertools
from typing import Callable, Iterable, Iterator, Optional, Union
from pathlib import Path


@registry.readers("spacious_corpus.SpaciousCorpus.v1")
def acquire_corpus(
    corpus_subpath: str,
    lang: str,
    limit: Optional[int],
    workdir: Union[Path, str],
) -> Callable[[Language], Iterable[Doc]]:
    
    workdir = Path(workdir)
    build_targets([corpus_subpath], str(workdir))

    def corpus_iterator(nlp: Language) -> Iterator[Doc]:
        absolute_corpus_path = workdir / corpus_subpath
        corpus = DocZip.open(absolute_corpus_path, lang)
        if limit is not None:
            corpus = itertools.islice(corpus, limit)

        return corpus
    
    return corpus_iterator

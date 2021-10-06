"""
This module provides the DocZip class, for reading and writing large numbers
of tokenized documents in spaCy form.
"""
from spacy.tokens import DocBin, Doc

import itertools
from zipfile import ZipFile
import tempfile
from pathlib import Path
from typing import Iterable, Iterator, Union, List
from .nlp import make_nlp_stack

PathLike = Union[Path, str]


class DocZip:
    """
    Implements a format for accessing tokenized documents in a corpus.

    Doc objects can be read from and written to a DocZip. A DocZip is
    implemented as a .zip file containing .spacy files, with sequential
    names such as `en_000.spacy`, `en_001.spacy`, etc.

    Each .spacy file contains up to a specified number of documents, 1
    million by default. This number should be decreased if the documents
    are long, because the documents in each chunk are read into memory
    all at once.

    (The leading zeros make it easier to list the parts in sorted order,
    as long as there are 1000 or fewer chunks, but it's okay for there
    to be more than 1000.)
    """

    def __init__(self, path: PathLike, lang: str):
        self.lang = lang

        # Does self.nlp need to be configurable to support different vocabs?
        # Should we serialize the vocab in the file as well?
        self.nlp = make_nlp_stack(lang)
        self.path = path

    @staticmethod
    def open(path: PathLike, lang: str) -> "DocZip":
        """
        DocZip.open is conceptually parallel to file.open, though at the moment
        it just calls the constructor.

        There's no need to close a DocZip, because the actual file is only open
        for reading or writing inside of methods when it needs to be.
        """
        return DocZip(path, lang)

    def iterate_chunk(self, chunkname: str) -> Iterator[Doc]:
        """
        Iterate the documents from one chunk, specified by its filename
        within the .zip.
        """
        doc_bin = DocBin(attrs=[])
        with ZipFile(self.path, mode="r") as zip_file:
            part_bytes = zip_file.read(chunkname)
            doc_bin.from_bytes(part_bytes)
        yield from doc_bin.get_docs(self.nlp.vocab)

    def get_chunks(self) -> List[str]:
        """
        Get the names of all the chunks, which can be passed to
        .iterate_chunk().
        """
        with ZipFile(self.path, mode="r") as zip_file:
            return zip_file.namelist()

    def iterate(self) -> Iterator[Doc]:
        """
        Iterate all documents from all chunks, in order.
        """
        for chunkname in self.get_chunks():
            yield from self.iterate_chunk(chunkname)

    def __iter__(self) -> Iterator[Doc]:
        return self.iterate()

    def write_stream(self, stream: Iterable[str], chunk_size: int = 1_000_000):
        """
        Take in a stream of document texts, tokenize them, and store them
        in the DocZip.
        """

        def chunker(item):
            return item[0] // chunk_size

        with ZipFile(self.path, mode="w") as zip_file:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                line_enumerator = enumerate(stream)
                for (chunk_num, group) in itertools.groupby(line_enumerator, chunker):
                    doc_bin = DocBin(attrs=[])
                    for _num, text in group:
                        doc = self.nlp(text)
                        doc_bin.add(doc)

                    filename = f"{self.lang}_{chunk_num:>03d}.spacy"
                    temp_file: Path = temp_path / f"{self.lang}_{chunk_num:>03d}.spacy"
                    doc_bin.to_disk(temp_file)
                    zip_file.write(temp_file, arcname=filename)

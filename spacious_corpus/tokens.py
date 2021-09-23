import spacy
from ftfy import fix_text
from pathlib import Path
from ftfy.fixes import unescape_html, fix_surrogates
import itertools
import sys
import typer
import zipfile
import tempfile

from spacy.tokens import DocBin


def tokenize_stream(lang, stream, output_file, chunk_size=100000, use_ftfy=True):
    def chunker(item):
        return item[0] // chunk_size

    nlp = spacy.blank(lang)
    with zipfile.ZipFile(output_file, mode='w') as zip_file:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            line_enumerator = enumerate(stream)
            for (chunk_num, group) in itertools.groupby(line_enumerator, chunker):
                doc_bin = DocBin(attrs=[])
                for _num, line in group:
                    line = line.strip()
                    if line:
                        if use_ftfy:
                            # Run all ftfy fixes, but don't let it introduce line breaks
                            line = fix_text(line.rstrip()).replace('\n', ' ')
                        else:
                            # Run only specific quick fixes from ftfy
                            line = fix_surrogates(unescape_html(line.rstrip())).replace('\n', ' ')
                        doc = nlp(line)
                        doc_bin.add(doc)

                filename = f"{lang}_{chunk_num:>03d}.spacy"
                temp_file: Path = temp_path / f"{lang}_{chunk_num:>03d}.spacy"
                doc_bin.to_disk(temp_file)
                zip_file.write(temp_file, arcname=filename)


def tokenize_stdin(lang, output_file, chunk_size=100000, use_ftfy=True):
    tokenize_stream(lang, sys.stdin, output_file, chunk_size=chunk_size, use_ftfy=use_ftfy)


def iterate_docs(dirname, lang):
    nlp = spacy.blank(lang)
    path = Path(dirname)
    for filename in path.iterdir():
        doc_bin = DocBin(attrs=[])
        doc_bin.from_disk(filename)
        yield from doc_bin.get_docs(nlp.vocab)


def main():
    typer.run(tokenize_stdin)


if __name__ == '__main__':
    main()

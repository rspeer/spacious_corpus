import spacy
from ftfy import fix_text
from pathlib import Path
from ftfy.fixes import unescape_html, fix_surrogates
import langcodes
import gzip
import itertools
import sys
import typer

from spacy.tokens import DocBin


def tokenize_stdin(lang, output_dir, chunk_size=100000, use_ftfy=True):
    def chunker(item):
        return item[0] // chunk_size

    path = Path(output_dir)
    path.mkdir(exist_ok=True)
    nlp = spacy.blank(lang)
    line_enumerator = enumerate(sys.stdin)
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

        filename = path / f"part_{chunk_num:<03d}.spacy"
        doc_bin.to_disk(filename)


if __name__ == '__main__':
    typer.run(tokenize_stdin)

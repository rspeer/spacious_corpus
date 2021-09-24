from ftfy import fix_text
from ftfy.fixes import unescape_html, fix_surrogates
import sys
import typer

from .storage import DocZip


MAX_LINE_LENGTH = 1_000_000


def tokenize_stream(lang, stream, output_file, chunk_size=1_000_000, use_ftfy=True):
    def processed_stream():
        for line in stream:
            line = line.strip()
            if line and len(line) < MAX_LINE_LENGTH:
                if use_ftfy:
                    line = fix_text(line.rstrip()).replace('\n', ' ')
                else:
                    # Run only specific quick fixes from ftfy
                    line = fix_surrogates(unescape_html(line.rstrip())).replace('\n', ' ')
                yield line

    doc_zip = DocZip.open(output_file, lang)
    doc_zip.write_stream(processed_stream(), chunk_size=chunk_size)


def tokenize_stdin(lang, output_file, chunk_size=1_000_000, use_ftfy=True):
    tokenize_stream(lang, sys.stdin, output_file, chunk_size=chunk_size, use_ftfy=use_ftfy)


def main():
    typer.run(tokenize_stdin)


if __name__ == '__main__':
    main()

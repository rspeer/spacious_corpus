from ftfy import fix_text
from ftfy.fixes import unescape_html, fix_surrogates
import re
import sys
import typer

from .storage import DocZip
from .nlp import normalize_text

MAX_LINE_LENGTH = 1_000_000


DIGIT_RE = re.compile(r"\d")
MULTI_DIGIT_RE = re.compile(r"\d[\d.,]+")


def _sub_numbers(match):
    """
    Given a regex match, return what it matched with digits replaced by
    #.
    """
    return DIGIT_RE.sub("#", match.group(0))


def smash_numbers(text):
    """
    If a token contains multiple consecutive digits (possibly with a decimal
    point or comma), replace the digits with the # symbol to get a generalized
    shape for the number.

    Prefix the result with 'NUM:' if it was changed, to incidate that it's
    a special token and not the literal text of the token. 'NUM:' will not
    appear in other tokens that we count, because we casefold them.

    >>> smash_numbers("r2d2")
    'r2d2'
    >>> smash_numbers("v3.2")
    'NUM:v#.#'
    >>> smash_numbers("24,601")
    'NUM:##,###'
    """
    replaced = MULTI_DIGIT_RE.sub(_sub_numbers, text)
    if replaced != text:
        return f"NUM:{replaced}"
    else:
        return text


def normalize_token(text: str, lang: str):
    """
    Apply all text normalizations, and replace multi-digit numbers with a
    representation of their shape (as in `smash_numbers`).
    """
    return smash_numbers(normalize_text(text, lang))


def tokenize_stream(lang, stream, output_file, chunk_size=1_000_000, use_ftfy=True):
    def processed_stream():
        for line in stream:
            line = line.strip()
            if line and len(line) < MAX_LINE_LENGTH:
                if use_ftfy:
                    line = fix_text(line.rstrip()).replace("\n", " ")
                else:
                    # Run only specific quick fixes from ftfy
                    line = fix_surrogates(unescape_html(line.rstrip())).replace(
                        "\n", " "
                    )
                yield line

    doc_zip = DocZip.open(output_file, lang)
    doc_zip.write_stream(processed_stream(), chunk_size=chunk_size)


def tokenize_stdin(lang, output_file, chunk_size=1_000_000, use_ftfy=True):
    tokenize_stream(
        lang, sys.stdin, output_file, chunk_size=chunk_size, use_ftfy=use_ftfy
    )


def main():
    typer.run(tokenize_stdin)


if __name__ == "__main__":
    main()

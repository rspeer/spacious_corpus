from collections import Counter
from .storage import DocZip
from .tokens import normalize_token
import spacy
import typer


def count_tokens(lang: str, in_filename: str, out_filename: str):
    """
    Take in a file containing a DocZip of tokenized documents, count its tokens,
    and write the ones with a count of at least 2 to a tabular text file.
    """
    doc_store = DocZip.open(in_filename, lang)
    counts = Counter()
    total = 0
    for doc in doc_store:
        toks = [normalize_token(tok.text, lang) for tok in doc]
        toks = [tok for tok in toks if tok != ""]
        counts.update(toks)
        total += len(toks)

    # adjusted_counts drops the items that only occurred once
    one_each = Counter(counts.keys())
    adjusted_counts = counts - one_each

    # Write the counted tokens to outfile
    with open(out_filename, "w", encoding="utf-8") as outfile:
        print("__total__\t{}".format(total), file=outfile)
        for token, adjcount in adjusted_counts.most_common():
            print("{}\t{}".format(token, adjcount + 1), file=outfile)


def count_main():
    typer.run(count_tokens)


def recount_messy(lang: str, in_filename: str, out_filename: str):
    """
    Take in a file of counts from another source (such as Google Books), and
    make it consistent with our tokenization and format.
    """
    counts = Counter()
    total = 0
    nlp = spacy.blank(lang)
    for line in open(in_filename, encoding="utf-8"):
        line = line.rstrip()
        if line and not line.startswith("__total__"):
            text, strcount = line.split("\t", 1)
            count = int(strcount)
            toks = [normalize_token(tok.text, lang) for tok in nlp(text)]
            toks = [tok for tok in toks if tok != ""]
            for tok in toks:
                counts[tok] += count
                total += count

    # Write the counted tokens to output
    with open(out_filename, "w", encoding="utf-8") as outfile:
        print("__total__\t{}".format(total), file=outfile)
        for token, count in counts.most_common():
            print("{}\t{}".format(token, count), file=outfile)


def recount_main():
    typer.run(recount_messy)

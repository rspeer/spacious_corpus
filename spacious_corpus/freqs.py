from collections import defaultdict
from typing import List, Dict
from operator import itemgetter
import statistics
import typer


def counts_to_freqs(infile: str) -> Dict[str, float]:
    """
    Convert a file containing word counts and a __total__ line to a list of decimal
    frequencies, by dividing each count by the __total__.
    """
    total = None
    freqs = {}
    for line in infile:
        word, strcount = line.rstrip().split('\t', 1)
        count = int(strcount)
        if word == '__total__':
            total = count
        else:
            freq = count / total
            freqs[word] = freq
    return freqs


def merge_freqs(freq_dicts):
    """
    Merge multiple dictionaries of frequencies, representing each word with
    the 'figure skating average' of the word's frequency over all sources,
    meaning that we drop the highest and lowest values and average the rest.
    """
    vocab = set()
    for freq_dict in freq_dicts:
        vocab.update(freq_dict)

    merged = defaultdict(float)
    N = len(freq_dicts)
    if N < 3:
        raise ValueError(
            "Merging frequencies requires at least 3 frequency lists."
        )
    for term in vocab:
        freqs = []
        for freq_dict in freq_dicts:
            freq = freq_dict.get(term, 0.)
            freqs.append(freq)

        if freqs:
            freqs.sort()
            inliers = freqs[1:-1]
            mean = statistics.mean(inliers)
            if mean > 0.:
                merged[term] = mean

    total = sum(merged.values())

    # Normalize the merged values so that they add up to 0.99 (based on
    # a rough estimate that 1% of tokens will be out-of-vocabulary in a
    # wordlist of this size).
    for term in merged:
        merged[term] = merged[term] / total * 0.99
    return merged


def _write_frequency_file(freq_dict, outfile):
    freq_items = sorted(freq_dict.items(), key=itemgetter(1, 0), reverse=True)
    for word, freq in freq_items:
        if freq < 1e-9:
            break
        print('{}\t{:.5g}'.format(word, freq), file=outfile)


def merge_counts_to_freqs(
    lang: str,
    inputs: List[str],
    output: str
):
    freq_dicts = [counts_to_freqs(infile) for infile in inputs]
    merged = merge_freqs(freq_dicts)
    with open(output, 'w', encoding='utf-8') as outfile:
        _write_frequency_file(merged, outfile)


def merge_main():
    typer.run(merge_counts_to_freqs)

# spacious_corpus

A build process for collecting plain-text corpus data in various languages.

This code is built on [Snakemake][]. Snakemake is a general-purpose build tool
that's centered around building data instead of compiling code. It supports
rules that have multiple inputs and multiple outputs, and the inputs and outputs
can be determined by pattern matches and variable expansions. This kind of thing
is necessary when we have a variety of sources, with different shapes to their
data, in a number of different languages.

[snakemake]: https://snakemake.readthedocs.io/en/stable/

This process originates from [exquisite-corpus][], but here we focus on data
sources and formats we want to use with SpaCy, and eliminate much of its
accumulated complexity.

[exquisite-corpus]: https://github.com/LuminosoInsight/exquisite-corpus


## Setup and dependencies

Run `pip install -e .` to install `spacious_corpus` as a package. The Python
dependencies of this code appear in `setup.cfg`, and will be installed as a
result of this command.

Another dependency is on [wikiparsec][], Elia's toolkit for parsing WikiText,
which is written in Haskell. Follow its instructions to build and install it.

[wikiparsec]: https://github.com/rspeer/wikiparsec

You also need command line tools such as `wget`, `curl`, and `bunzip2`.

Make sure that you have enough hard disk space available. All of the downloaded
and built data will go into the `data/` subdirectory, so if you need to, you can
make this a symbolic link to a separate disk.

## Running a build

The Snakefile describes how various data is built. The script `./make.sh`
invokes Snakemake with appropriate options so that it schedules up to 8
processes in parallel, and (for example) makes sure not to get booted from
Wikimedia's download server by downloading too many of their files at the same
time.

You can give an individual file (or multiple files) as the target of `make.sh`,
and Snakemake will figure out how to build it from all of its dependencies. The
end of the Snakefile provides some top-level rules that don't correspond to
files:

* `./make.sh freqs`
  
  Collect various sources of unigram word frequencies, and combine them into
  a word frequency list -- an estimate of the unigram probability of each
  lexeme in the language as a whole.

* `./make.sh wikipedia`

  Download and tokenize Wikipedia in many languages.

* `./make.sh opensubtitles`

  Download and tokenize OpenSubtitles in many languages, removing parenthesized
  text from the start of each subtitle.

* `./make.sh oscar`

  Download and tokenize the first 1,000,000 lines of the OSCAR web-crawled
  corpus in many languages.

You should expect these builds to take at least a day to run to completion.

## Output formats

### Frequencies

Frequencies appear in `data/freqs/{lang}.txt`, as tab-separated lexemes and
frequencies. The frequencies are scaled to add up to 0.99 (taking a rough guess
that out-of-vocabulary words are 1% of the total).

Here are the first several lines of `data/freqs/en.txt`:

```
the     0.055551
,       0.050059
.       0.043191
of      0.026978
and     0.024423
to      0.023004
in      0.019477
```

These lexemes come from text in a normal form specified in `spacious_corpus.nlp`:

- Text is NFC or NFKC normalized, depending on the language
- Multi-script languages (such as Serbian) are transliterated into Latin letters
- Text is case-folded to lowercase
- In languages that use dotted vs. dotless I (like Turkish), the case-folding is
  aware of the different mapping of letters
- Vowel marks are removed, in languages where they are optional and uncommon

When tokenizing and counting tokens, we apply more changes:

- Multi-digit numbers are collapsed into one lexeme representing the shape of
  the digits: for example, `24,601` becomes `NUM:##,###`
- Whitespace is stripped from the edges of the tokens
- Tokens made only of whitespace are removed

### Tokens

Tokenized text is stored in .zip files of .spacy binary files. These files are
read and written with the `spacious_corpus.storage.DocZip` class.
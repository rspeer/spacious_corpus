#!/bin/sh
# Run Snakemake with appropriate download limits (so we don't get limited from downloading
# Wikipedia, for example)
snakemake $@ -j 8 --snakefile spacious_corpus/config/Snakefile --resources wpdownload=2 --resources opusdownload=4

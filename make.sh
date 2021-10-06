#!/bin/sh
# Run Snakemake with appropriate download limits (so we don't get limited from downloading
# Wikipedia, for example)
snakemake $@ -j 8 --resources wpdownload=2 --resources opusdownload=4

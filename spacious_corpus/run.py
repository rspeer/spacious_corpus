"""
Provides a CLI for building a particular target (or list of targets) in
spacious_corpus, and a function that can be reused in `corpus.py` to
ensure a particular corpus is built and then iterate over it.
"""
import snakemake
import typer
from .util import snakemake_filename

from typing import List

# Limits on how many simulataneous files we can download from various sources
RESOURCES = {
    'opusdownload': 4,
    'wpdownload': 2,
}


def build_targets(targets: List[str], workdir: str):
    """
    Build the requested list of targets, given as relative paths starting with
    'data/', with `workdir` as the working directory.

    `workdir` should point to a directory on a large disk. Reusing the same
    workdir allows reusing previously downloaded and built resources.
    """
    snakemake.snakemake(
        snakemake_filename(),
        targets=targets,
        workdir=workdir,
        cores=8,
        resources=RESOURCES
    )


def build_main():
    typer.run(build_targets)

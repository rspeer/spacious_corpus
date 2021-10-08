import snakemake
import typer
from .util import snakemake_filename

from pathlib import Path
from typing import List, Union

# Limits on how many simulataneous files we can download from various sources
RESOURCES = {
    'opusdownload': 4,
    'wpdownload': 2,
}


def build_targets(targets: List[str], workdir: str):
    snakemake.snakemake(
        snakemake_filename(),
        targets=targets,
        workdir=workdir,
        cores=8,
        resources=RESOURCES
    )


def build_main():
    typer.run(build_targets)

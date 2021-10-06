import datasets
import itertools
import pathlib
import typer
from tqdm import tqdm
from typing import Optional

from .tokens import tokenize_stream


def stream_oscar(lang, num_lines, cache_path, progress=True):
    dataset = datasets.load_dataset(
        "oscar",
        f"unshuffled_deduplicated_{lang}",
        split="train",
        streaming=True,
        cache_dir=cache_path,
    )
    iterator = itertools.islice(dataset, num_lines)
    if progress:
        iterator = tqdm(iterator, total=num_lines)
        iterator.set_description(f"oscar.{lang}")
    for item in iterator:
        yield item["text"]


def tokenize_oscar(
    lang: str,
    output_file: str,
    cache_dir: Optional[str] = typer.Option(
        None, help="Directory to download OSCAR data into"
    ),
    chunk_size: int = 100_000,
    num_lines: int = 1_000_000,
):
    cache_path = pathlib.Path(cache_dir)
    cache_path.mkdir(exist_ok=True)
    stream = stream_oscar(lang, num_lines, cache_path)
    tokenize_stream(lang, stream, output_file, chunk_size=chunk_size, use_ftfy=True)


def main():
    typer.run(tokenize_oscar)


if __name__ == "__main__":
    main()

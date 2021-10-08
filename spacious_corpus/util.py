from pkg_resources import resource_filename

CONFIG_ROOT = resource_filename('spacious_corpus', 'config')
import os


def config_filename(filename):
    return os.path.join(CONFIG_ROOT, filename)


def snakemake_filename():
    return config_filename('Snakefile')

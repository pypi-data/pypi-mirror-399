"""
Entry point for running automl as a module.

Usage:
    python -m automl run data.csv
    python -m automl --help
"""

from .cli import cli

if __name__ == '__main__':
    cli()

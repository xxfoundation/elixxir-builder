"""
main.py - main functionality for xxbuilder tool
"""

import click
import sys

@click.command(help='XX Network Builder')
@click.option('--output', '-o', type=click.File('wb'), default=sys.stdout,
              help='Optional output file')
def cli(output, seed, count):
    print("Hello, world!\n", file=output)

if __name__ == '__main__':
    cli()

"""gdpr-article-9-toolkit CLI entry point."""

import click

from src import __version__


@click.command()
@click.version_option(version=__version__, prog_name="gdpr-article-9-toolkit")
def cli() -> None:
    """Check UK GDPR Article 9 processing conditions for special category data."""
    click.echo("gdpr-article-9-toolkit")


if __name__ == "__main__":
    cli()

"""Main entry point for haniwers v2 CLI."""

import typer

from haniwers import v2

app = typer.Typer(help="Haniwers v2 - Next-generation cosmic ray detection analysis")


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo(f"haniwers {v2.__version__}")


@app.command()
def measure() -> None:
    """[placeholder] Measurement with kazunoko"""
    pass


@app.command()
def convert() -> None:
    """[placeholder] Conversion with datemaki"""
    pass


if __name__ == "__main__":
    app()

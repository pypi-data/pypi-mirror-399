"""Console script for TRITON_SWMM_benchmarking."""

import typer
from rich.console import Console

from TRITON_SWMM_benchmarking import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for TRITON_SWMM_benchmarking."""
    console.print("Replace this message by putting your code into "
               "TRITON_SWMM_benchmarking.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()

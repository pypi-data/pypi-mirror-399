import sys
from pathlib import Path

import click
import numpy as np

from linear_regression.linear_regression_python_bindings import do_linear_regression  # ty: ignore[unresolved-import]


@click.command()
@click.option(
    "--input-tsv",
    required=True,
    help="A headerless TSV file with two columns. Each row defines an observation (x, y).",
    type=click.Path(exists=True, path_type=Path, file_okay=True, dir_okay=False),
)
@click.option(
    "--output-tsv",
    required=True,
    help="A TSV file with informative row labels.",
    type=click.Path(path_type=Path, file_okay=True, dir_okay=False),
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="If False and outout-tsv exists, the program errors out. If True, the output is overwritten.",
)
def linear_regression(input_tsv: Path, output_tsv: Path, overwrite: bool) -> None:
    """
    - Read a TSV file with at least one row and two columns (i.e., (x, y) in each row)
    - Using the rust library to do the analysis
    - Write the results to a TSV file with informative row labels
    """
    input_data = np.loadtxt(input_tsv, delimiter="\t")
    if input_data.shape[0] < 1:
        _error_and_exit("There must at least one row of data.")
    if input_data.shape[1] != 2:
        _error_and_exit("There must be two columns of data.")
    if np.any(~np.isfinite(input_data)):
        _error_and_exit("All the input data must be finite (non-NA and non-infinite).")

    if (overwrite is False) and (output_tsv.is_file()):
        _error_and_exit(f"The output file {output_tsv} already exists.")

    click.echo(f"Input file: {input_tsv.name}")
    click.echo(f"Output file: {output_tsv.name}")
    click.echo(f"Read {input_data.shape[0]} data points")

    input_data = input_data.ravel()
    input_data = input_data.astype(np.float64)
    output = do_linear_regression(input_data)
    with open(output_tsv, "w") as f:
        for n, v in output:
            f.write(f"{n}\t{v}\n")

    click.echo("Done")


def _error_and_exit(message: str) -> None:
    click.echo(message, err=True)
    sys.exit(1)


if __name__ == "__main__":
    linear_regression()

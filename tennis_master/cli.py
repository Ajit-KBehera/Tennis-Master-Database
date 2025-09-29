import os
import sys
from pathlib import Path

import click

from .pipeline.build import build_all


@click.group()
def cli():
	"""Tennis Master data integration CLI."""
	pass


@cli.command()
@click.option("--data-root", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True)
@click.option("--out-dir", type=click.Path(file_okay=False, path_type=Path), required=True)
def build(data_root: Path, out_dir: Path):
	"""Build manifests, dimensions, and master outputs."""
	out_dir.mkdir(parents=True, exist_ok=True)
	build_all(data_root=data_root, out_dir=out_dir)
	click.echo(f"Build complete. Outputs in {out_dir}")


if __name__ == "__main__":
	cli()



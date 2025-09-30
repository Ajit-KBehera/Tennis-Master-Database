import os
import sys
from pathlib import Path

import click

from .pipeline.build import build_all_with_futures, build_futures_only


@click.group()
def cli():
	"""Tennis Master Futures Integration CLI."""
	pass


@cli.command()
@click.option("--data-root", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True)
@click.option("--out-dir", type=click.Path(file_okay=False, path_type=Path), required=True)
def build(data_root: Path, out_dir: Path):
	"""Build all outputs including ATP futures matches."""
	out_dir.mkdir(parents=True, exist_ok=True)
	build_all_with_futures(data_root=data_root, out_dir=out_dir)
	click.echo(f"Build complete with futures. Outputs in {out_dir}")


@cli.command()
@click.option("--data-root", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True)
@click.option("--out-dir", type=click.Path(file_okay=False, path_type=Path), required=True)
def futures_only(data_root: Path, out_dir: Path):
	"""Build only futures matches for testing."""
	out_dir.mkdir(parents=True, exist_ok=True)
	build_futures_only(data_root=data_root, out_dir=out_dir)
	click.echo(f"Futures-only build complete. Outputs in {out_dir}")


if __name__ == "__main__":
	cli()

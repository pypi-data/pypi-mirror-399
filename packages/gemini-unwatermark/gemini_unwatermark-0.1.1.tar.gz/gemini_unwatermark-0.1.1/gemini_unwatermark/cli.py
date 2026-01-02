"""CLI interface for gemini-watermark-remover."""

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

from .processor import process_image
from .utils import validate_image, get_output_path

app = typer.Typer(
    name="gemini-unwatermark",
    help="Remove watermarks from Gemini-generated images using LaMa inpainting.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def main(
    images: Annotated[
        list[Path],
        typer.Argument(
            help="Image file(s) to process. Supports glob patterns.",
            exists=True,
            readable=True,
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o",
            help="Output path (single image only).",
        ),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir", "-d",
            help="Output directory for batch processing.",
        ),
    ] = None,
    model_path: Annotated[
        Optional[Path],
        typer.Option(
            "--model-path",
            help="Custom ONNX model path (skips auto-download).",
            exists=True,
            readable=True,
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f",
            help="Overwrite existing output files.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet", "-q",
            help="Suppress progress output.",
        ),
    ] = False,
    workers: Annotated[
        int,
        typer.Option(
            "--workers", "-w",
            help="Number of parallel workers for batch processing.",
            min=1,
            max=8,
        ),
    ] = 4,
) -> None:
    """Remove watermarks from Gemini-generated images."""
    if output is not None and len(images) > 1:
        console.print("[red]Error:[/] --output can only be used with a single image.", style="bold")
        raise typer.Exit(1)

    for img in images:
        valid, error = validate_image(img)
        if not valid:
            console.print(f"[red]Error:[/] {error}")
            raise typer.Exit(1)

    outputs: list[tuple[Path, Path]] = []
    for img in images:
        out = get_output_path(img, output, output_dir)
        if out.exists() and not force:
            console.print(f"[yellow]Skipping:[/] {out} exists (use --force to overwrite)")
            continue
        outputs.append((img, out))

    if not outputs:
        console.print("[yellow]No images to process.[/]")
        raise typer.Exit(0)

    def process_one(inp: Path, out: Path) -> tuple[Path, Optional[str]]:
        try:
            process_image(inp, out, model_path=model_path, quiet=True)
            return inp, None
        except Exception as e:
            return inp, str(e)

    if len(outputs) == 1:
        inp, out = outputs[0]
        if not quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                progress.add_task(f"Processing {inp.name}...", total=None)
                process_image(inp, out, model_path=model_path, quiet=quiet)
        else:
            process_image(inp, out, model_path=model_path, quiet=quiet)
        if not quiet:
            console.print(f"[green]Saved:[/] {out}")
    else:
        failed: list[tuple[Path, str]] = []
        succeeded = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
        ) as progress:
            task = progress.add_task("Processing images...", total=len(outputs))

            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(process_one, inp, out): (inp, out) for inp, out in outputs}

                for future in as_completed(futures):
                    inp, error = future.result()
                    if error:
                        failed.append((inp, error))
                    else:
                        succeeded += 1
                    progress.update(task, advance=1)

        if not quiet:
            console.print(f"[green]Processed:[/] {succeeded}/{len(outputs)} images")
            if failed:
                for inp, error in failed:
                    console.print(f"[red]Failed:[/] {inp.name}: {error}")


if __name__ == "__main__":
    app()

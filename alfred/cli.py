from __future__ import annotations

import webbrowser
from pathlib import Path

import typer
from dotenv import load_dotenv

from alfred import orchestrator

app = typer.Typer(
    help="Alfred — agentic ad campaign generator. Company name in, three proposals out.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def run(
    company: str = typer.Argument(..., help="Company name to research, e.g. 'Liquid Death'"),
    out: Path = typer.Option(Path("out"), "--out", "-o", help="Output root directory."),
    backend: str | None = typer.Option(None, "--backend", "-b", help="openai | replicate | stub (overrides ALFRED_IMAGE_BACKEND)."),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open the report in the default browser when done."),
):
    """Run the end-to-end pipeline for a single company."""
    load_dotenv()
    from alfred.image_backends import build_backend
    image_backend = build_backend(backend) if backend else None
    report = orchestrator.run(company, out_root=out, image_backend=image_backend)
    typer.echo(str(report))
    if open_browser:
        webbrowser.open(report.resolve().as_uri())


if __name__ == "__main__":
    app()

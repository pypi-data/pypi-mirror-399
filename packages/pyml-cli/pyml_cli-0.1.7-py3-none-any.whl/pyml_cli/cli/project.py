"""Project initialization CLI."""

from pathlib import Path

from cookiecutter.main import cookiecutter
from typer import Typer

app = Typer()

PROJECT_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "project"


@app.command()
def init():
    """Initialize project from template."""
    cookiecutter(str(PROJECT_TEMPLATE_DIR.resolve()))

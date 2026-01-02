import typer
from pathlib import Path
from typing import Optional

from dumpster.api import dump

app = typer.Typer()

DEFAULT_DUMP_YAML = """# Dumpster configuration
output: sources.txt
extensions:
  - .py
  - .md
  - .yaml
  - .txt
contents:
  - "**/*.py"
  - "**/*.md"
"""


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """
    Calling without commnad start the dump

    """
    if ctx.invoked_subcommand is None:
        dump()


@app.command(
    help="Run dumpster",
)
def run():
    """Default command to dump code based on dump.yaml settings"""
    dump()


@app.command(help="Generate a dumpster configuration")
def init(
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    )
):
    """Create/update dump.yaml and .gitignore"""
    # Create dump.yaml if it doesn't exist
    dump_yaml_path = Path("dump.yaml")
    if not dump_yaml_path.exists():
        with open(dump_yaml_path, "w") as f:
            f.write(DEFAULT_DUMP_YAML)
        typer.echo(f"Created {dump_yaml_path}")
    else:
        typer.echo(f"File {dump_yaml_path} already exists, skipping creation")

    # Update .gitignore
    gitignore_path = Path(".gitignore")
    output_file = output or "sources.txt"

    if gitignore_path.exists():
        with open(gitignore_path, "r+") as f:
            content = f.read()
            if output_file not in content:
                f.write(f"\n# Dumpster output\n{output_file}\n")
                typer.echo(f"Updated {gitignore_path} with {output_file}")
            else:
                typer.echo(
                    f"Reference of {output_file} is already in {gitignore_path}, skipping"
                )
    else:
        with open(gitignore_path, "w") as f:
            f.write(f"# Dumpster output\n{output_file}\n")
        typer.echo(f"Created {gitignore_path} with {output_file}")


def cli():
    app()

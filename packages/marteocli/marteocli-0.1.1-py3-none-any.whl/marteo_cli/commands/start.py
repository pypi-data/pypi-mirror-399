import shutil
from enum import Enum
from pathlib import Path

import typer  # type: ignore
from rich.console import Console

app = typer.Typer()
console = Console()


class Template(str, Enum):
    blank = "blank"
    cmake = "cmake"
    default = "default"
    header = "header"
    hmake = "hmake"


@app.command()
def create(
    project_name: str = typer.Argument(..., help="Nome do projeto"),
    template: Template = typer.Option(
        Template.blank, "--template", "-t", help="Template a usar"
    ),
):
    base_dir = Path(__file__).parent.parent
    template_src = base_dir / "templates" / f"{template.value}"
    project_dir = Path.cwd() / project_name

    if project_dir.exists():
        console.print(f" ERRO: Directory '{project_name}' goes exists!")
        raise typer.Exit(1)

    if not template_src.exists():
        console.print(f" ERRO: Template '{template.value}' goes exists!")
        raise typer.Exit(1)

    try:
        shutil.copytree(template_src, project_dir)
        console.print(f" [green]✔[/green] Project '{project_name}' template created.")
        console.print(" Next steps:")
        console.print(f"  cd {project_name}")
        console.print("  read file README.md")
    except Exception as e:
        console.print(f" [red]ERRO: {e}[/red]")
        raise typer.Exit(1)

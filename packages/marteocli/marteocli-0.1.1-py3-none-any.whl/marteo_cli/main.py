import typer  # type: ignore
from rich.console import Console

from marteo_cli.commands import start
from marteo_cli.version import version

app = typer.Typer()
console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"{version}")
        raise typer.Exit()


version_options = typer.Option(
    None, "--version", "-v", callback=version_callback, is_eager=True
)


@app.callback()
def main(version: bool = version_options):
    pass


app.add_typer(start.app, name="start")

if __name__ == "__main__":
    app()

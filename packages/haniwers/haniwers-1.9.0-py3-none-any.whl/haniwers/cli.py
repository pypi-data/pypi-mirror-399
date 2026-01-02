import typer
from haniwers.v0.cli import app as v0_app
from haniwers.v1.cli import app as v1_app

app = typer.Typer(help="Haniwers CLI")

# v1 サブコマンドとして追加
app.add_typer(v0_app, name="v0", help="Haniwers v0 command group")

# v1 サブコマンドとして追加
app.add_typer(v1_app, name="v1", help="Haniwers v1 command group")

if __name__ == "__main__":
    app()

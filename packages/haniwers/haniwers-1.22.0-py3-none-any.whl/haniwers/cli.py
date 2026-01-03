import typer
from haniwers.v1.cli import app as v1_app
from haniwers.v2.cli import app as v2_app

app = typer.Typer(help="Haniwers CLI")

# v1 サブコマンドとして追加
app.add_typer(v1_app, name="v1", help="Haniwers v1 command group")

# v2 サブコマンドとして追加
app.add_typer(v2_app, name="v2", help="Haniwers v2 command group")

if __name__ == "__main__":
    app()

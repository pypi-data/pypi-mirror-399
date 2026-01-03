import typer


app = typer.Typer()

@app.command()
def main(name: str):
    """
    Greet the user
    """
    typer.echo(f"Hello {name}")

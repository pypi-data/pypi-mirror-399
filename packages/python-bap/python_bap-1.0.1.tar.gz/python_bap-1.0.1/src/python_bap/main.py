import typer


app = typer.Typer()

@app.command()
def main(name: str, language: str = 'en'):
    """
    Greet the user
    """
    if language == 'sp':
        typer.echo(f"Hola {name}")
    else:
        typer.echo(f"Hello {name}")
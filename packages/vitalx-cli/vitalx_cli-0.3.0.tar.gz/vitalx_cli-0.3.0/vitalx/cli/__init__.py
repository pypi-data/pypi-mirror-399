import typer

from .auth import auth_commands

app = typer.Typer(no_args_is_help=True)

app.add_typer(auth_commands, name="auth")


def main() -> None:
    app()


if __name__ == "__main__":
    main()

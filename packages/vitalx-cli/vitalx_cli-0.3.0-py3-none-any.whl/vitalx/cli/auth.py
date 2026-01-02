import rich
import typer
from vitalx.cli_auth import (
    current_tokens,
    get_userinfo,
    initiate_device_code_flow,
    poll_for_device_code_flow_completion,
)

auth_commands = typer.Typer(no_args_is_help=True)


@auth_commands.command()
def login() -> None:
    if current_tokens():
        rich.print(
            "[bold yellow]There is an existing Vital Dashboard login.[/bold yellow]"
        )
        typer.confirm("Do you want to re-authenticate?", abort=True)

    flow = initiate_device_code_flow()

    rich.print(
        "You will be asked to confirm the code "
        f"[bold]{flow['user_code']}[/bold] "
        "as you sign-in with the Vital Dashboard."
    )

    typer.confirm(
        "Ready to proceed in your default web browser?",
        abort=True,
    )

    import webbrowser

    webbrowser.open(flow["verification_uri_complete"])

    poll_for_device_code_flow_completion(flow)

    rich.print("[bold green]You have logged in successfully.[/bold green]")


@auth_commands.command()
def info() -> None:
    tokens = current_tokens()

    if not tokens:
        rich.print("[bold red]No signed-in user with vitalx-cli.[/bold red]")
        return

    claims = get_userinfo(tokens["id_token"])

    rich.print(f"Logged in as [bold]{claims['name']}[/bold] ({claims['email']})")

"""Configuration and authentication commands."""

import asyncio
import webbrowser
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from alpha_cli.credentials import (
    get_alpha_credentials,
    get_kalshi_credentials,
    delete_alpha_credentials,
    delete_kalshi_credentials,
    store_kalshi_credentials,
    mask_api_key,
)
from alpha_cli.types import KalshiCredentials
from alpha_cli.output import console, print_error, print_success, print_warning

app = typer.Typer(
    name="config",
    help="Configure Alpha CLI settings and credentials.",
    no_args_is_help=True,
)


@app.command("show")
def show_config() -> None:
    """Show current configuration."""
    alpha_creds = get_alpha_credentials()
    kalshi_creds = get_kalshi_credentials()

    content = "[bold]Alpha CLI Configuration[/bold]\n\n"

    # Alpha credentials
    content += "[bold]Alpha Account:[/bold]\n"
    if alpha_creds:
        content += f"  Email: {alpha_creds.user_email or 'N/A'}\n"
        content += f"  API Key: {mask_api_key(alpha_creds.api_key)}\n"
    else:
        content += "  [dim]Not authenticated. Run `alpha login` to sign in.[/dim]\n"

    content += "\n[bold]Kalshi Credentials:[/bold]\n"
    if kalshi_creds:
        content += f"  API Key: {mask_api_key(kalshi_creds.api_key)}\n"
        content += f"  Private Key: {kalshi_creds.private_key_path or 'N/A'}\n"
    else:
        content += "  [dim]Not configured. Run `alpha config kalshi` to set up.[/dim]\n"

    console.print(Panel(content, title="Configuration"))


@app.command("kalshi")
def configure_kalshi(
    api_key: Annotated[
        str | None, typer.Option("--api-key", "-k", help="Kalshi API key")
    ] = None,
    private_key: Annotated[
        str | None, typer.Option("--private-key", "-p", help="Path to private key")
    ] = None,
) -> None:
    """Configure Kalshi API credentials."""
    # If not provided via options, prompt interactively
    if api_key is None:
        api_key = typer.prompt("Enter Kalshi API Key", hide_input=True)

    if private_key is None:
        private_key = typer.prompt(
            "Enter path to private key (optional)",
            default="",
            show_default=False,
        )
        if not private_key:
            private_key = None

    creds = KalshiCredentials(
        api_key=api_key,
        private_key_path=private_key,
    )

    store_kalshi_credentials(creds)
    print_success("Kalshi credentials stored securely in system keyring.")


@app.command("clear")
def clear_credentials(
    all: Annotated[bool, typer.Option("--all", "-a", help="Clear all credentials")] = False,
    alpha: Annotated[bool, typer.Option("--alpha", help="Clear Alpha credentials")] = False,
    kalshi: Annotated[bool, typer.Option("--kalshi", help="Clear Kalshi credentials")] = False,
) -> None:
    """Clear stored credentials."""
    if all or (not alpha and not kalshi):
        # Clear all if --all or no specific flags
        if typer.confirm("Clear all stored credentials?"):
            delete_alpha_credentials()
            delete_kalshi_credentials()
            print_success("All credentials cleared.")
        return

    if alpha:
        delete_alpha_credentials()
        print_success("Alpha credentials cleared.")

    if kalshi:
        delete_kalshi_credentials()
        print_success("Kalshi credentials cleared.")

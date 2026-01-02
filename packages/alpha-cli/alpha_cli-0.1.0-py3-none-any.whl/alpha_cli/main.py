"""Main entry point for Alpha CLI."""

import typer
from rich.console import Console
from rich.panel import Panel

from alpha_cli import __version__
from alpha_cli.commands.kalshi import app as kalshi_app
from alpha_cli.commands.congress import app as congress_app
from alpha_cli.commands.config import app as config_app
from alpha_cli.commands.scan import app as scan_app
from alpha_cli.credentials import get_alpha_credentials, store_alpha_credentials, delete_alpha_credentials
from alpha_cli.types import AlphaCredentials
from alpha_cli.output import console, print_success, print_error, print_info

# Create main app
app = typer.Typer(
    name="alpha",
    help="Cross-reference congressional trades with prediction markets.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

# Add subcommands
app.add_typer(kalshi_app, name="kalshi")
app.add_typer(congress_app, name="congress")
app.add_typer(config_app, name="config")
app.add_typer(scan_app, name="scan")


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"alpha-cli version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """
    Alpha CLI - Cross-reference congressional trades with prediction markets.

    Free features:
      alpha kalshi markets     List Kalshi prediction markets
      alpha kalshi market      Get market details
      alpha kalshi orderbook   View order book
      alpha kalshi find        Search markets

      alpha congress trades    List congressional trades
      alpha congress member    Get trades for a member
      alpha congress ticker    Get trades for a ticker
      alpha congress top       Most traded tickers

    Premium features ($20/month):
      alpha scan               Cross-reference trades with markets

    Get started:
      alpha kalshi markets     See what's available
      alpha congress trades    See recent trades
    """
    pass


@app.command()
def login() -> None:
    """
    Authenticate with Alpha CLI.

    Opens a browser window to complete authentication.
    Your API key is stored securely in your system keyring.
    """
    console.print(
        Panel(
            "[bold]Alpha CLI Authentication[/bold]\n\n"
            "This would open a browser to complete authentication.\n\n"
            "[dim]Note: Backend not yet implemented. For testing, you can\n"
            "set the ALPHA_API_KEY environment variable.[/dim]",
            title="Login",
        )
    )

    # For now, provide manual key entry for testing
    if typer.confirm("\nWould you like to enter an API key manually for testing?"):
        api_key = typer.prompt("Enter API key", hide_input=True)
        email = typer.prompt("Enter email (optional)", default="")

        creds = AlphaCredentials(
            api_key=api_key,
            user_email=email if email else None,
        )
        store_alpha_credentials(creds)
        print_success("Credentials stored securely in system keyring.")


@app.command()
def logout() -> None:
    """
    Log out and remove stored credentials.
    """
    creds = get_alpha_credentials()
    if not creds:
        print_info("Not currently logged in.")
        return

    if typer.confirm("Remove stored credentials?"):
        delete_alpha_credentials()
        print_success("Logged out successfully.")


@app.command()
def status() -> None:
    """
    Show current authentication status.
    """
    creds = get_alpha_credentials()

    if creds:
        console.print(
            Panel(
                f"[green]Authenticated[/green]\n\n"
                f"Email: {creds.user_email or 'N/A'}\n"
                f"API Key: {creds.api_key[:16]}...{creds.api_key[-4:]}\n\n"
                "[dim]Subscription status would be shown here[/dim]",
                title="Account Status",
            )
        )
    else:
        console.print(
            Panel(
                "[yellow]Not authenticated[/yellow]\n\n"
                "Free features are available without an account.\n"
                "Run `alpha login` to unlock premium features.",
                title="Account Status",
            )
        )


@app.command()
def upgrade() -> None:
    """
    Upgrade to Alpha CLI Premium.

    Premium features include:
    - AI-powered market matching
    - Higher accuracy cross-references
    - Priority support
    """
    console.print(
        Panel(
            "[bold]Alpha CLI Premium[/bold]\n\n"
            "Premium features:\n"
            "  [green]+[/green] AI-powered ticker-to-market matching\n"
            "  [green]+[/green] Higher accuracy cross-references\n"
            "  [green]+[/green] Priority support\n"
            "  [green]+[/green] Unlimited scan calls\n\n"
            "[bold]$20/month[/bold] - 7-day free trial\n\n"
            "[dim]Payment would be handled via Stripe Checkout.\n"
            "This feature is not yet implemented.[/dim]",
            title="Upgrade to Premium",
        )
    )


if __name__ == "__main__":
    app()

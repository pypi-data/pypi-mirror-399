"""Scan command for cross-referencing congress trades with prediction markets."""

import asyncio
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from alpha_cli.credentials import get_alpha_credentials
from alpha_cli.services.scan import ScanService
from alpha_cli.types import AuthContext, AuthState
from alpha_cli.output import (
    OutputFormat,
    console,
    format_date,
    format_party,
    format_trade_type,
    format_amount,
    format_price,
    output_json,
    output_csv,
    print_error,
    print_warning,
    to_serializable,
)

app = typer.Typer(
    name="scan",
    help="Cross-reference congressional trades with prediction markets (Premium).",
)


def get_auth_context() -> AuthContext:
    """Get current authentication context."""
    creds = get_alpha_credentials()
    if not creds:
        return AuthContext(state=AuthState.ANONYMOUS)

    # For now, treat any credentials as free tier
    # In the full implementation, we'd validate with the backend
    return AuthContext(
        state=AuthState.AUTHENTICATED_FREE,
        user_email=creds.user_email,
    )


@app.callback(invoke_without_command=True)
def scan_main(
    ctx: typer.Context,
    days: Annotated[int, typer.Option("--days", "-d", help="Days to look back")] = 30,
    ticker: Annotated[str | None, typer.Option("--ticker", "-t", help="Filter by ticker")] = None,
    party: Annotated[
        str | None, typer.Option("--party", "-p", help="Filter by party (R or D)")
    ] = None,
    min_relevance: Annotated[
        float, typer.Option("--min-relevance", "-r", help="Minimum relevance score (0-1)")
    ] = 0.5,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum results")] = 20,
    format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """
    Cross-reference congressional trades with prediction markets.

    This command finds congressional stock trades and shows
    relevant prediction markets that could be affected.

    Basic matching (Tier 1) is available to all users.
    Premium users get enhanced AI-powered matching.
    """
    if ctx.invoked_subcommand is not None:
        return

    async def _run() -> None:
        auth_context = get_auth_context()

        # Validate party filter
        party_filter: Literal["R", "D"] | None = None
        if party:
            if party.upper() not in ("R", "D"):
                print_error("Party must be 'R' or 'D'")
                raise typer.Exit(1)
            party_filter = "R" if party.upper() == "R" else "D"

        service = ScanService()
        try:
            result = await service.scan(
                days=days,
                ticker=ticker,
                party=party_filter,
                min_relevance=min_relevance,
                auth_context=auth_context,
            )

            cross_refs = result.cross_references[:limit]

            if result.is_stale:
                print_warning("Using cached market data. Live data temporarily unavailable.")

            if format == OutputFormat.JSON:
                output_json(to_serializable(result))
            elif format == OutputFormat.CSV:
                # Flatten for CSV
                rows = []
                for cr in cross_refs:
                    for market in cr.related_markets:
                        rows.append({
                            "trade_date": cr.congress_trade.transaction_date,
                            "member": cr.congress_trade.representative,
                            "party": cr.congress_trade.party,
                            "trade_type": cr.congress_trade.trade_type,
                            "ticker": cr.congress_trade.ticker,
                            "amount": cr.congress_trade.amount,
                            "market_ticker": market.ticker,
                            "market_title": market.title,
                            "yes_price": float(market.yes_price),
                            "no_price": float(market.no_price),
                            "relevance": market.relevance_score,
                        })
                output_csv(rows)
            else:
                if not cross_refs:
                    console.print("[dim]No cross-references found.[/dim]")
                    console.print(
                        "\n[dim]This could mean:[/dim]"
                        "\n  - No congressional trades in the specified period"
                        "\n  - No relevant Kalshi markets for traded tickers"
                        "\n  - Try increasing --days or removing filters"
                    )
                    return

                console.print(
                    f"\n[bold]Congressional Trades + Prediction Markets[/bold]\n"
                    f"[dim]Last {days} days | Relevance >= {min_relevance}[/dim]\n"
                )

                for i, cr in enumerate(cross_refs, 1):
                    trade = cr.congress_trade

                    # Trade header
                    header_text = Text()
                    header_text.append(f"{i}. ", style="dim")
                    header_text.append(trade.ticker, style="bold cyan")
                    header_text.append(" - ")
                    header_text.append(trade.representative)
                    header_text.append(" (")
                    if trade.party == "R":
                        header_text.append("R", style="red")
                    elif trade.party == "D":
                        header_text.append("D", style="blue")
                    else:
                        header_text.append("-")
                    header_text.append(")")

                    console.print(header_text)

                    # Trade details
                    trade_type_text = Text()
                    if trade.trade_type == "purchase":
                        trade_type_text.append("BUY", style="green bold")
                    else:
                        trade_type_text.append("SELL", style="red bold")

                    console.print(
                        f"   {trade_type_text} | {format_amount(trade.amount)} | {format_date(trade.transaction_date)}"
                    )

                    # Related markets
                    if cr.related_markets:
                        console.print("   [dim]Related Markets:[/dim]")
                        for market in cr.related_markets[:3]:  # Show top 3
                            relevance_pct = int(market.relevance_score * 100)
                            market_line = (
                                f"     [{market.relevance_type}] {market.ticker}: "
                                f"YES @ [green]{format_price(market.yes_price)}[/green] "
                                f"({relevance_pct}% match)"
                            )
                            console.print(market_line)
                    else:
                        console.print("   [dim]No related markets found[/dim]")

                    console.print()  # Blank line between entries

                console.print(f"[dim]Showing {len(cross_refs)} cross-references[/dim]")

                # Show premium upsell if not premium
                if not auth_context.can_use_premium():
                    console.print(
                        "\n[yellow]Tip:[/yellow] Premium users get AI-powered matching "
                        "with higher accuracy. Run `alpha upgrade` to learn more."
                    )

        finally:
            await service.close()

    asyncio.run(_run())

"""Congressional trading commands."""

import asyncio
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from alpha_cli.clients.congress import CongressClient
from alpha_cli.output import (
    OutputFormat,
    console,
    format_date,
    format_party,
    format_trade_type,
    format_amount,
    output_json,
    output_csv,
    print_error,
    to_serializable,
)

app = typer.Typer(
    name="congress",
    help="Query congressional trading data.",
    no_args_is_help=True,
)


@app.command("trades")
def list_trades(
    days: Annotated[int, typer.Option("--days", "-d", help="Days to look back")] = 30,
    ticker: Annotated[str | None, typer.Option("--ticker", "-t", help="Filter by ticker")] = None,
    party: Annotated[
        str | None, typer.Option("--party", "-p", help="Filter by party (R or D)")
    ] = None,
    chamber: Annotated[
        str, typer.Option("--chamber", "-c", help="Filter by chamber (house, senate, all)")
    ] = "all",
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum trades to show")] = 50,
    format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """List recent congressional trades."""

    async def _run() -> None:
        client = CongressClient()
        try:
            # Validate party filter
            party_filter: Literal["R", "D"] | None = None
            if party:
                if party.upper() not in ("R", "D"):
                    print_error("Party must be 'R' or 'D'")
                    raise typer.Exit(1)
                party_filter = "R" if party.upper() == "R" else "D"

            # Validate chamber filter
            chamber_filter: Literal["house", "senate", "all"] = "all"
            if chamber.lower() in ("house", "senate", "all"):
                chamber_filter = chamber.lower()  # type: ignore
            else:
                print_error("Chamber must be 'house', 'senate', or 'all'")
                raise typer.Exit(1)

            trades = await client.get_trades(
                days=days,
                ticker=ticker,
                party=party_filter,
                chamber=chamber_filter,
            )

            # Limit results
            trades = trades[:limit]

            if format == OutputFormat.JSON:
                output_json([to_serializable(t) for t in trades])
            elif format == OutputFormat.CSV:
                output_csv([to_serializable(t) for t in trades])
            else:
                if not trades:
                    console.print("[dim]No trades found.[/dim]")
                    return

                table = Table(show_header=True, header_style="bold")
                table.add_column("Date", style="dim")
                table.add_column("Member")
                table.add_column("Party", justify="center")
                table.add_column("Type", justify="center")
                table.add_column("Ticker", style="cyan")
                table.add_column("Amount", justify="right")
                table.add_column("Asset")

                for t in trades:
                    table.add_row(
                        format_date(t.transaction_date),
                        t.representative[:25] + "..." if len(t.representative) > 25 else t.representative,
                        format_party(t.party),
                        format_trade_type(t.trade_type),
                        t.ticker,
                        format_amount(t.amount),
                        t.asset_description[:30] + "..." if len(t.asset_description) > 30 else t.asset_description,
                    )

                console.print(table)
                console.print(f"\n[dim]Showing {len(trades)} trades from last {days} days[/dim]")
        finally:
            await client.close()

    asyncio.run(_run())


@app.command("member")
def get_member_trades(
    name: Annotated[str, typer.Argument(help="Member name (partial match)")],
    days: Annotated[int, typer.Option("--days", "-d", help="Days to look back")] = 365,
    format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Get trades for a specific member of Congress."""

    async def _run() -> None:
        client = CongressClient()
        try:
            trades = await client.get_member_trades(member=name, days=days)

            if format == OutputFormat.JSON:
                output_json([to_serializable(t) for t in trades])
            elif format == OutputFormat.CSV:
                output_csv([to_serializable(t) for t in trades])
            else:
                if not trades:
                    console.print(f"[dim]No trades found for '{name}'[/dim]")
                    return

                # Get member info from first trade
                member_name = trades[0].representative
                party = trades[0].party

                # Calculate summary stats
                purchases = sum(1 for t in trades if t.trade_type == "purchase")
                sales = sum(1 for t in trades if t.trade_type == "sale")
                tickers = set(t.ticker for t in trades)

                header = f"[bold]{member_name}[/bold]"
                if party:
                    header += f" ({party})"

                console.print(Panel(f"""
{header}

[bold]Trading Activity (last {days} days):[/bold]
  Total Trades: {len(trades)}
  Purchases: [green]{purchases}[/green]
  Sales: [red]{sales}[/red]
  Unique Tickers: {len(tickers)}
""", title="Member Profile"))

                # Show recent trades
                table = Table(show_header=True, header_style="bold", title="Recent Trades")
                table.add_column("Date", style="dim")
                table.add_column("Type", justify="center")
                table.add_column("Ticker", style="cyan")
                table.add_column("Amount", justify="right")
                table.add_column("Asset")

                for t in trades[:20]:  # Show last 20
                    table.add_row(
                        format_date(t.transaction_date),
                        format_trade_type(t.trade_type),
                        t.ticker,
                        format_amount(t.amount),
                        t.asset_description[:40] + "..." if len(t.asset_description) > 40 else t.asset_description,
                    )

                console.print(table)

                if len(trades) > 20:
                    console.print(f"\n[dim]Showing 20 of {len(trades)} trades[/dim]")
        finally:
            await client.close()

    asyncio.run(_run())


@app.command("ticker")
def get_ticker_trades(
    ticker: Annotated[str, typer.Argument(help="Stock ticker (e.g., NVDA)")],
    days: Annotated[int, typer.Option("--days", "-d", help="Days to look back")] = 365,
    format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Get congressional trades for a specific ticker."""

    async def _run() -> None:
        client = CongressClient()
        try:
            trades = await client.get_ticker_trades(ticker=ticker.upper(), days=days)

            if format == OutputFormat.JSON:
                output_json([to_serializable(t) for t in trades])
            elif format == OutputFormat.CSV:
                output_csv([to_serializable(t) for t in trades])
            else:
                if not trades:
                    console.print(f"[dim]No congressional trades found for '{ticker.upper()}'[/dim]")
                    return

                # Calculate summary stats
                purchases = sum(1 for t in trades if t.trade_type == "purchase")
                sales = sum(1 for t in trades if t.trade_type == "sale")
                members = set(t.representative for t in trades)
                republicans = sum(1 for t in trades if t.party == "R")
                democrats = sum(1 for t in trades if t.party == "D")

                asset_desc = trades[0].asset_description if trades else ticker.upper()

                console.print(Panel(f"""
[bold cyan]{ticker.upper()}[/bold cyan] - {asset_desc}

[bold]Congressional Trading Activity (last {days} days):[/bold]
  Total Trades: {len(trades)}
  Purchases: [green]{purchases}[/green]
  Sales: [red]{sales}[/red]

[bold]By Party:[/bold]
  Republicans: [red]{republicans}[/red]
  Democrats: [blue]{democrats}[/blue]

[bold]Members Trading:[/bold] {len(members)}
""", title=f"Ticker: {ticker.upper()}"))

                # Show trades
                table = Table(show_header=True, header_style="bold", title="Trades")
                table.add_column("Date", style="dim")
                table.add_column("Member")
                table.add_column("Party", justify="center")
                table.add_column("Type", justify="center")
                table.add_column("Amount", justify="right")

                for t in trades[:30]:  # Show last 30
                    table.add_row(
                        format_date(t.transaction_date),
                        t.representative[:30] + "..." if len(t.representative) > 30 else t.representative,
                        format_party(t.party),
                        format_trade_type(t.trade_type),
                        format_amount(t.amount),
                    )

                console.print(table)

                if len(trades) > 30:
                    console.print(f"\n[dim]Showing 30 of {len(trades)} trades[/dim]")
        finally:
            await client.close()

    asyncio.run(_run())


@app.command("top")
def get_top_tickers(
    days: Annotated[int, typer.Option("--days", "-d", help="Days to look back")] = 30,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Number of tickers to show")] = 20,
    format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Show most traded tickers by Congress."""

    async def _run() -> None:
        client = CongressClient()
        try:
            top_tickers = await client.get_top_traded_tickers(days=days, limit=limit)

            if format == OutputFormat.JSON:
                output_json([{"ticker": t, "count": c} for t, c in top_tickers])
            elif format == OutputFormat.CSV:
                output_csv([{"ticker": t, "count": c} for t, c in top_tickers])
            else:
                if not top_tickers:
                    console.print("[dim]No trades found.[/dim]")
                    return

                table = Table(show_header=True, header_style="bold", title=f"Top {limit} Traded Tickers (last {days} days)")
                table.add_column("Rank", justify="right", style="dim")
                table.add_column("Ticker", style="cyan")
                table.add_column("Trades", justify="right")
                table.add_column("Bar", min_width=30)

                max_count = top_tickers[0][1] if top_tickers else 1
                for i, (ticker, count) in enumerate(top_tickers, 1):
                    bar_width = int((count / max_count) * 30)
                    bar = "[green]" + "=" * bar_width + "[/green]"
                    table.add_row(str(i), ticker, str(count), bar)

                console.print(table)
        finally:
            await client.close()

    asyncio.run(_run())

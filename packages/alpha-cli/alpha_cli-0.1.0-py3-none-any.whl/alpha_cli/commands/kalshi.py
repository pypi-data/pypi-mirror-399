"""Kalshi market commands."""

import asyncio
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from alpha_cli.clients.kalshi import KalshiClient
from alpha_cli.output import (
    OutputFormat,
    console,
    format_price,
    output_json,
    output_csv,
    print_error,
    to_serializable,
)

app = typer.Typer(
    name="kalshi",
    help="Query Kalshi prediction markets.",
    no_args_is_help=True,
)


@app.command("markets")
def list_markets(
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum markets to show")] = 20,
    status: Annotated[
        str | None, typer.Option("--status", "-s", help="Filter by status (open, closed, settled)")
    ] = "open",
    format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """List Kalshi markets."""

    async def _run() -> None:
        client = KalshiClient()
        try:
            markets, _ = await client.get_markets(limit=limit, status=status)

            if format == OutputFormat.JSON:
                output_json([to_serializable(m) for m in markets])
            elif format == OutputFormat.CSV:
                output_csv([to_serializable(m) for m in markets])
            else:
                if not markets:
                    console.print("[dim]No markets found.[/dim]")
                    return

                table = Table(show_header=True, header_style="bold")
                table.add_column("Ticker", style="cyan", no_wrap=True)
                table.add_column("Title", max_width=50)
                table.add_column("YES", justify="right", style="green")
                table.add_column("NO", justify="right", style="red")
                table.add_column("Volume", justify="right")

                for m in markets:
                    table.add_row(
                        m.ticker,
                        m.title[:50] + "..." if len(m.title) > 50 else m.title,
                        format_price(m.yes_price),
                        format_price(m.no_price),
                        f"{m.volume:,}",
                    )

                console.print(table)
                console.print(f"\n[dim]Showing {len(markets)} markets[/dim]")
        finally:
            await client.close()

    asyncio.run(_run())


@app.command("market")
def get_market(
    ticker: Annotated[str, typer.Argument(help="Market ticker (e.g., KXBTC-150K)")],
    format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Get details for a specific market."""

    async def _run() -> None:
        client = KalshiClient()
        try:
            market = await client.get_market(ticker.upper())

            if market is None:
                print_error(f"Market '{ticker}' not found.")
                raise typer.Exit(1)

            if format == OutputFormat.JSON:
                output_json(to_serializable(market))
            elif format == OutputFormat.CSV:
                output_csv([to_serializable(market)])
            else:
                # Create detailed panel
                content = f"""[bold cyan]{market.ticker}[/bold cyan]

[bold]{market.title}[/bold]
{market.subtitle or ''}

[bold]Prices:[/bold]
  YES: [green]{format_price(market.yes_price)}[/green] (Bid: {format_price(market.yes_bid)}, Ask: {format_price(market.yes_ask)})
  NO:  [red]{format_price(market.no_price)}[/red] (Bid: {format_price(market.no_bid)}, Ask: {format_price(market.no_ask)})

[bold]Activity:[/bold]
  Volume: {market.volume:,}
  Open Interest: {market.open_interest:,}

[bold]Status:[/bold] {market.status}
[bold]Close Time:[/bold] {market.close_time or 'N/A'}
[bold]Result:[/bold] {market.result or 'Pending'}
"""
                console.print(Panel(content, title="Market Details"))
        finally:
            await client.close()

    asyncio.run(_run())


@app.command("orderbook")
def get_orderbook(
    ticker: Annotated[str, typer.Argument(help="Market ticker")],
    depth: Annotated[int, typer.Option("--depth", "-d", help="Order book depth")] = 10,
    format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Get order book for a market."""

    async def _run() -> None:
        client = KalshiClient()
        try:
            orderbook = await client.get_orderbook(ticker.upper(), depth=depth)

            if orderbook is None:
                print_error(f"Market '{ticker}' not found.")
                raise typer.Exit(1)

            if format == OutputFormat.JSON:
                output_json(to_serializable(orderbook))
            elif format == OutputFormat.CSV:
                # Flatten orderbook for CSV
                rows = []
                for i, (price, qty) in enumerate(orderbook.yes_bids):
                    rows.append({"side": "YES", "type": "bid", "price": float(price), "quantity": qty})
                for i, (price, qty) in enumerate(orderbook.yes_asks):
                    rows.append({"side": "YES", "type": "ask", "price": float(price), "quantity": qty})
                for i, (price, qty) in enumerate(orderbook.no_bids):
                    rows.append({"side": "NO", "type": "bid", "price": float(price), "quantity": qty})
                for i, (price, qty) in enumerate(orderbook.no_asks):
                    rows.append({"side": "NO", "type": "ask", "price": float(price), "quantity": qty})
                output_csv(rows)
            else:
                console.print(f"\n[bold cyan]Order Book: {ticker.upper()}[/bold cyan]\n")

                # YES side
                yes_table = Table(title="YES", show_header=True, header_style="bold")
                yes_table.add_column("Bid Qty", justify="right", style="green")
                yes_table.add_column("Bid", justify="right", style="green")
                yes_table.add_column("Ask", justify="right", style="red")
                yes_table.add_column("Ask Qty", justify="right", style="red")

                max_rows = max(len(orderbook.yes_bids), len(orderbook.yes_asks))
                for i in range(max_rows):
                    bid_qty = str(orderbook.yes_bids[i][1]) if i < len(orderbook.yes_bids) else ""
                    bid_price = format_price(orderbook.yes_bids[i][0]) if i < len(orderbook.yes_bids) else ""
                    ask_price = format_price(orderbook.yes_asks[i][0]) if i < len(orderbook.yes_asks) else ""
                    ask_qty = str(orderbook.yes_asks[i][1]) if i < len(orderbook.yes_asks) else ""
                    yes_table.add_row(bid_qty, bid_price, ask_price, ask_qty)

                console.print(yes_table)

                # NO side
                no_table = Table(title="NO", show_header=True, header_style="bold")
                no_table.add_column("Bid Qty", justify="right", style="green")
                no_table.add_column("Bid", justify="right", style="green")
                no_table.add_column("Ask", justify="right", style="red")
                no_table.add_column("Ask Qty", justify="right", style="red")

                max_rows = max(len(orderbook.no_bids), len(orderbook.no_asks))
                for i in range(max_rows):
                    bid_qty = str(orderbook.no_bids[i][1]) if i < len(orderbook.no_bids) else ""
                    bid_price = format_price(orderbook.no_bids[i][0]) if i < len(orderbook.no_bids) else ""
                    ask_price = format_price(orderbook.no_asks[i][0]) if i < len(orderbook.no_asks) else ""
                    ask_qty = str(orderbook.no_asks[i][1]) if i < len(orderbook.no_asks) else ""
                    no_table.add_row(bid_qty, bid_price, ask_price, ask_qty)

                console.print(no_table)
        finally:
            await client.close()

    asyncio.run(_run())


@app.command("find")
def find_markets(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum results")] = 20,
    format: Annotated[
        OutputFormat, typer.Option("--format", "-f", help="Output format")
    ] = OutputFormat.TABLE,
) -> None:
    """Search for markets by query."""

    async def _run() -> None:
        client = KalshiClient()
        try:
            markets = await client.search_markets(query, limit=limit)

            if format == OutputFormat.JSON:
                output_json([to_serializable(m) for m in markets])
            elif format == OutputFormat.CSV:
                output_csv([to_serializable(m) for m in markets])
            else:
                if not markets:
                    console.print(f"[dim]No markets found matching '{query}'[/dim]")
                    return

                table = Table(show_header=True, header_style="bold")
                table.add_column("Ticker", style="cyan", no_wrap=True)
                table.add_column("Title", max_width=50)
                table.add_column("YES", justify="right", style="green")
                table.add_column("NO", justify="right", style="red")

                for m in markets:
                    table.add_row(
                        m.ticker,
                        m.title[:50] + "..." if len(m.title) > 50 else m.title,
                        format_price(m.yes_price),
                        format_price(m.no_price),
                    )

                console.print(table)
                console.print(f"\n[dim]Found {len(markets)} markets matching '{query}'[/dim]")
        finally:
            await client.close()

    asyncio.run(_run())

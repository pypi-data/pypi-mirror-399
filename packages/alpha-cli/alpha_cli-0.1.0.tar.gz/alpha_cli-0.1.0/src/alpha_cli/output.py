"""Output formatting utilities for CLI."""

import csv
import io
import json
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


class OutputFormat(str, Enum):
    """Output format options."""

    TABLE = "table"
    JSON = "json"
    CSV = "csv"


console = Console()
error_console = Console(stderr=True)


def format_price(price: Decimal) -> str:
    """Format a price as cents."""
    cents = int(price * 100)
    return f"{cents}c"


def format_amount(amount: str) -> str:
    """Format an amount range."""
    # Clean up common formats
    amount = amount.strip()
    if not amount:
        return "N/A"
    return amount


def format_date(date_str: str) -> str:
    """Format a date string."""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except ValueError:
        return date_str


def format_party(party: str | None) -> Text:
    """Format party with color."""
    if party == "R":
        return Text("R", style="red")
    elif party == "D":
        return Text("D", style="blue")
    elif party == "I":
        return Text("I", style="yellow")
    else:
        return Text("-", style="dim")


def format_trade_type(trade_type: str) -> Text:
    """Format trade type with color."""
    if trade_type == "purchase":
        return Text("BUY", style="green")
    elif trade_type == "sale":
        return Text("SELL", style="red")
    else:
        return Text(trade_type.upper(), style="yellow")


def to_serializable(obj: Any) -> Any:
    """Convert object to JSON-serializable format."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, "__dict__"):
        return {k: to_serializable(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    return obj


def output_json(data: Any) -> None:
    """Output data as JSON."""
    console.print_json(json.dumps(to_serializable(data), indent=2))


def output_csv(data: list[dict], headers: list[str] | None = None) -> None:
    """Output data as CSV."""
    if not data:
        return

    output = io.StringIO()
    if headers is None:
        headers = list(data[0].keys())

    writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    for row in data:
        writer.writerow(to_serializable(row))

    console.print(output.getvalue())


def print_error(message: str) -> None:
    """Print an error message."""
    error_console.print(f"[red]Error:[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]Warning:[/yellow] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]Success:[/green] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[blue]Info:[/blue] {message}")


def create_market_table() -> Table:
    """Create a table for market data."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("Ticker", style="cyan", no_wrap=True)
    table.add_column("Title", max_width=50)
    table.add_column("YES", justify="right", style="green")
    table.add_column("NO", justify="right", style="red")
    table.add_column("Volume", justify="right")
    table.add_column("Status")
    return table


def create_trades_table() -> Table:
    """Create a table for congress trades."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("Date", style="dim")
    table.add_column("Member")
    table.add_column("Party", justify="center")
    table.add_column("Type", justify="center")
    table.add_column("Ticker", style="cyan")
    table.add_column("Amount", justify="right")
    return table


def create_orderbook_panel(ticker: str, side: str, bids: list, asks: list) -> Panel:
    """Create a panel for orderbook display."""
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("Bid", justify="right", style="green")
    table.add_column("Price", justify="center")
    table.add_column("Ask", justify="right", style="red")

    # Combine bids and asks at each price level
    max_rows = max(len(bids), len(asks))
    for i in range(max_rows):
        bid_str = ""
        price_str = ""
        ask_str = ""

        if i < len(bids):
            price, qty = bids[i]
            bid_str = str(qty)
            price_str = format_price(price)
        if i < len(asks):
            price, qty = asks[i]
            ask_str = str(qty)
            if not price_str:
                price_str = format_price(price)

        table.add_row(bid_str, price_str, ask_str)

    return Panel(table, title=f"{side} Order Book - {ticker}")

"""CLI commands for Alpha CLI."""

from alpha_cli.commands.kalshi import app as kalshi_app
from alpha_cli.commands.congress import app as congress_app
from alpha_cli.commands.config import app as config_app
from alpha_cli.commands.scan import app as scan_app

__all__ = [
    "kalshi_app",
    "congress_app",
    "config_app",
    "scan_app",
]

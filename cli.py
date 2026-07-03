"""
cli.py
======
Command-line interface for the Binance Futures Trading Bot.

This module owns two responsibilities:

1. **Argument parsing** — defining and parsing CLI arguments with ``argparse``.
2. **Rich UI rendering** — printing professional, coloured panels and tables
   using the ``rich`` library (progress spinners, confirmation prompts,
   order summaries, and result displays).

It intentionally contains *no* business logic; it delegates everything to
:mod:`bot.validators` and :mod:`bot.orders`.
"""

import argparse
import sys
from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm
from rich.table import Table
from rich.text import Text

from bot.logging_config import logger

# ---------------------------------------------------------------------------
# Module-level Rich console (stderr=False keeps it on stdout)
# ---------------------------------------------------------------------------
console = Console()

# ---------------------------------------------------------------------------
# Branding constants
# ---------------------------------------------------------------------------
APP_NAME: str = "Binance Futures Trading Bot"
APP_VERSION: str = "v1.0.0"
BANNER_COLOR: str = "bold cyan"
SUCCESS_COLOR: str = "bold green"
ERROR_COLOR: str = "bold red"
WARNING_COLOR: str = "bold yellow"
INFO_COLOR: str = "cyan"


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the ``argparse.ArgumentParser`` for the trading bot CLI.

    Returns:
        argparse.ArgumentParser: Fully configured parser.
    """
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description=(
            f"{APP_NAME} {APP_VERSION} — "
            "Place MARKET and LIMIT orders on Binance Futures Testnet."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001\n"
            "  python main.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000\n"
        ),
    )

    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol, e.g. BTCUSDT (required).",
    )
    parser.add_argument(
        "--side",
        type=str,
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        metavar="SIDE",
        help="Order side: BUY or SELL (required).",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        type=str,
        required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        metavar="TYPE",
        help="Order type: MARKET or LIMIT (required).",
    )
    parser.add_argument(
        "--quantity",
        type=float,
        required=True,
        metavar="QUANTITY",
        help="Order quantity in base asset units (required).",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        metavar="PRICE",
        help="Limit price (required for LIMIT orders, ignored for MARKET).",
    )

    return parser


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """
    Parse and return command-line arguments.

    Args:
        argv (Optional[list[str]]): Argument list; defaults to ``sys.argv[1:]``.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    return build_parser().parse_args(argv)


# ---------------------------------------------------------------------------
# Rich UI helpers
# ---------------------------------------------------------------------------


def print_banner() -> None:
    """Display a styled application banner in the terminal."""
    banner_text = Text(justify="center")
    banner_text.append(f" {APP_NAME} ", style=BANNER_COLOR)
    banner_text.append(f"{APP_VERSION}", style="dim cyan")
    console.print(Panel(banner_text, border_style="cyan", padding=(0, 2)))


def print_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> None:
    """
    Render a styled *Order Request* summary table.

    Args:
        symbol (str):            Trading pair.
        side (str):              Order side.
        order_type (str):        Order type.
        quantity (float):        Order quantity.
        price (Optional[float]): Limit price (``None`` for MARKET).
    """
    table = Table(
        title="ORDER REQUEST",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        title_style=BANNER_COLOR,
        show_header=True,
        header_style="bold white on dark_cyan",
        min_width=45,
    )
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="bold white", no_wrap=True)

    side_style = SUCCESS_COLOR if side == "BUY" else ERROR_COLOR
    price_display = f"${price:,.2f}" if price is not None else "— (MARKET)"

    table.add_row("Symbol", symbol)
    table.add_row("Side", Text(side, style=side_style))
    table.add_row("Order Type", order_type)
    table.add_row("Quantity", str(quantity))
    table.add_row("Price", price_display)

    console.print(table)
    console.print()


def confirm_order() -> bool:
    """
    Prompt the user to confirm before placing the order.

    Returns:
        bool: ``True`` if the user confirms, ``False`` otherwise.
    """
    return Confirm.ask(
        "[bold yellow]Proceed with placing this order?[/bold yellow]",
        default=True,
        console=console,
    )


def print_order_result(result: dict, success: bool = True) -> None:
    """
    Render a styled order result panel.

    Args:
        result (dict): Parsed order response from :func:`~bot.orders.place_order`.
        success (bool): Whether the order was placed successfully.
    """
    if success:
        title = "✅  ORDER PLACED SUCCESSFULLY"
        border = "green"
        status_style = SUCCESS_COLOR
        message = Text("Order placed successfully ✓", style=SUCCESS_COLOR)
    else:
        title = "❌  ORDER FAILED"
        border = "red"
        status_style = ERROR_COLOR
        message = Text("Order failed ✗", style=ERROR_COLOR)

    table = Table(
        title=title,
        box=box.DOUBLE_EDGE,
        border_style=border,
        title_style=f"bold {border}",
        show_header=True,
        header_style=f"bold white on {'dark_green' if success else 'dark_red'}",
        min_width=50,
    )
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="bold white", no_wrap=True)

    # Format average price
    avg_price = result.get("avg_price", "N/A")
    try:
        avg_price_display = f"${float(avg_price):,.4f}" if avg_price not in ("N/A", "0", "0.00") else "Pending / N/A"
    except (ValueError, TypeError):
        avg_price_display = str(avg_price)

    # Format executed quantity
    exec_qty = result.get("executed_qty", "N/A")

    table.add_row("Order ID", str(result.get("order_id", "N/A")))
    table.add_row("Status", Text(str(result.get("status", "N/A")), style=status_style))
    table.add_row("Executed Qty", str(exec_qty))
    table.add_row("Average Price", avg_price_display)
    table.add_row("", "")
    table.add_row("Message", message)

    console.print()
    console.print(table)
    console.print()


def print_error(message: str) -> None:
    """
    Display a user-friendly error panel in the terminal.

    Args:
        message (str): The error message to display.
    """
    console.print(
        Panel(
            f"[{ERROR_COLOR}]{message}[/{ERROR_COLOR}]",
            title="[bold red]ERROR[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
    )
    logger.error("User-facing error displayed: %s", message)


def print_warning(message: str) -> None:
    """
    Display a styled warning message in the terminal.

    Args:
        message (str): The warning message to display.
    """
    console.print(f"[{WARNING_COLOR}]⚠  {message}[/{WARNING_COLOR}]")


def run_with_spinner(description: str):
    """
    Return a Rich :class:`~rich.progress.Progress` context manager configured
    with a spinner, useful for wrapping API calls.

    Usage::

        with run_with_spinner("Contacting Binance …") as progress:
            task = progress.add_task(description)
            result = api_call()
            progress.update(task, completed=True)

    Args:
        description (str): Text shown next to the spinner.

    Returns:
        Progress: Configured Rich ``Progress`` context manager.
    """
    return Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )

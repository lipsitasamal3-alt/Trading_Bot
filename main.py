"""
main.py
=======
Entry point for the Binance Futures Trading Bot.

Execution flow
--------------
1. Parse CLI arguments.
2. Display the application banner.
3. Validate all order parameters.
4. Show an *Order Request* summary and ask for confirmation.
5. Contact Binance Futures Testnet (with a progress spinner).
6. Display the order result or a user-friendly error panel.

No internal tracebacks are ever shown to the user; all exceptions are caught
here and presented as clean error panels via :mod:`bot.cli`.

Usage
-----
::

    python main.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    python main.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
"""

import sys

from bot.cli import (
    confirm_order,
    parse_args,
    print_banner,
    print_error,
    print_order_request,
    print_order_result,
    run_with_spinner,
    console,
)
from bot.client import get_client
from bot.logging_config import logger
from bot.orders import NetworkError, OrderError, place_order
from bot.validators import validate_all


def main() -> None:
    """
    Orchestrate the full order-placement workflow.

    This is the sole entry point called by ``__main__``.  It catches every
    exception category, logs the details, and shows the user a friendly
    message — never a raw traceback.
    """
    # ------------------------------------------------------------------
    # 1. Parse arguments
    # ------------------------------------------------------------------
    args = parse_args()
    logger.debug(
        "CLI args — symbol=%s side=%s type=%s qty=%s price=%s",
        args.symbol,
        args.side,
        args.order_type,
        args.quantity,
        args.price,
    )

    # ------------------------------------------------------------------
    # 2. Banner
    # ------------------------------------------------------------------
    print_banner()

    # ------------------------------------------------------------------
    # 3. Validate inputs
    # ------------------------------------------------------------------
    try:
        params = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValueError as exc:
        print_error(str(exc))
        logger.warning("Order aborted due to validation error: %s", exc)
        sys.exit(1)

    # ------------------------------------------------------------------
    # 4. Display order request summary & confirmation
    # ------------------------------------------------------------------
    print_order_request(
        symbol=params["symbol"],
        side=params["side"],
        order_type=params["order_type"],
        quantity=params["quantity"],
        price=params["price"],
    )

    if not confirm_order():
        console.print("\n[bold yellow]Order cancelled by user.[/bold yellow]\n")
        logger.info("Order cancelled by user at confirmation prompt.")
        sys.exit(0)

    # ------------------------------------------------------------------
    # 5. Initialise client (with spinner)
    # ------------------------------------------------------------------
    try:
        with run_with_spinner("Connecting to Binance Futures Testnet …") as progress:
            task = progress.add_task("Connecting to Binance Futures Testnet …")
            client = get_client()
            progress.update(task, completed=True)
    except EnvironmentError as exc:
        print_error(str(exc))
        logger.error("Environment configuration error: %s", exc)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print_error(
            f"Failed to connect to Binance Futures Testnet: {exc}\n"
            "Check your API credentials and internet connection."
        )
        logger.exception("Unexpected error during client initialisation: %s", exc)
        sys.exit(1)

    # ------------------------------------------------------------------
    # 6. Place order (with spinner)
    # ------------------------------------------------------------------
    try:
        with run_with_spinner("Placing order on Binance Futures Testnet …") as progress:
            task = progress.add_task("Placing order on Binance Futures Testnet …")
            result = place_order(
                client=client,
                symbol=params["symbol"],
                side=params["side"],
                order_type=params["order_type"],
                quantity=params["quantity"],
                price=params["price"],
            )
            progress.update(task, completed=True)

        print_order_result(result, success=True)

    except OrderError as exc:
        print_error(str(exc))
        logger.error("Order placement failed (OrderError): %s", exc)
        print_order_result(
            {
                "order_id": "N/A",
                "status": "FAILED",
                "executed_qty": "0",
                "avg_price": "N/A",
            },
            success=False,
        )
        sys.exit(1)

    except NetworkError as exc:
        print_error(str(exc))
        logger.error("Network failure during order placement: %s", exc)
        sys.exit(1)

    except Exception as exc:  # noqa: BLE001
        print_error(f"An unexpected error occurred: {exc}")
        logger.exception("Unhandled exception in main: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()

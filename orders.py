"""
orders.py
=========
Order placement and result formatting for Binance Futures Testnet.

This module exposes a single public entry point — :func:`place_order` — which
handles both MARKET and LIMIT orders.  All Binance-specific exceptions are
caught here and re-raised as typed application exceptions so that the CLI
layer never needs to import ``binance`` directly.
"""

from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from bot.logging_config import logger

# ---------------------------------------------------------------------------
# Custom application-level exceptions
# ---------------------------------------------------------------------------


class OrderError(Exception):
    """Raised when an order cannot be placed due to a known API error."""


class NetworkError(Exception):
    """Raised when a network-level failure prevents order placement."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_futures_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> dict:
    """
    Build the keyword-argument dictionary for a Futures order.

    Args:
        symbol (str):            Trading pair (e.g. ``"BTCUSDT"``).
        side (str):              ``"BUY"`` or ``"SELL"``.
        order_type (str):        ``"MARKET"`` or ``"LIMIT"``.
        quantity (float):        Order size.
        price (Optional[float]): Limit price; ``None`` for MARKET orders.

    Returns:
        dict: Parameters ready to be passed to
              :meth:`~binance.client.Client.futures_create_order`.
    """
    params: dict = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"  # Good-Till-Cancelled

    logger.debug("Order params built: %s", params)
    return params


def _parse_response(response: dict) -> dict:
    """
    Extract and normalise the fields of interest from a Binance order response.

    Args:
        response (dict): Raw JSON response from the Binance Futures API.

    Returns:
        dict: A cleaned dictionary with keys:
              ``order_id``, ``status``, ``executed_qty``, ``avg_price``,
              ``symbol``, ``side``, ``type``, ``orig_qty``.
    """
    return {
        "order_id": response.get("orderId", "N/A"),
        "status": response.get("status", "N/A"),
        "executed_qty": response.get("executedQty", "0"),
        "avg_price": response.get("avgPrice", "N/A"),
        "symbol": response.get("symbol", "N/A"),
        "side": response.get("side", "N/A"),
        "type": response.get("type", "N/A"),
        "orig_qty": response.get("origQty", "N/A"),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def place_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> dict:
    """
    Place a MARKET or LIMIT order on Binance Futures Testnet.

    Args:
        client (Client):         Authenticated Binance client.
        symbol (str):            Trading pair (e.g. ``"BTCUSDT"``).
        side (str):              ``"BUY"`` or ``"SELL"``.
        order_type (str):        ``"MARKET"`` or ``"LIMIT"``.
        quantity (float):        Order size in base asset units.
        price (Optional[float]): Limit price (required for LIMIT orders).

    Returns:
        dict: Parsed order response — see :func:`_parse_response`.

    Raises:
        OrderError:   On a Binance API or order-specific error.
        NetworkError: On a connection or timeout failure.
    """
    params = _build_futures_order_params(symbol, side, order_type, quantity, price)

    logger.info(
        "Sending order request — symbol=%s side=%s type=%s qty=%s price=%s",
        symbol,
        side,
        order_type,
        quantity,
        price,
    )

    try:
        raw_response: dict = client.futures_create_order(**params)
    except BinanceOrderException as exc:
        logger.error(
            "BinanceOrderException — code=%s message=%s params=%s",
            exc.code,
            exc.message,
            params,
        )
        raise OrderError(
            f"Order rejected by Binance (code {exc.code}): {exc.message}"
        ) from exc
    except BinanceAPIException as exc:
        logger.error(
            "BinanceAPIException — status=%s code=%s message=%s",
            exc.status_code,
            exc.code,
            exc.message,
        )
        # Surface specific, user-friendly messages for common errors
        if exc.status_code == 401:
            raise OrderError(
                "Authentication failed. Please check your API key and secret."
            ) from exc
        if exc.code == -1121:
            raise OrderError(
                f"Invalid symbol '{symbol}'. "
                "Verify the symbol exists on Binance Futures Testnet."
            ) from exc
        raise OrderError(
            f"Binance API error (HTTP {exc.status_code}, code {exc.code}): "
            f"{exc.message}"
        ) from exc
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network error while placing order: %s", exc)
        raise NetworkError(
            "Could not reach Binance Futures Testnet. "
            "Check your internet connection and try again."
        ) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error while placing order: %s", exc)
        raise NetworkError(
            f"An unexpected error occurred: {exc}"
        ) from exc

    parsed = _parse_response(raw_response)
    logger.info(
        "Order placed successfully — order_id=%s status=%s executed_qty=%s avg_price=%s",
        parsed["order_id"],
        parsed["status"],
        parsed["executed_qty"],
        parsed["avg_price"],
    )
    logger.debug("Full API response: %s", raw_response)

    return parsed

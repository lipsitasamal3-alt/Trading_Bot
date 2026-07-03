"""
client.py
=========
Binance Futures Testnet API client wrapper.

Responsibilities:
    - Load API credentials from environment variables
    - Instantiate and configure the ``python-binance`` ``Client``
      pointing at the Futures Testnet base URL
    - Provide a singleton accessor so the client is created only once
    - Perform a lightweight connectivity check on startup

Environment variables (loaded via python-dotenv):
    BINANCE_API_KEY    — Futures Testnet API key
    BINANCE_API_SECRET — Futures Testnet API secret
"""

import os
from functools import lru_cache

from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

from bot.logging_config import logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FUTURES_TESTNET_BASE_URL: str = "https://testnet.binancefuture.com"
FUTURES_TESTNET_STREAM_URL: str = "wss://stream.binancefuture.com"


def _load_credentials() -> tuple[str, str]:
    """
    Load API credentials from the ``.env`` file.

    Returns:
        tuple[str, str]: A ``(api_key, api_secret)`` pair.

    Raises:
        EnvironmentError: If either environment variable is missing or empty.
    """
    load_dotenv()

    api_key: str = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret: str = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key:
        raise EnvironmentError(
            "BINANCE_API_KEY is not set. "
            "Please add it to your .env file."
        )
    if not api_secret:
        raise EnvironmentError(
            "BINANCE_API_SECRET is not set. "
            "Please add it to your .env file."
        )

    logger.debug("API credentials loaded successfully.")
    return api_key, api_secret


@lru_cache(maxsize=1)
def get_client() -> Client:
    """
    Create (or return the cached) Binance Futures Testnet client.

    The client is configured to use the Futures Testnet REST and WebSocket
    endpoints.  A single server-time synchronisation call is made to verify
    connectivity and that the credentials are valid.

    Returns:
        Client: A fully initialised ``python-binance`` ``Client`` instance.

    Raises:
        EnvironmentError:    If API credentials are missing.
        BinanceAPIException: If authentication fails.
        ConnectionError:     If the Testnet is unreachable.
    """
    api_key, api_secret = _load_credentials()

    logger.info("Initialising Binance Futures Testnet client …")

    client = Client(
        api_key=api_key,
        api_secret=api_secret,
        testnet=True,
    )

    # Override base URLs to target the Futures Testnet explicitly
    client.FUTURES_URL = f"{FUTURES_TESTNET_BASE_URL}/fapi"
    client.FUTURES_TESTNET_URL = f"{FUTURES_TESTNET_BASE_URL}/fapi"

    # Connectivity / auth check — fetch server time
    try:
        server_time = client.futures_time()
        logger.info(
            "Connected to Binance Futures Testnet. Server time: %s",
            server_time.get("serverTime"),
        )
    except BinanceAPIException as exc:
        logger.error(
            "Authentication / connectivity check failed: %s (code=%s)",
            exc.message,
            exc.status_code,
        )
        raise

    return client

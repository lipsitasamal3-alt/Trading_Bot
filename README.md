# 📈 Binance Futures Trading Bot

A professional, production-grade Python trading bot for **Binance Futures Testnet (USDT-M)**.  
Place MARKET and LIMIT orders directly from the command line with rich terminal output, robust validation, and structured logging.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔗 **Testnet Connection** | Connects exclusively to `https://testnet.binancefuture.com` |
| 🔐 **Secure Auth** | API credentials stored in `.env`, never hard-coded |
| 📊 **MARKET Orders** | Instant execution at best available price |
| 📉 **LIMIT Orders** | Placed at a specified price with GTC time-in-force |
| ↕️ **BUY / SELL** | Full support for both order sides |
| ✅ **Input Validation** | Comprehensive pre-flight checks with clear error messages |
| 🎨 **Rich Terminal UI** | Coloured panels, styled tables, progress spinners |
| ❓ **Confirmation Prompt** | Interactive confirmation before order placement |
| 📝 **Structured Logging** | Timestamped file logs with rotation (10 MB / 5 backups) |
| 🛡️ **Error Handling** | All Binance exceptions caught; no raw tracebacks shown |
| 🐍 **Python 3.11+** | Full type hints, PEP 8 compliant, modular architecture |

---

## 📁 Project Structure

```
trading_bot/
│
├── bot/
│   ├── __init__.py          # Package metadata
│   ├── client.py            # Binance client factory & credential loading
│   ├── orders.py            # Order placement logic & custom exceptions
│   ├── validators.py        # Input validation utilities
│   ├── logging_config.py    # Rotating file + console logging setup
│   └── cli.py               # argparse + Rich terminal UI components
│
├── logs/
│   └── trading_bot.log      # Auto-created on first run
│
├── .env.example             # Template — copy to .env and fill in keys
├── .gitignore
├── main.py                  # Entry point — run this file
├── requirements.txt
└── README.md
```

---

## 🛠️ Installation

### Prerequisites

- Python **3.11** or higher
- `pip` (bundled with Python)
- An active internet connection

### Steps

```bash
# 1. Clone or download the project
git clone <repo-url>
cd trading_bot

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt
```

---

## 🔑 Creating a Binance Futures Testnet Account & API Keys

### Step 1 — Register on Binance Futures Testnet

1. Open [https://testnet.binancefuture.com](https://testnet.binancefuture.com) in your browser.
2. Click **"Log In"** → authenticate with your **GitHub account** (no credit card or KYC required).
3. You will be automatically credited with test USDT funds.

### Step 2 — Generate API Keys

1. After logging in, locate the **"API Key"** tab at the top of the dashboard.
2. Click **"Generate Key"**.
3. Binance will immediately display your **API Key** and **Secret Key**.

> ⚠️ **Important:** Copy both keys now — the Secret Key is shown only once.

---

## ⚙️ Setting Up `.env`

```bash
# Copy the template
cp .env.example .env
```

Open `.env` in a text editor and replace the placeholder values:

```env
BINANCE_API_KEY=paste_your_api_key_here
BINANCE_API_SECRET=paste_your_secret_key_here
```

> 🔒 The `.env` file is already listed in `.gitignore` — it will never be committed.

---

## 🚀 Running the Bot

### MARKET Order — BUY

```bash
python main.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### MARKET Order — SELL

```bash
python main.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### LIMIT Order — BUY

```bash
python main.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 60000
```

### LIMIT Order — SELL

```bash
python main.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

### ETHUSDT MARKET Order

```bash
python main.py --symbol ETHUSDT --side BUY --type MARKET --quantity 0.01
```

---

## 📋 CLI Reference

```
usage: trading_bot [-h] --symbol SYMBOL --side SIDE --type TYPE
                   --quantity QUANTITY [--price PRICE]

Arguments:
  --symbol    SYMBOL    Trading pair symbol, e.g. BTCUSDT (required)
  --side      SIDE      Order side: BUY or SELL (required)
  --type      TYPE      Order type: MARKET or LIMIT (required)
  --quantity  QUANTITY  Order quantity in base asset units (required)
  --price     PRICE     Limit price (required for LIMIT, ignored for MARKET)
```

---

## 🖥️ Terminal Output

When you run the bot, you will see:

1. **Application banner** — branded header
2. **Order Request table** — all parameters displayed before submission
3. **Confirmation prompt** — `Proceed? [Y/n]`
4. **Progress spinner** — while connecting to Binance
5. **Order Result table** — Order ID, Status, Executed Qty, Avg Price

**Example output (MARKET BUY):**

```
╔══════════════════════════════════════════╗
║      Binance Futures Trading Bot v1.0.0  ║
╚══════════════════════════════════════════╝

╔══════════════ ORDER REQUEST ══════════════╗
║ Field        │ Value                      ║
║──────────────│────────────────────────────║
║ Symbol       │ BTCUSDT                    ║
║ Side         │ BUY                        ║
║ Order Type   │ MARKET                     ║
║ Quantity     │ 0.001                      ║
║ Price        │ — (MARKET)                 ║
╚═══════════════════════════════════════════╝

Proceed with placing this order? [Y/n]: y

⠋ Connecting to Binance Futures Testnet …   0:00:01
⠙ Placing order on Binance Futures Testnet … 0:00:00

╔════════ ✅  ORDER PLACED SUCCESSFULLY ════════╗
║ Field          │ Value                        ║
║────────────────│──────────────────────────────║
║ Order ID       │ 3847201938                   ║
║ Status         │ FILLED                       ║
║ Executed Qty   │ 0.001                        ║
║ Average Price  │ $62,345.1000                 ║
║                │                              ║
║ Message        │ Order placed successfully ✓  ║
╚══════════════════════════════════════════════╝
```

---

## 📝 Logging

All activity is logged to `logs/trading_bot.log`.

### Log Format

```
2025-01-15 14:23:01 | INFO     | trading_bot.client       | get_client               | Connected to Binance Futures Testnet. Server time: 1736950981000
2025-01-15 14:23:02 | INFO     | trading_bot.orders       | place_order              | Sending order request — symbol=BTCUSDT side=BUY type=MARKET qty=0.001 price=None
2025-01-15 14:23:02 | INFO     | trading_bot.orders       | place_order              | Order placed successfully — order_id=3847201938 status=FILLED executed_qty=0.001 avg_price=62345.1
```

### What Is Logged

| Level | Events |
|---|---|
| `DEBUG` | Validated params, full API responses, internal state |
| `INFO` | Client init, order requests, successful order placement |
| `WARNING` | Validation failures, user-facing warnings |
| `ERROR` | API errors, network failures, authentication issues |

Log files rotate automatically at **10 MB** with **5 backups** retained.

---

## 🧪 Testing Both Order Types (Step-by-Step)

Follow these steps to generate a complete `trading_bot.log` covering all scenarios.

### Setup

```bash
# Ensure your .env is populated with Testnet keys
# Activate your virtual environment
pip install -r requirements.txt
```

### Test 1 — MARKET BUY

```bash
python main.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```
→ Confirm with `Y`.  
✔ Expected: Status `FILLED`, Executed Qty `0.001`, Average Price populated.

### Test 2 — MARKET SELL

```bash
python main.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```
→ Confirm with `Y`.  
✔ Expected: Status `FILLED`.

### Test 3 — LIMIT BUY (below market)

```bash
python main.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
```
→ Confirm with `Y`.  
✔ Expected: Status `NEW` (resting in order book because price is below market).

### Test 4 — LIMIT SELL (above market)

```bash
python main.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000
```
→ Confirm with `Y`.  
✔ Expected: Status `NEW` (resting in order book).

### Test 5 — Validation Error (missing price for LIMIT)

```bash
python main.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001
```
✔ Expected: Red error panel — `Price is required for LIMIT orders.`

### Test 6 — Cancel at Confirmation

```bash
python main.py --symbol ETHUSDT --side BUY --type MARKET --quantity 0.01
```
→ When prompted, type `N`.  
✔ Expected: `Order cancelled by user.`

After all tests, review the log:

```bash
# Windows
type logs\trading_bot.log

# macOS / Linux
cat logs/trading_bot.log
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `BINANCE_API_KEY is not set` | Ensure `.env` exists with valid keys |
| `Authentication failed` | Re-generate keys on the Testnet dashboard |
| `Invalid symbol` | Use a valid Futures pair (e.g. `BTCUSDT`, `ETHUSDT`) |
| `Margin insufficient` | Check your Testnet balance; request more test funds |
| `Connection error` | Check internet; Testnet may be under maintenance |
| `Order minimum not met` | Increase quantity (BTC min is typically 0.001) |

---

## 📌 Assumptions

1. All orders target **USDT-M Futures Testnet** — not Spot or Coin-M.
2. `timeInForce` for LIMIT orders is set to **GTC** (Good-Till-Cancelled).
3. The bot places orders in **one-way position mode** (Testnet default).
4. No trailing stops, OCO, or bracket orders are implemented in this version.
5. Quantity precision follows Binance's symbol filters; users must supply valid values.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `python-binance` | 1.0.19 | Binance REST API client |
| `python-dotenv` | 1.0.1 | `.env` file loader |
| `rich` | 13.9.4 | Terminal colours, tables, spinners |
| `requests` | 2.32.3 | HTTP transport (used by python-binance) |

---

## 📄 License

This project is provided for educational purposes as part of an internship assignment.  
Do **not** use with real funds or on Binance Mainnet without thorough testing and risk review.

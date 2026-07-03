
# Binance Futures Trading Bot

## Overview

This project is a Python-based trading bot developed as part of the Primetrade.ai Python Developer internship assignment.

The application interacts with the Binance Futures Testnet API to place MARKET and LIMIT orders through a command-line interface. The project follows a modular architecture with separate components for API communication, order handling, validation, logging, and CLI operations.

---

## Features

- Place MARKET orders
- Place LIMIT orders
- Supports BUY and SELL orders
- Command-line interface using argparse
- Input validation
- Structured logging
- Exception handling
- Modular and reusable code

---

## Project Structure

```
Trading_Bot/
│
├── bot/
│   ├── client.py
│   ├── orders.py
│   ├── validators.py
│   ├── logging_config.py
│   └── cli.py
│
├── logs/
├── main.py
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

---

## Installation

Clone the repository:

```bash
git clone <your-github-repository-url>
cd Trading_Bot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_secret_key
```

---

## Running the Application

Market Order

```bash
python main.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Limit Order

```bash
python main.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

---

## Logging

The application records:

- API requests
- API responses
- Validation errors
- Network errors
- Exceptions

Logs are stored inside the `logs` directory.

---

## Technologies Used

- Python 3
- python-binance
- Rich
- argparse
- logging
- python-dotenv

---

## Note

Due to Binance's current account verification (KYC) requirements in my region, I was unable to generate Binance Futures Testnet API credentials. As a result, I could not execute live testnet orders or generate the requested order log files.

The application has been fully implemented and is ready to run with valid Binance Futures Testnet API credentials.

---

## Author

Lipsita Samal

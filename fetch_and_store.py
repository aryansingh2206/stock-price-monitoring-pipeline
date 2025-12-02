#!/usr/bin/env python3
"""
Fetch stock prices for tickers, store in SQLite, alert on big moves.
Assumption: Alert if (current_price - previous_close) / previous_close * 100 >= threshold.
"""

import os
import time
from datetime import datetime
import json
import smtplib
from email.message import EmailMessage

import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./stocks.db")
TICKERS = [t.strip().upper() for t in os.getenv("TICKERS", "AAPL,MSFT,GOOGL,AMZN,TSLA").split(",")]
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "3.0"))

# Email config
SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "")
SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587") or 587)
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}, echo=False)

def ensure_schema():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS prices (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ticker TEXT NOT NULL,
          fetched_at TIMESTAMP NOT NULL,
          price REAL NOT NULL,
          previous_close REAL,
          pct_change REAL,
          volume INTEGER,
          raw_json TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS summary_24h (
          ticker TEXT PRIMARY KEY,
          first_price REAL,
          last_price REAL,
          min_price REAL,
          max_price REAL,
          avg_price REAL,
          pct_change_24h REAL,
          last_updated TIMESTAMP
        );
        """))

def fetch_ticker_data(ticker):
    tk = yf.Ticker(ticker)
    info = tk.history(period="1d", interval="1m", actions=False)
    if info.empty:
        info2 = tk.info
        price = info2.get("regularMarketPrice") or info2.get("previousClose")
        prev_close = info2.get("previousClose")
        volume = info2.get("volume")
    else:
        last_row = info.iloc[-1]
        price = float(last_row["Close"])
        prev_close = tk.info.get("previousClose")
        volume = int(last_row.get("Volume", 0))
    return {
        "price": price,
        "previous_close": float(prev_close) if prev_close is not None else None,
        "volume": int(volume) if volume is not None else None,
        "raw_json": {}
    }

def send_email(subject, body):
    if not SMTP_HOST or not EMAIL_FROM or not EMAIL_TO:
        print("Email not configured, printing alert instead.")
        print(subject)
        print(body)
        return

    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        if EMAIL_USER and EMAIL_PASS:
            smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print("Email sent:", subject)

def process_and_store(ticker, data):
    price = data["price"]
    prev_close = data["previous_close"]
    volume = data["volume"]
    pct_change = None
    if prev_close and prev_close != 0:
        pct_change = (price - prev_close) / prev_close * 100.0

    now = datetime.utcnow()

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO prices (ticker, fetched_at, price, previous_close, pct_change, volume, raw_json)
            VALUES (:ticker, :fetched_at, :price, :previous_close, :pct_change, :volume, :raw_json)
        """), {
            "ticker": ticker,
            "fetched_at": now,
            "price": price,
            "previous_close": prev_close,
            "pct_change": pct_change,
            "volume": volume,
            "raw_json": json.dumps(data["raw_json"])
        })

    return pct_change

def check_and_alert(ticker, pct_change, price, prev_close):
    if pct_change is None:
        return
    thr = ALERT_THRESHOLD
    if abs(pct_change) >= thr:
        subj = f"ALERT {ticker}: {pct_change:.2f}% move"
        body = f"{ticker} moved {pct_change:.2f}% vs previous close.\nPrice: {price}\nPrev Close: {prev_close}\nTime: {datetime.utcnow().isoformat()} UTC"
        send_email(subj, body)

def main():
    ensure_schema()
    for t in TICKERS:
        try:
            data = fetch_ticker_data(t)
            pct = process_and_store(t, data)
            check_and_alert(t, pct, data["price"], data["previous_close"])
            time.sleep(1)
        except Exception as e:
            print(f"Error for {t}: {e}")

if __name__ == "__main__":
    main()

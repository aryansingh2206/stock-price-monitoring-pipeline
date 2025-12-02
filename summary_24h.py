#!/usr/bin/env python3
"""
Compute summary stats for last 24 hours and update summary_24h table
and/or print a quick console report.
"""

import os
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "./stocks.db")
TICKERS = [t.strip().upper() for t in os.getenv("TICKERS", "AAPL,MSFT,GOOGL,AMZN,TSLA").split(",")]

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}, echo=False)

def summary_for_ticker(conn, ticker):
    since = datetime.utcnow() - timedelta(hours=24)
    df = pd.read_sql(text("SELECT fetched_at, price FROM prices WHERE ticker = :ticker AND fetched_at >= :since ORDER BY fetched_at"),
                     conn, params={"ticker": ticker, "since": since})
    if df.empty:
        return None
    df['fetched_at'] = pd.to_datetime(df['fetched_at'])
    first_price = float(df.iloc[0]['price'])
    last_price = float(df.iloc[-1]['price'])
    min_price = float(df['price'].min())
    max_price = float(df['price'].max())
    avg_price = float(df['price'].mean())
    pct_change_24h = (last_price - first_price) / first_price * 100.0 if first_price != 0 else None
    return {
        "ticker": ticker,
        "first_price": first_price,
        "last_price": last_price,
        "min_price": min_price,
        "max_price": max_price,
        "avg_price": avg_price,
        "pct_change_24h": pct_change_24h,
        "last_updated": datetime.utcnow(),
    }

def upsert_summary(conn, s):
    conn.execute(text("""
    INSERT INTO summary_24h (ticker, first_price, last_price, min_price, max_price, avg_price, pct_change_24h, last_updated)
    VALUES (:ticker, :first_price, :last_price, :min_price, :max_price, :avg_price, :pct_change_24h, :last_updated)
    ON CONFLICT(ticker) DO UPDATE SET
      first_price = excluded.first_price,
      last_price = excluded.last_price,
      min_price = excluded.min_price,
      max_price = excluded.max_price,
      avg_price = excluded.avg_price,
      pct_change_24h = excluded.pct_change_24h,
      last_updated = excluded.last_updated
    """), s)

def main():
    with engine.begin() as conn:
        for t in TICKERS:
            s = summary_for_ticker(conn, t)
            if s:
                upsert_summary(conn, s)
                print(f"{t}: {s['first_price']:.2f} -> {s['last_price']:.2f} ({s['pct_change_24h']:.2f}%)")
            else:
                print(f"{t}: no data in last 24h")

if __name__ == "__main__":
    main()

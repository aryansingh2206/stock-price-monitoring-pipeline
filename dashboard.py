import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

DB_PATH = "stocks.db"

st.set_page_config(page_title="Stock Monitor Dashboard", layout="wide")

st.title("📊 Real-Time Stock Monitoring Dashboard")

conn = sqlite3.connect(DB_PATH)

# === Sidebar ===
tickers = pd.read_sql("SELECT DISTINCT ticker FROM prices", conn)["ticker"].tolist()
selected = st.sidebar.multiselect("Select Tickers", tickers, default=tickers)

hours = st.sidebar.slider("Show last N hours", 1, 48, 24)

since = datetime.utcnow() - timedelta(hours=hours)

# === Main Charts ===
for ticker in selected:
    df = pd.read_sql(
        "SELECT fetched_at, price FROM prices WHERE ticker=? AND fetched_at >= ? ORDER BY fetched_at",
        conn,
        params=[ticker, since],
        parse_dates=['fetched_at']
    )

    if df.empty:
        st.warning(f"No data for {ticker}")
        continue

    st.subheader(f"📈 {ticker} Price Movement (Last {hours} hours)")

    fig, ax = plt.subplots()
    ax.plot(df["fetched_at"], df["price"])
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.grid(True)

    st.pyplot(fig)

# === Summary Table ===
st.header("📋 24-Hour Summary")

summary_df = pd.read_sql("SELECT * FROM summary_24h", conn)
st.dataframe(summary_df)

conn.close()

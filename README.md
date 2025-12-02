
# 📈 Stock Monitoring Pipeline

A lightweight, real-time stock monitoring system that fetches live prices every 5 minutes, stores historical snapshots in SQLite, and generates alerts when prices move more than a configurable threshold (default: 3%).  
Includes a Streamlit dashboard to visualize trends and analyze 24-hour summaries.  

Built using **Python**, **yfinance**, **Pandas**, **SQLite**, and **Task Scheduler/Cron**.

---

## 🚀 Features

### ✔ Automated Data Fetching (Every 5 Minutes)
- Fetches stock prices for selected tickers via `yfinance`
- Records price, volume, and percentage change
- Stores snapshots in a persistent SQLite database

### ✔ Alerting System
- Triggers console alerts when price movement exceeds ±3% vs previous close
- Optional email alerts using SMTP credentials

### ✔ Streamlit Dashboard
- Interactive charts showing price movement over the last N hours
- Live data pulled directly from SQLite
- 24-hour summary table with min/max/avg/change

### ✔ SQLite Storage
- Historical `prices` table  
- Materialized `summary_24h` table  
- Easy inspection via SQLite browser or VS Code

---

## 🛠 Tech Stack

- **Python 3**
- **yfinance API**
- **Pandas**
- **SQLite**
- **SQLAlchemy**
- **Streamlit**
- **Task Scheduler (Windows) / Cron (Linux/Mac)**

---

## 📁 Project Structure

```

stock-monitor/
│
├── fetch_and_store.py       # Fetches prices, stores rows, triggers alerts
├── summary_24h.py           # Generates 24-hour summary stats
├── dashboard.py             # Streamlit dashboard UI
│
├── stocks.db                # SQLite database (auto-created)
│
├── requirements.txt
├── .env.example
├── .env                     # Your config (not committed)
├── run_fetch.bat            # Windows scheduled task launcher
│
└── README.md

```

---

## ⚙️ Setup & Installation

### 1. Clone repo
```

git clone [https://github.com/yourusername/stock-monitor.git](https://github.com/yourusername/stock-monitor.git)
cd stock-monitor

```

### 2. Create a virtual environment
Windows:
```

python -m venv venv
.\venv\Scripts\Activate.ps1

```

Linux/Mac:
```

python3 -m venv venv
source venv/bin/activate

```

### 3. Install dependencies
```

pip install -r requirements.txt

```

### 4. Configure environment variables  
Copy:
```

cp .env.example .env   # or create manually

```

Edit `.env` with your tickers, alert threshold, and optional email credentials.

---

## ▶️ Running the Project

### Manual fetch
```

python fetch_and_store.py

```

### Generate 24-hour summary
```

python summary_24h.py

```

### Launch Dashboard (Highly Recommended)
```

streamlit run dashboard.py

```

---

## ⏱️ Scheduling the Fetch Script (Windows Task Scheduler)

1. Create a file `run_fetch.bat`:
```

@echo off
cd /d C:\Users\aryan\stock-monitor
C:\Users\aryan\stock-monitor\venv\Scripts\python.exe fetch_and_store.py

```

2. Open **Task Scheduler → Create Task**

3. Trigger:
- Repeat every **5 minutes**
- Indefinitely

4. Action:
- Start Program → `run_fetch.bat`

This ensures price fetching runs **24/7 automatically**.

---

## 📊 Dashboard Preview

- Line charts showing last N-hours price movement  
- Ticker-based filtering  
- Auto-generated summary table  
- Clean layout for recruiters & demos  

Run:
```

streamlit run dashboard.py

```

---

## 🧪 Sample Queries (SQLite)

```

SELECT * FROM prices ORDER BY fetched_at DESC LIMIT 10;
SELECT * FROM summary_24h;

```

---

## 🌟 Future Enhancements
- FastAPI service exposing `/latest` and `/summary`
- Docker container for deployment
- Grafana dashboard + Prometheus exporter
- Support for commodity/crypto tickers

---


---


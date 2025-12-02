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

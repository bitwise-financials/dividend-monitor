# <div style="display: flex; align-items: center; justify-content: center;"><img align="left" alt="Python Logo" width="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" /><span style="margin-left: 5px;">Dividend Monitoring & Alert System</span></div>

**An intelligent, automated system for real-time dividend monitoring — built for portfolio managers, analysts, and finance professionals.**

---

## Core Features

- <strong>Threshold Alerts</strong>  
  Instantly detects significant changes in quarterly dividends, which is triggered by both +20% and -20% changes, and notified via email.

- <strong>Custom Configuration</strong>  
  Set your own alert thresholds and tailor your watchlist to focus on key holdings

---

## 📁 Project Structure

```
dividend-monitor/
├── .github/
│   └── workflows/
│       └── dividend-monitor.yml
├── config/
│   └── tickers.txt
├── data/
│   └── dividends_data.json
├── check_dividends.py
├── requirements.txt
├── .gitignore
└── README.md
```
---

## ⚙️ Technical Architecture

```
Stock Watchlist
     ↓
Daily Dividend Scan
     ↓
Check for Change ≥ ±20%
     |
     ├── Yes → Trigger Alert → Send Email Notification
     |
     └── No  → Log the Data in JSON Database
```

- **Language:** Python 3.9  
- **Data Source:** Yahoo Finance API  
- **Automation:** GitHub Actions  
- **Storage:** Supabase  

---

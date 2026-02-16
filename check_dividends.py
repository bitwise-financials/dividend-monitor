#!/usr/bin/env python3
"""
Dividend Monitor - Checks stock dividends and sends email alerts
"""
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import yfinance as yf
from pathlib import Path

# Configuration
DATA_FILE = "data/dividends_data.json"
TICKERS_FILE = "config/tickers.txt"
ALERT_THRESHOLD = 0.20  # 20% change threshold


def load_tickers():
    """Load stock tickers from config file"""
    tickers_path = Path(TICKERS_FILE)
    if not tickers_path.exists():
        print(f"Warning: {TICKERS_FILE} not found. Creating empty file.")
        tickers_path.parent.mkdir(parents=True, exist_ok=True)
        tickers_path.write_text("AAPL\n")
        return ["AAPL"]
    
    with open(TICKERS_FILE, 'r') as f:
        tickers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return tickers


def load_stored_data():
    """Load previously stored dividend data"""
    data_path = Path(DATA_FILE)
    if not data_path.exists():
        print(f"No existing data file found. Creating new one at {DATA_FILE}")
        data_path.parent.mkdir(parents=True, exist_ok=True)
        return {}
    
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_stored_data(data):
    """Save dividend data to file"""
    Path(DATA_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {DATA_FILE}")


def fetch_dividends(ticker):
    """Fetch dividend data for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        dividends = stock.dividends.reset_index()
        
        if dividends.empty:
            print(f"No dividend data found for {ticker}")
            return None
        
        # Convert to list of dictionaries
        dividend_list = []
        for _, row in dividends.iterrows():
            dividend_list.append({
                'date': row['Date'].strftime('%Y-%m-%d'),
                'amount': float(row['Dividends'])
            })
        
        return dividend_list
    
    except Exception as e:
        print(f"Error fetching dividends for {ticker}: {str(e)}")
        return None


def check_for_alerts(ticker, stored_dividends, new_dividends):
    """
    Check if new dividends meet alert criteria
    Returns: (should_alert, alert_message)
    """
    if not new_dividends or len(new_dividends) < 2:
        return False, None
    
    # Get the latest dividend
    latest = new_dividends[-1]
    previous = new_dividends[-2]
    
    # Check if this is a new dividend (not in stored data)
    if stored_dividends:
        stored_dates = [d['date'] for d in stored_dividends]
        if latest['date'] in stored_dates:
            # Not a new dividend
            return False, None
    
    # Calculate percentage change
    latest_amount = latest['amount']
    previous_amount = previous['amount']
    
    if previous_amount == 0:
        return False, None
    
    change_pct = (latest_amount - previous_amount) / previous_amount
    
    # Check if change exceeds threshold
    if abs(change_pct) >= ALERT_THRESHOLD:
        direction = "increased" if change_pct > 0 else "decreased"
        alert_message = f"""
🚨 DIVIDEND ALERT for {ticker} 🚨

New Dividend Announced: ${latest_amount:.4f}
Previous Dividend: ${previous_amount:.4f}
Change: {change_pct*100:.2f}%

The dividend has {direction} by more than {ALERT_THRESHOLD*100:.0f}%.

Date: {latest['date']}

---
Dividend Monitor - GitHub Actions
        """
        return True, alert_message
    
    return False, None


def send_email_alert(subject, message):
    """Send email alert via Gmail"""
    # Get credentials from environment variables
    sender_email = os.environ.get('EMAIL_SENDER')
    sender_password = os.environ.get('EMAIL_PASSWORD')
    receiver_email = os.environ.get('EMAIL_RECEIVER')
    
    if not all([sender_email, sender_password, receiver_email]):
        print("ERROR: Email credentials not configured!")
        print("Please set EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECEIVER in GitHub Secrets")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        # Send email via Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email alert sent successfully to {receiver_email}")
        return True
    
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False


def main():
    """Main execution function"""
    print(f"=== Dividend Monitor Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    # Load configuration
    tickers = load_tickers()
    print(f"Monitoring {len(tickers)} stocks: {', '.join(tickers)}\n")
    
    # Load stored data
    stored_data = load_stored_data()
    
    alerts_sent = 0
    
    # Check each ticker
    for ticker in tickers:
        print(f"Checking {ticker}...")
        
        # Fetch current dividends
        new_dividends = fetch_dividends(ticker)
        
        if new_dividends is None:
            print(f"Skipping {ticker} due to fetch error\n")
            continue
        
        # Get stored dividends for this ticker
        stored_dividends = stored_data.get(ticker, [])
        
        # Check for alerts
        should_alert, alert_message = check_for_alerts(ticker, stored_dividends, new_dividends)
        
        if should_alert:
            print(f"🚨 ALERT CONDITION MET for {ticker}!")
            subject = f"Dividend Alert: {ticker} - Significant Change Detected"
            if send_email_alert(subject, alert_message):
                alerts_sent += 1
        else:
            print(f"No alert conditions met for {ticker}")
        
        # Update stored data (always update to latest)
        stored_data[ticker] = new_dividends
        print(f"Updated stored data for {ticker} ({len(new_dividends)} dividend records)\n")
    
    # Save updated data
    save_stored_data(stored_data)
    
    print(f"\n=== Dividend Monitor Completed ===")
    print(f"Total alerts sent: {alerts_sent}")
    print(f"Next check in 5 minutes...")


if __name__ == "__main__":
    main()

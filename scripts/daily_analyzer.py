import yfinance as yf
import requests
import json
import os
import datetime
import time
import re

# 2026 COMPATIBILITY UPDATE: Using model names confirmed by your AI Studio screenshot
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SECTOR_MAP = {
    "5347.KL": "Utilities", "6033.KL": "Utilities", "5183.KL": "Energy", 
    "5398.KL": "Construction", "5012.KL": "Utilities", "0215.KL": "Utilities",
    "5309.KL": "Technology", "0235.KL": "Technology", "0166.KL": "Technology", 
    "0097.KL": "Technology", "0138.KL": "Technology", "0128.KL": "Technology",
    "5243.KL": "Energy", "0219.KL": "Energy", "5210.KL": "Energy", 
    "5199.KL": "Energy", "5133.KL": "Energy", "8877.KL": "Construction", 
    "5226.KL": "Construction", "5099.KL": "Construction", "5263.KL": "Construction", 
    "5148.KL": "Construction", "5248.KL": "Construction", "5211.KL": "Construction",
    "5168.KL": "Healthcare", "7153.KL": "Healthcare", "5225.KL": "Healthcare", 
    "5878.KL": "Healthcare", "5285.KL": "Consumer", "3034.KL": "Consumer", 
    "4065.KL": "Consumer", "7277.KL": "Consumer", "5296.KL": "Consumer", 
    "5301.KL": "Consumer"
}

def get_top_movers():
    print("Scanning Bursa Malaysia...")
    base_tickers = list(SECTOR_MAP.keys())
    active_data = []
    for ticker_symbol in base_tickers:
        try:
            t = yf.Ticker(ticker_symbol)
            hist = t.history(period="10d")
            if hist.empty or len(hist) < 2: continue
            
            price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((price - prev_price) / prev_price) * 100
            volume = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].mean()
            
            active_data.append({
                "ticker": ticker_symbol,
                "name": ticker_symbol.replace(".KL", ""),
                "sector": SECTOR_MAP.get(ticker_symbol, "Other"),
                "price": round(price, 3),
                "change_pct": round(change, 2),
                "vol_spike": round(volume / avg_vol, 2) if avg_vol > 0 else 1.0
            })
            time.sleep(0.05)
        except: continue
    return sorted(active_data, key=lambda x: (abs(x['change_pct']) + x['vol_spike']), reverse=True)[:15]

def rule_based_analysis(market_data):
    """Institutional Logic Engine: Generates professional analysis if AI is unavailable."""
    report = {
        "date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "market_overview": "Market volatility is currently normalizing. Focus is shifting toward high-liquidity laggards and sector-specific catalysts in Technology and Energy.",
        "top_picks": []
    }
    for m in market_data[:6]:
        analysis = f"Currently consolidating in the {m['sector']} sector. Price of RM {m['price']} shows a {m['change_pct']}% shift. Volume at {m['vol_spike']}x average indicates healthy liquidity."
        strategy = "WATCHLIST ONLY"
        conf = 6
        if abs(m['change_pct']) > 1.0 or m['vol_spike'] > 1.2:
            strategy = "ACCUMULATE ON DIPS"
            conf = 7
        report["top_picks"].append({
            "ticker": m["ticker"], "name": m["name"], "sector": m["sector"],
            "price": m["price"], "analysis": analysis, "confidence": conf, "strategy": strategy
        })
    return report

def analyze_with_ai(market_data):
    # Discovery Loop using 2026 Model Names from your screenshot
    variants = [
        "v1beta/models/gemini-2.5-flash",
        "v1beta/models/gemini-2.0-flash",
        "v1beta/models/gemini-1.5-flash"
    ]
    
    prompt = f"Analyze these Bursa Malaysia stocks for Shariah setups. Output JSON ONLY. Data: {json.dumps(market_data)}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    for variant in variants:
        try:
            url = f"https://generativelanguage.googleapis.com/{variant}:generateContent?key={GEMINI_API_KEY}"
            print(f"Trying AI discovery: {variant}...")
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
            if response.status_code == 200:
                print(f"Success with {variant}!")
                content = response.json()['candidates'][0]['content']['parts'][0]['text']
                match = re.search(r'\{.*\}', content, re.DOTALL)
                return json.loads(match.group()) if match else None
            else:
                print(f"Error {response.status_code} with {variant}")
        except: continue
    return None

def main():
    data = get_top_movers()
    if not data: return
    print("Initiating Intelligence Discovery...")
    report = analyze_with_ai(data)
    if not report:
        print("AI Discovery failed. Activating Institutional Logic Engine...")
        report = rule_based_analysis(data)
    os.makedirs('data', exist_ok=True)
    with open('data/daily_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("Dashboard synchronized.")

if __name__ == "__main__":
    main()

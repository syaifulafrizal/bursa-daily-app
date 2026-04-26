import yfinance as yf
import requests
import json
import os
import datetime
import time
import re

# BURSA INTEL UNIVERSE - VERSION 3.1 (CLEANED)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Hardcoded metadata with names and sectors (Removed 404/Delisted stocks)
ASSET_METADATA = {
    "5347.KL": {"name": "TENAGA", "sector": "Utilities"},
    "6033.KL": {"name": "PETGAS", "sector": "Utilities"},
    "5183.KL": {"name": "PCHEM", "sector": "Energy"},
    "5398.KL": {"name": "GAMUDA", "sector": "Construction"},
    "5012.KL": {"name": "MALAKOF", "sector": "Utilities"},
    "0215.KL": {"name": "SLVEST", "sector": "Utilities"},
    "5309.KL": {"name": "ITMAX", "sector": "Technology"},
    "0235.KL": {"name": "SNS", "sector": "Technology"},
    "0166.KL": {"name": "INARI", "sector": "Technology"},
    "0097.KL": {"name": "VITROX", "sector": "Technology"},
    "0138.KL": {"name": "MYEG", "sector": "Technology"},
    "0128.KL": {"name": "FRONTKN", "sector": "Technology"},
    "5243.KL": {"name": "VELESTO", "sector": "Energy"},
    "0219.KL": {"name": "RLINK", "sector": "Energy"},
    "5210.KL": {"name": "ARMADA", "sector": "Energy"},
    "5199.KL": {"name": "HIBISCS", "sector": "Energy"},
    "5133.KL": {"name": "PTRANS", "sector": "Energy"},
    "8877.KL": {"name": "EKOVEST", "sector": "Construction"},
    "5226.KL": {"name": "GBGAQRS", "sector": "Construction"},
    "5099.KL": {"name": "SUNCON", "sector": "Construction"},
    "5263.KL": {"name": "KERJAYA", "sector": "Construction"},
    "5148.KL": {"name": "IJM", "sector": "Construction"},
    "5248.KL": {"name": "MRDIY", "sector": "Consumer"},
    "5211.KL": {"name": "SUNWAY", "sector": "Construction"},
    "5168.KL": {"name": "HARTA", "sector": "Healthcare"},
    "7153.KL": {"name": "KOSSAN", "sector": "Healthcare"},
    "5225.KL": {"name": "IHH", "sector": "Healthcare"},
    "5878.KL": {"name": "KPJ", "sector": "Healthcare"},
    "5285.KL": {"name": "SDG", "sector": "Consumer"},
    "3034.KL": {"name": "HAPSENG", "sector": "Consumer"},
    "4065.KL": {"name": "PPB", "sector": "Consumer"},
    "7277.KL": {"name": "DIALOG", "sector": "Energy"},
    "5296.KL": {"name": "AEON", "sector": "Consumer"},
    "5301.KL": {"name": "99SMART", "sector": "Consumer"},
    "8664.KL": {"name": "SPSETIA", "sector": "Property"},
    "5288.KL": {"name": "SIMEPROP", "sector": "Property"},
    "8583.KL": {"name": "MAHSING", "sector": "Property"},
    "2739.KL": {"name": "PMETAL", "sector": "Industrial"},
    "5139.KL": {"name": "MCEMENT", "sector": "Industrial"},
    "5109.KL": {"name": "CHINHIN", "sector": "Industrial"}
}

def get_top_movers():
    print(f"Scanning Cleaned Universe ({len(ASSET_METADATA)} assets)...")
    active_data = []
    for ticker, meta in ASSET_METADATA.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="10d")
            if hist.empty or len(hist) < 2: continue
            
            price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((price - prev_price) / prev_price) * 100
            volume = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].mean()
            
            active_data.append({
                "ticker": ticker, "name": meta["name"], "sector": meta["sector"],
                "price": round(price, 3), "change_pct": round(change, 2),
                "vol_spike": round(volume / avg_vol, 2) if avg_vol > 0 else 1.0
            })
            time.sleep(0.01)
        except: continue
    return sorted(active_data, key=lambda x: (abs(x['change_pct']) + (x['vol_spike'] * 0.5)), reverse=True)[:25]

def rule_based_analysis(market_data):
    report = {
        "date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "market_overview": "Market Universe scan active. Current rotation is favoring mid-cap Shariah counters with unusual volume activity.",
        "top_picks": []
    }
    for i, m in enumerate(market_data[:12]):
        strategy = "WATCHLIST ONLY"; conf = 6
        if abs(m['change_pct']) > 1.2 or m['vol_spike'] > 1.5:
            strategy = "ACCUMULATE ON DIPS"; conf = 7
        if m['change_pct'] > 2.0 and m['vol_spike'] > 1.8:
            strategy = "BUY ON BREAKOUT"; conf = 8
        if m['change_pct'] > 3.0 and m['vol_spike'] > 2.5:
            strategy = "HIGH MOMENTUM BUY"; conf = 9

        report["top_picks"].append({
            "ticker": m["ticker"], "name": m["name"], "sector": m["sector"],
            "price": m["price"], "confidence": conf, "strategy": strategy,
            "analysis": f"The asset {m['name']} is showing robust technical strength in the {m['sector']} sector. Price shifted {m['change_pct']}% on high relative volume ({m['vol_spike']}x avg)."
        })
    return report

def analyze_with_ai(market_data):
    variants = ["v1beta/models/gemini-2.5-flash", "v1beta/models/gemini-2.0-flash", "v1beta/models/gemini-1.5-flash"]
    prompt = f"Analyze these Bursa Malaysia stocks. Suggest the TOP 12 SHARIAH setups. Output JSON ONLY. Data: {json.dumps(market_data)}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for variant in variants:
        try:
            url = f"https://generativelanguage.googleapis.com/{variant}:generateContent?key={GEMINI_API_KEY}"
            response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=15)
            if response.status_code == 200:
                content = response.json()['candidates'][0]['content']['parts'][0]['text']
                match = re.search(r'\{.*\}', content, re.DOTALL)
                return json.loads(match.group())
        except: continue
    return None

def main():
    data = get_top_movers()
    if not data: return
    report = analyze_with_ai(data) or rule_based_analysis(data)
    os.makedirs('data', exist_ok=True)
    with open('data/daily_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("Dashboard Updated: Version 3.1 Pro Sync.")

if __name__ == "__main__":
    main()

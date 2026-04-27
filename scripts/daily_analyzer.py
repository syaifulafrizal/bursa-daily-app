import yfinance as yf
import requests
import json
import os
import datetime
import time
import re

# ASSET ARCHITECT ENGINE - VERSION 5.0 (DEEP DIVE INTEGRATED)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ASSET_METADATA = {
    # UTILITIES & RE
    "5347.KL": {"name": "TENAGA", "sector": "Utilities"}, "6033.KL": {"name": "PETGAS", "sector": "Utilities"},
    "5183.KL": {"name": "PCHEM", "sector": "Energy"}, "5012.KL": {"name": "MALAKOF", "sector": "Utilities"},
    "0215.KL": {"name": "SLVEST", "sector": "Utilities"}, "6742.KL": {"name": "YTL", "sector": "Utilities"},
    "0217.KL": {"name": "SAMAIDEN", "sector": "Utilities"}, "5246.KL": {"name": "WESTPORT", "sector": "Utilities"},
    "0132.KL": {"name": "CYPARK", "sector": "Utilities"},
    # TECHNOLOGY
    "5309.KL": {"name": "ITMAX", "sector": "Technology"}, "0235.KL": {"name": "SNS", "sector": "Technology"},
    "0166.KL": {"name": "INARI", "sector": "Technology"}, "0097.KL": {"name": "VITROX", "sector": "Technology"},
    "0138.KL": {"name": "MYEG", "sector": "Technology"}, "0128.KL": {"name": "FRONTKN", "sector": "Technology"},
    "7006.KL": {"name": "D&O", "sector": "Technology"}, "0008.KL": {"name": "SKPRES", "sector": "Technology"},
    "0151.KL": {"name": "CTOS", "sector": "Technology"}, "3867.KL": {"name": "MPI", "sector": "Technology"},
    "0023.KL": {"name": "IFCA", "sector": "Technology"}, "0123.KL": {"name": "LGMS", "sector": "Technology"},
    "0111.KL": {"name": "UWC", "sector": "Technology"}, "5005.KL": {"name": "UNISEM", "sector": "Technology"},
    # CONSTRUCTION & INFRA
    "5398.KL": {"name": "GAMUDA", "sector": "Construction"}, "8877.KL": {"name": "EKOVEST", "sector": "Construction"},
    "5226.KL": {"name": "GBGAQRS", "sector": "Construction"}, "5099.KL": {"name": "SUNCON", "sector": "Construction"},
    "5263.KL": {"name": "KERJAYA", "sector": "Construction"}, "5148.KL": {"name": "IJM", "sector": "Construction"},
    "5248.KL": {"name": "MRDIY", "sector": "Consumer"}, "5211.KL": {"name": "SUNWAY", "sector": "Construction"},
    "5031.KL": {"name": "WCEHB", "sector": "Construction"}, "1651.KL": {"name": "MRCB", "sector": "Construction"},
    "5340.KL": {"name": "GADANG", "sector": "Construction"}, "5223.KL": {"name": "ECONBHD", "sector": "Construction"},
    "5236.KL": {"name": "MUDAJYA", "sector": "Construction"}, "5071.KL": {"name": "TROP", "sector": "Construction"},
    # ENERGY (O&G)
    "5243.KL": {"name": "VELESTO", "sector": "Energy"}, "0219.KL": {"name": "RLINK", "sector": "Energy"},
    "5210.KL": {"name": "ARMADA", "sector": "Energy"}, "5199.KL": {"name": "HIBISCS", "sector": "Energy"},
    "5133.KL": {"name": "PTRANS", "sector": "Energy"}, "7277.KL": {"name": "DIALOG", "sector": "Energy"},
    "5218.KL": {"name": "SAPNRG", "sector": "Energy"}, "5132.KL": {"name": "COASTAL", "sector": "Energy"},
    "5190.KL": {"name": "WASCO", "sector": "Energy"},
    # CONSUMER & RETAIL
    "5285.KL": {"name": "SDG", "sector": "Consumer"}, "3034.KL": {"name": "HAPSENG", "sector": "Consumer"},
    "4065.KL": {"name": "PPB", "sector": "Consumer"}, "5296.KL": {"name": "AEON", "sector": "Consumer"},
    "5301.KL": {"name": "99SMART", "sector": "Consumer"}, "3689.KL": {"name": "F&N", "sector": "Consumer"},
    "4707.KL": {"name": "NESTLE", "sector": "Consumer"}, "7052.KL": {"name": "QL", "sector": "Consumer"},
    "5212.KL": {"name": "TGC", "sector": "Consumer"}, "5250.KL": {"name": "7ELEVEN", "sector": "Consumer"},
    # HEALTHCARE
    "5168.KL": {"name": "HARTA", "sector": "Healthcare"}, "7153.KL": {"name": "KOSSAN", "sector": "Healthcare"},
    "5225.KL": {"name": "IHH", "sector": "Healthcare"}, "5878.KL": {"name": "KPJ", "sector": "Healthcare"},
    "7113.KL": {"name": "TOPGLOV", "sector": "Healthcare"}, "7106.KL": {"name": "SUPERMX", "sector": "Healthcare"},
    "7081.KL": {"name": "PHARMA", "sector": "Healthcare"},
    # PROPERTY
    "8664.KL": {"name": "SPSETIA", "sector": "Property"}, "5288.KL": {"name": "SIMEPROP", "sector": "Property"},
    "8583.KL": {"name": "MAHSING", "sector": "Property"}, "5148.KL": {"name": "UEMS", "sector": "Property"},
    "5249.KL": {"name": "IOIPROP", "sector": "Property"}, "5279.KL": {"name": "MATRIX", "sector": "Property"},
    "1503.KL": {"name": "OSK", "sector": "Property"},
    # INDUSTRIAL
    "5005.KL": {"name": "UNISEM", "sector": "Industrial"}, "2739.KL": {"name": "PMETAL", "sector": "Industrial"},
    "5139.KL": {"name": "MCEMENT", "sector": "Industrial"}, "5099.KL": {"name": "SUNCON", "sector": "Industrial"},
    "5109.KL": {"name": "CHINHIN", "sector": "Industrial"}
}

def get_top_movers():
    print(f"Scanning Asset Architect Universe ({len(ASSET_METADATA)} assets)...")
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
            
            news_items = []
            if t.news:
                for n in t.news[:3]:
                    news_items.append(n['title'])

            active_data.append({
                "ticker": ticker, "name": meta["name"], "sector": meta["sector"],
                "price": round(price, 3), "change_pct": round(change, 2),
                "vol_spike": round(volume / avg_vol, 2) if avg_vol > 0 else 1.0,
                "news": news_items
            })
            time.sleep(0.01)
        except: continue
    # Sort by momentum score and return top 40 for AI to filter
    return sorted(active_data, key=lambda x: (abs(x['change_pct']) + (x['vol_spike'] * 0.5)), reverse=True)[:40]

def rule_based_analysis(market_data):
    report = {
        "date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "market_overview": "Market Universe scan active. High volume rebalancing detected in key laggard sectors.",
        "top_picks": []
    }
    # Return 24 picks in fallback
    for i, m in enumerate(market_data[:24]):
        strategy = "WATCHLIST"; conf = 6
        reason = "Volume activity"
        if abs(m['change_pct']) > 1.2 or m['vol_spike'] > 1.5:
            strategy = "ACCUMULATE"; conf = 7; reason = "Breakout momentum"
        if m['change_pct'] > 2.0 and m['vol_spike'] > 1.8:
            strategy = "BULLISH BREAKOUT"; conf = 8; reason = "Institutional flow"
            
        report["top_picks"].append({
            "ticker": m["ticker"], "name": m["name"], "sector": m["sector"],
            "price": m["price"], "confidence": conf, "strategy": strategy,
            "confidence_basis": reason,
            "analysis": f"{m['name']} is exhibiting technical strength in the {m['sector']} sector. Price shifted {m['change_pct']}% on {m['vol_spike']}x relative volume.",
            "deep_dive": {
                "thesis": f"Technical setup in {m['name']} is driven by a volume anomaly in the {m['sector']} sector.",
                "catalysts": [f"{m['vol_spike']}x Average Daily Volume", "Support zone established"],
                "risks": ["Broader market volatility", "Sector rotation risk"]
            }
        })
    return report

def analyze_with_ai(market_data):
    variants = ["v1beta/models/gemini-2.5-flash", "v1beta/models/gemini-2.0-flash", "v1beta/models/gemini-1.5-flash"]
    prompt = f"""
    You are a Senior Bursa Analyst. Analyze these Bursa Malaysia stocks. 
    1. Pick the TOP 24 most interesting SHARIAH setups (do not limit to 12).
    2. Provide a 'confidence_basis' field explaining why the confidence score was given (e.g. 'Strong News Catalyst', 'Volume Breakout', etc.).
    3. Provide a 'deep_dive' object with 'thesis', 'catalysts' (list), and 'risks' (list).
    Output JSON ONLY. Data: {json.dumps(market_data)}
    
    JSON Format:
    {{
      "date": "{datetime.datetime.now().strftime('%Y-%m-%d')}",
      "market_overview": "Detailed overview...",
      "top_picks": [
        {{
          "ticker": "...", "name": "...", "sector": "...", "price": 0.00,
          "analysis": "2-sentence brief",
          "confidence": 1-10,
          "confidence_basis": "Short reason",
          "strategy": "...",
          "deep_dive": {{
            "thesis": "Longer investment thesis...",
            "catalysts": ["Catalyst 1", "Catalyst 2"],
            "risks": ["Risk 1", "Risk 2"]
          }}
        }}
      ]
    }}
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for variant in variants:
        try:
            url = f"https://generativelanguage.googleapis.com/{variant}:generateContent?key={GEMINI_API_KEY}"
            response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=25)
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
    print("Asset Architect V5.0 Synchronized.")

if __name__ == "__main__":
    main()

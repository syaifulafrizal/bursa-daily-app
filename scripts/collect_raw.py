import yfinance as yf
import json
import time
import datetime
import xml.etree.ElementTree as ET

ASSET_METADATA = {
    "5347.KL": {"name": "TENAGA", "sector": "Utilities"}, "6033.KL": {"name": "PETGAS", "sector": "Utilities"},
    "5183.KL": {"name": "PCHEM", "sector": "Energy"}, "5398.KL": {"name": "GAMUDA", "sector": "Construction"},
    "5012.KL": {"name": "MALAKOF", "sector": "Utilities"}, "0215.KL": {"name": "SLVEST", "sector": "Utilities"},
    "6742.KL": {"name": "YTL", "sector": "Utilities"}, "0217.KL": {"name": "SAMAIDEN", "sector": "Utilities"},
    "5246.KL": {"name": "WESTPORT", "sector": "Utilities"}, "0132.KL": {"name": "CYPARK", "sector": "Utilities"},
    "5309.KL": {"name": "ITMAX", "sector": "Technology"}, "0235.KL": {"name": "SNS", "sector": "Technology"},
    "0166.KL": {"name": "INARI", "sector": "Technology"}, "0097.KL": {"name": "VITROX", "sector": "Technology"},
    "0138.KL": {"name": "MYEG", "sector": "Technology"}, "0128.KL": {"name": "FRONTKN", "sector": "Technology"},
    "5243.KL": {"name": "VELESTO", "sector": "Energy"}, "0219.KL": {"name": "RLINK", "sector": "Energy"},
    "5210.KL": {"name": "ARMADA", "sector": "Energy"}, "5199.KL": {"name": "HIBISCS", "sector": "Energy"},
    "5133.KL": {"name": "PTRANS", "sector": "Energy"}, "8877.KL": {"name": "EKOVEST", "sector": "Construction"},
    "5226.KL": {"name": "GBGAQRS", "sector": "Construction"}, "5099.KL": {"name": "SUNCON", "sector": "Construction"},
    "5263.KL": {"name": "KERJAYA", "sector": "Construction"}, "5148.KL": {"name": "IJM", "sector": "Construction"},
    "5248.KL": {"name": "MRDIY", "sector": "Consumer"}, "5211.KL": {"name": "SUNWAY", "sector": "Construction"},
    "5168.KL": {"name": "HARTA", "sector": "Healthcare"}, "7153.KL": {"name": "KOSSAN", "sector": "Healthcare"},
    "5225.KL": {"name": "IHH", "sector": "Healthcare"}, "5878.KL": {"name": "KPJ", "sector": "Healthcare"},
    "5285.KL": {"name": "SDG", "sector": "Consumer"}, "5296.KL": {"name": "AEON", "sector": "Consumer"},
    "5301.KL": {"name": "99SMART", "sector": "Consumer"}, "8664.KL": {"name": "SPSETIA", "sector": "Property"},
    "5288.KL": {"name": "SIMEPROP", "sector": "Property"}, "8583.KL": {"name": "MAHSING", "sector": "Property"},
    "2739.KL": {"name": "PMETAL", "sector": "Industrial"}, "5139.KL": {"name": "MCEMENT", "sector": "Industrial"},
    "5109.KL": {"name": "CHINHIN", "sector": "Industrial"}
}

def get_google_news(name):
    try:
        query = f"{name} Bursa Malaysia news"
        url = f"https://news.google.com/rss/search?q={query}&hl=en-MY&gl=MY&ceid=MY:en"
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        return [item.find('title').text for item in root.findall('./channel/item')[:2]]
    except: return []

print("Scanning for movers...")
data = []
for ticker, meta in ASSET_METADATA.items():
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="10d")
        if hist.empty or len(hist) < 2: continue
        price = hist['Close'].iloc[-1]
        change = round(((price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100, 2)
        vol_spike = round(hist['Volume'].iloc[-1] / hist['Volume'].mean(), 2) if hist['Volume'].mean() > 0 else 1.0
        data.append({"ticker": ticker, "name": meta["name"], "sector": meta["sector"], "price": round(price, 3), "change_pct": change, "vol_spike": vol_spike})
    except: continue

top = sorted(data, key=lambda x: abs(x['change_pct']) + x['vol_spike'], reverse=True)[:15]
print(json.dumps(top))

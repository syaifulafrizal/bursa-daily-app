import yfinance as yf
from google import genai
import json
import os
import datetime
import time
import re

# Setup Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

# Using the newest google-genai SDK to fix routing issues
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-1.5-flash" 

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
                "vol_spike": round(volume / avg_vol, 2)
            })
            time.sleep(0.1)
        except: continue
    return sorted(active_data, key=lambda x: (abs(x['change_pct']) + x['vol_spike']), reverse=True)[:20]

def analyze_market(market_data):
    prompt = f"""
    You are a Senior Bursa Malaysia Analyst. 
    Analyze these stocks and suggest the TOP 5-8 most interesting SHARIAH-COMPLIANT setups.
    
    Data:
    {json.dumps(market_data, indent=2)}
    
    Output JSON ONLY:
    {{
      "date": "{datetime.datetime.now().strftime('%Y-%m-%d')}",
      "market_overview": "Sophisticated read on Bursa today.",
      "top_picks": [
        {{
          "ticker": "Ticker",
          "name": "Full Name",
          "sector": "Sector",
          "price": 0.00,
          "analysis": "2-sentence institutional analysis",
          "confidence": 1-10,
          "strategy": "Actionable stance"
        }}
      ]
    }}
    """
    try:
        # Switch to newest client.models.generate_content pattern
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        content = response.text
        match = re.search(r'\{.*\}', content, re.DOTALL)
        return json.loads(match.group()) if match else json.loads(content)
    except Exception as e:
        print(f"AI Error: {e}")
        # FALLBACK: Create a basic report if AI fails so the website doesn't break
        return {
            "date": datetime.datetime.now().strftime('%Y-%m-%d'),
            "market_overview": "AI Analysis is currently synchronizing. Showing raw market data.",
            "top_picks": [
                {
                    "ticker": m["ticker"],
                    "name": m["name"],
                    "sector": m["sector"],
                    "price": m["price"],
                    "analysis": f"Price change: {m['change_pct']}% | Volume Spike: {m['vol_spike']}x avg.",
                    "confidence": 5,
                    "strategy": "MONITOR DATA"
                } for m in market_data[:5]
            ]
        }

def main():
    data = get_top_movers()
    print(f"Analyzing {len(data)} movers...")
    report = analyze_market(data)
    if report:
        os.makedirs('data', exist_ok=True)
        report_path = os.path.join('data', 'daily_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print("Success.")

if __name__ == "__main__":
    main()

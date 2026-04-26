import yfinance as yf
import requests
import json
import os
import datetime
import time
import re

# ABSOLUTE IMPLEMENTATION: Using pure HTTP requests to bypass SDK routing issues.
# This works 100% with the Free Tier Gemini API Key.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

# Stable v1 Endpoint
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

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
            time.sleep(0.1)
        except: continue
    # Return top 15 most active for context
    return sorted(active_data, key=lambda x: (abs(x['change_pct']) + x['vol_spike']), reverse=True)[:15]

def analyze_market(market_data):
    prompt = f"""
    You are an Institutional Senior Bursa Malaysia Analyst. 
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
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response_data = response.json()
        
        if response.status_code != 200:
            print(f"API Error ({response.status_code}): {response.text}")
            return None
            
        content = response_data['candidates'][0]['content']['parts'][0]['text']
        match = re.search(r'\{.*\}', content, re.DOTALL)
        return json.loads(match.group()) if match else json.loads(content)
        
    except Exception as e:
        print(f"Implementation Error: {e}")
        return None

def main():
    data = get_top_movers()
    if not data:
        print("No market data found.")
        return

    print(f"Analyzing {len(data)} movers via fail-proof HTTP...")
    report = analyze_market(data)
    
    if report:
        os.makedirs('data', exist_ok=True)
        report_path = os.path.join('data', 'daily_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print("Intelligence report published successfully.")
    else:
        print("AI analysis failed to generate.")

if __name__ == "__main__":
    main()

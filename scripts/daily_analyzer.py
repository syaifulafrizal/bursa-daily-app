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

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-1.5-flash" 

# Shariah Sector Map for Fallback
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
    print("Scanning Bursa Malaysia for active stocks...")
    # Cleaned list (removed delisted/404 symbols)
    base_tickers = list(SECTOR_MAP.keys())
    
    active_data = []
    for ticker_symbol in base_tickers:
        try:
            t = yf.Ticker(ticker_symbol)
            # Use a longer period to ensure we always get at least two trading days
            hist = t.history(period="10d")
            if hist.empty or len(hist) < 2: 
                continue
            
            price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((price - prev_price) / prev_price) * 100
            volume = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].mean()
            vol_spike = volume / avg_vol if avg_vol > 0 else 1.0
            
            # Fetch news
            news_items = []
            try:
                if t.news:
                    for n in t.news[:3]:
                        news_items.append(n['title'])
            except:
                pass

            # We accept everything that has a price to avoid "0 movers"
            # The AI will then sort the wheat from the chaff
            active_data.append({
                "ticker": ticker_symbol,
                "name": ticker_symbol.replace(".KL", ""), # Fallback name
                "sector": SECTOR_MAP.get(ticker_symbol, "Other"),
                "price": round(price, 3),
                "change_pct": round(change, 2),
                "vol_spike": round(vol_spike, 2),
                "news": news_items
            })
            time.sleep(0.2) # Small delay for reliability
        except Exception as e:
            print(f"Skipping {ticker_symbol}: {e}")
            continue
            
    # Sort by momentum (price change * volume spike)
    active_data = sorted(active_data, key=lambda x: (abs(x['change_pct']) + x['vol_spike']), reverse=True)
    return active_data[:20] # Send top 20 to AI

def analyze_market(market_data):
    if not market_data:
        return None

    prompt = f"""
    You are a Senior Bursa Malaysia Analyst. 
    Analyze these stocks for a Shariah-compliant watchlist. 
    
    RULES:
    1. EXCLUDE non-Shariah stocks.
    2. YOU MUST suggest the TOP 5-8 most interesting stocks from the list provided.
    3. Categorize each into a sector: Technology, Utilities, Energy, Construction, Healthcare, Consumer, or Other.
    
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
          "sector": "Sector Name",
          "price": 0.00,
          "analysis": "2-sentence institutional analysis",
          "confidence": 1-10,
          "strategy": "Actionable stance"
        }}
      ]
    }}
    """
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

def main():
    market_data = get_top_movers()
    print(f"Captured {len(market_data)} assets. Generating intelligence report...")
    
    report = analyze_market(market_data)
    
    if report:
        os.makedirs('data', exist_ok=True)
        with open('data/daily_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("Intelligence report published successfully.")
    else:
        print("Failed to generate report.")

if __name__ == "__main__":
    main()

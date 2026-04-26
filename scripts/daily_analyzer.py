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

def get_top_movers():
    """
    Enhanced market scanner focusing on high-volume and trending Shariah-compliant sectors.
    """
    print("Scanning Bursa Malaysia for active stocks...")
    # Expanded list of high-liquidity stocks across key sectors
    base_tickers = [
        # Utilities & Infrastructure (Data Center Proxies)
        "5347.KL", "6033.KL", "5183.KL", "5398.KL", "5012.KL", "0215.KL", "5014.KL",
        # Tech & Data Centers
        "5309.KL", "0235.KL", "0166.KL", "0097.KL", "0138.KL", "0128.KL", "0151.KL", "0008.KL",
        # Energy (O&G Recovery)
        "5243.KL", "0219.KL", "5279.KL", "5210.KL", "5199.KL", "5133.KL",
        # Construction & Property (Johor Theme)
        "8877.KL", "5226.KL", "5099.KL", "5263.KL", "5148.KL", "5248.KL", "5211.KL",
        # Gloves / Healthcare (VM2026)
        "5168.KL", "7153.KL", "5225.KL", "5878.KL", "5235.KL",
        # Consumer & Retail
        "5285.KL", "3034.KL", "4065.KL", "7277.KL", "5296.KL", "5301.KL"
    ]
    
    active_data = []
    for ticker_symbol in base_tickers:
        try:
            t = yf.Ticker(ticker_symbol)
            # Use 7 days to guarantee data availability regardless of holidays/weekends
            hist = t.history(period="7d")
            if hist.empty or len(hist) < 2: continue
            
            info = t.info
            price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((price - prev_price) / prev_price) * 100
            volume = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].mean()
            
            # Extract sector
            sector = info.get('sector', 'Other')
            if 'Technology' in sector: sector = 'Technology'
            elif 'Utilities' in sector: sector = 'Utilities'
            elif 'Energy' in sector: sector = 'Energy'
            elif 'Industrial' in sector: sector = 'Construction'
            elif 'Construction' in sector: sector = 'Construction'
            elif 'Healthcare' in sector: sector = 'Healthcare'
            elif 'Consumer' in sector: sector = 'Consumer'
            
            # Simplified News
            news_items = []
            if t.news:
                for n in t.news[:3]:
                    news_items.append(n['title'])

            # Score relevance
            vol_spike = volume / avg_vol if avg_vol > 0 else 1.0
            
            # CAPTURE ALL: We lower the threshold even more. 
            # If volume is > 50% of avg OR price moves > 0.1%, we keep it for AI to decide.
            # This prevents "0 stocks found" errors.
            if abs(change) >= 0.05 or vol_spike > 0.5:
                active_data.append({
                    "ticker": ticker_symbol,
                    "name": info.get('shortName', ticker_symbol),
                    "sector": sector,
                    "price": round(price, 3),
                    "change_pct": round(change, 2),
                    "vol_spike": round(vol_spike, 2),
                    "news": news_items
                })
        except:
            continue
            
    # Sort by momentum
    active_data = sorted(active_data, key=lambda x: (abs(x['change_pct']) * x['vol_spike']), reverse=True)
    return active_data[:25] # Send top 25 to AI

def analyze_market(market_data):
    if not market_data:
        return None

    prompt = f"""
    You are a Senior Bursa Malaysia Analyst. 
    Analyze these stocks for a Shariah-compliant watchlist. 
    
    RULES:
    1. EXCLUDE non-Shariah stocks (Banks like Maybank, Public Bank, etc., should not be in your final list).
    2. Suggest at least 5-8 stocks from the data below. If data is limited, explain why in the overview.
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
          "name": "Name",
          "sector": "Sector Name",
          "price": 0.00,
          "analysis": "2-sentence deep dive",
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
    except:
        return None

def main():
    market_data = get_top_movers()
    print(f"Captured {len(market_data)} movers. Analyzing...")
    report = analyze_market(market_data)
    
    if report:
        # Save to data directory
        os.makedirs('data', exist_ok=True)
        with open('data/daily_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("Report updated.")

if __name__ == "__main__":
    main()

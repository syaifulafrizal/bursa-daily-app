import yfinance as yf
import google.generativeai as genai
import json
import os
import datetime
import time

# Setup Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_top_movers():
    """
    Fetches the current top gainers/active stocks from Bursa Malaysia using yfinance.
    Note: yfinance doesn't have a direct 'Shariah-only' screener, so we fetch active
    ones and let the AI or a local list filter them.
    """
    print("Scanning Bursa Malaysia for active stocks...")
    # Common active sectors/indices to pull symbols from
    # For a truly dynamic approach, we pull a broad list or use a predefined 'Active' set
    # Here we use the FBMKLCI + FBM70 as a base for high-liquidity stocks
    base_tickers = [
        "5347.KL", "5243.KL", "5309.KL", "5398.KL", "5225.KL", "0215.KL", "8877.KL", 
        "0219.KL", "5226.KL", "0235.KL", "5168.KL", "7153.KL", "5285.KL", "6033.KL", 
        "5183.KL", "1023.KL", "1155.KL", "1295.KL", "1066.KL", "5819.KL", "6888.KL",
        "4707.KL", "5225.KL", "3034.KL", "4065.KL", "8664.KL", "5012.KL", "1818.KL"
    ]
    
    active_data = []
    for ticker_symbol in base_tickers:
        try:
            t = yf.Ticker(ticker_symbol)
            # Use 1d period with small interval to see today's/yesterday's momentum
            hist = t.history(period="2d")
            if hist.empty or len(hist) < 2: continue
            
            price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((price - prev_price) / prev_price) * 100
            volume = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].mean()
            
            # Only include if there is significant price action or volume spike
            if abs(change) > 1.5 or volume > (avg_vol * 1.2):
                active_data.append({
                    "ticker": ticker_symbol,
                    "name": t.info.get('shortName', ticker_symbol),
                    "price": round(price, 3),
                    "change_pct": round(change, 2),
                    "vol_spike": round(volume / avg_vol, 2),
                    "news": "\n".join([f"- {n['title']}" for n in t.news[:3]])
                })
        except:
            continue
            
    return active_data

def analyze_market(market_data):
    prompt = f"""
    You are a Senior Bursa Malaysia Market Analyst. 
    Analyze the following list of active Bursa stocks. 
    
    CRITICAL RULES:
    1. ONLY suggest stocks that are SHARIAH-COMPLIANT. Use your internal knowledge of Bursa Malaysia Shariah status.
    2. Focus on stocks with HIGH CONFIDENCE based on news and volume spikes.
    
    Current Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
    
    Active Market Data:
    {json.dumps(market_data, indent=2)}
    
    Provide your analysis in JSON format:
    {{
      "date": "YYYY-MM-DD",
      "market_overview": "Short summary of current Bursa tone and major themes today",
      "top_picks": [
        {{
          "ticker": "Ticker",
          "name": "Name",
          "price": 0.00,
          "analysis": "In-depth analysis of WHY this is interesting TODAY (News + Price Action)",
          "confidence": 1-10,
          "strategy": "Actionable strategy (e.g. Buy on breakout, Watch for pullback)"
        }}
      ]
    }}
    """
    
    response = model.generate_content(prompt)
    try:
        json_str = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_str)
    except:
        return None

def main():
    # Step 1: Scan market for dynamic 'Top Movers'
    market_data = get_top_movers()
    
    # Step 2: Let AI filter for Shariah-compliance and Quality
    print("Filtering for Shariah-compliance and analyzing setups...")
    report = analyze_market(market_data)
    
    if report:
        report_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'daily_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Dynamic report generated: {report_path}")

if __name__ == "__main__":
    main()

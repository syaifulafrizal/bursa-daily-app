import yfinance as yf
from google import genai
import json
import os
import datetime
import time
import re

# Setup Gemini API using the new google-genai SDK
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
# Using 1.5-flash as it has the most reliable free-tier quota for daily tasks
MODEL_ID = "gemini-1.5-flash" 

def get_top_movers():
    """
    Fetches the current top gainers/active stocks from Bursa Malaysia using yfinance.
    """
    print("Scanning Bursa Malaysia for active stocks...")
    base_tickers = [
        "5347.KL", "5243.KL", "5309.KL", "5398.KL", "5225.KL", "0215.KL", "8877.KL", 
        "0219.KL", "5226.KL", "0235.KL", "5168.KL", "7153.KL", "5285.KL", "6033.KL", 
        "5183.KL", "1023.KL", "1155.KL", "1295.KL", "1066.KL", "5819.KL", "6888.KL",
        "4707.KL", "3034.KL", "4065.KL", "8664.KL", "5012.KL", "1818.KL"
    ]
    
    active_data = []
    for ticker_symbol in base_tickers:
        try:
            t = yf.Ticker(ticker_symbol)
            # Use 5 days to ensure we always have data even if market was closed yesterday
            hist = t.history(period="5d")
            if hist.empty or len(hist) < 2: continue
            
            price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((price - prev_price) / prev_price) * 100
            volume = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].mean()
            
            # Relaxed filters to ensure we always find some interesting stocks
            if abs(change) > 0.5 or volume > (avg_vol * 0.8):
                active_data.append({
                    "ticker": ticker_symbol,
                    "name": t.info.get('shortName', ticker_symbol),
                    "price": round(price, 3),
                    "change_pct": round(change, 2),
                    "vol_spike": round(volume / avg_vol, 2),
                    "news": "\n".join([f"- {n['title']}" for n in t.news[:3]])
                })
        except Exception as e:
            continue
            
    # Sort by change percentage to prioritize movers
    active_data = sorted(active_data, key=lambda x: abs(x['change_pct']), reverse=True)
    return active_data[:15] # Limit to top 15 movers for AI prompt efficiency

def analyze_market(market_data):
    if not market_data:
        return {
            "date": datetime.datetime.now().strftime('%Y-%m-%d'),
            "market_overview": "Market data scan yielded no active movers. Monitoring for upcoming volatility.",
            "top_picks": []
        }

    prompt = f"""
    You are a Senior Bursa Malaysia Market Analyst. 
    Analyze the following list of active Bursa stocks. 
    
    CRITICAL RULES:
    1. ONLY suggest stocks that are SHARIAH-COMPLIANT. Use your internal knowledge.
    2. Focus on stocks with HIGH CONFIDENCE based on news and volume spikes.
    
    Current Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
    
    Active Market Data:
    {json.dumps(market_data, indent=2)}
    
    Provide your analysis in JSON format:
    {{
      "date": "YYYY-MM-DD",
      "market_overview": "Short summary of current Bursa tone",
      "top_picks": [
        {{
          "ticker": "Ticker",
          "name": "Name",
          "price": 0.00,
          "analysis": "In-depth analysis of WHY this is interesting TODAY",
          "confidence": 1-10,
          "strategy": "Actionable strategy"
        }}
      ]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        content = response.text
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(content)
    except Exception as e:
        print(f"Error analyzing with Gemini: {e}")
        return None

def main():
    market_data = get_top_movers()
    print(f"Found {len(market_data)} stocks to analyze. Sending to Gemini...")
    
    report = analyze_market(market_data)
    
    if report:
        report_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, 'daily_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report generated: {report_path}")
    else:
        print("Failed to generate report.")

if __name__ == "__main__":
    main()

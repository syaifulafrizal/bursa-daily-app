# 🏛️ Asset Architect: Manual Intelligence Node

Automated, high-fidelity market intelligence for Shariah-compliant equities on Bursa Malaysia. This repository operates as a **Manual Intelligence Node**, powered by Gemini Agent synthesis.

## 🚀 The Vision
**Asset Architect** bridges the gap between institutional-grade data and retail Shariah investors. By synthesizing price action, volume anomalies, and news catalysts, the platform identifies high-conviction setups every morning before the market open.

## 🛠️ Architecture
- **Engine:** Manual Agent Synthesis (Bypasses API rate limits/costs).
- **Frontend:** Responsive dashboard using Tailwind CSS and Plus Jakarta Sans.
- **Data Source:** YFinance real-time market feed.
- **Workflow:** Human-in-the-loop agentic updates via Gemini CLI.

## 📡 Operational Workflow

This repository has been optimized for **Manual Agent Updates** to ensure 100% reliable, high-quality analysis without API key restrictions.

### Daily Update Procedure:
1. **Open Gemini CLI** in this repository.
2. **Issue Directive:**  
   `"Run the daily market analysis and update the website."`
3. **Agent Action:**  
   The agent will automatically:
   - Scan the 120-stock Shariah Universe.
   - Fetch real-time price, volume, and Google News headlines.
   - Perform in-context AI synthesis of catalysts and risks.
   - Update `data/daily_report.json` and push to GitHub Pages.

## 🛠️ Local Development
To run the dashboard locally for testing:
1. Clone the repository.
2. Open `index.html` in any modern web browser.
3. Ensure the `data/` directory contains valid JSON files.

## ⚖️ Disclaimer
Asset Architect is an automated research tool. All information is provided for educational purposes and does not constitute financial advice. Trading involves significant risk of loss. Always consult a licensed professional before investing.

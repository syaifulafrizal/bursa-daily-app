# 🏛️ Asset Architect: Shariah Market Intelligence

Automated, high-fidelity market intelligence for Shariah-compliant equities on Bursa Malaysia. Powered by AI and real-time flow analysis.

## 🚀 Vision
**Asset Architect** is designed to bridge the gap between institutional-grade data and retail Shariah investors. By synthesizing price action, volume anomalies, and news catalysts, the platform identifies high-conviction setups every morning before the market open.

## 🛠️ Core Technology
- **Intelligence Engine:** Version 4.0 (Multi-model AI with expert logic fallback).
- **Automation:** GitHub Actions cloud orchestration.
- **Data Source:** YFinance Real-time market feed.
- **Frontend:** Responsive dashboard using Tailwind CSS and Plus Jakarta Sans.

## 📡 Deployment Guide

### 1. Intelligence Key
Generate a free API key from [Google AI Studio](https://aistudio.google.com/). This powers the qualitative analysis layer.

### 2. Infrastructure Setup
Push the codebase to a **Public** GitHub repository to leverage unlimited Action minutes:
```bash
git init
git add .
git commit -m "Architect: Initializing V4.0 Infrastructure"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/asset-architect.git
git push -u origin main
```

### 3. Security Configuration
In your GitHub Repo:
1. Navigate to **Settings > Secrets and variables > Actions**.
2. Create a **New repository secret**.
3. Name: `GEMINI_API_KEY`
4. Value: (Your key from Step 1).

### 4. Live Dashboard Activation
1. Navigate to **Settings > Pages**.
2. Deployment Source: `Deploy from a branch`.
3. Branch: `main` | Folder: `/ (root)`.
4. Click **Save**.

### 5. Manual Execution
To see results immediately, go to the **Actions** tab, select `Daily Bursa Analysis`, and click `Run workflow`.

## ⚖️ Disclaimer
Asset Architect is an automated research tool. All information is provided for educational purposes and does not constitute financial advice. Trading involves significant risk of loss. Always consult a licensed professional before investing.

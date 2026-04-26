# Bursa Daily Analyst App

Automated Shariah-compliant market intelligence for Bursa Malaysia.

## Features
- **Daily Automated Updates:** Runs every trading day at 8:00 AM MYT via GitHub Actions.
- **AI-Powered Analysis:** Combines technical data (Price, Volume) with latest news headlines using Gemini 1.5 Flash.
- **Shariah-Focused:** Monitors a curated list of Shariah-compliant stocks.
- **Free Hosting:** Hosted on GitHub Pages.

## Deployment Instructions

### 1. Get a Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Create a free API Key.

### 2. Setup your GitHub Repository
1. Create a **new repository** on GitHub (make it Public to have free GitHub Actions).
2. Push this folder to your repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

### 3. Configure GitHub Secrets
1. In your GitHub repository, go to **Settings > Secrets and variables > Actions**.
2. Click **New repository secret**.
3. Name: `GEMINI_API_KEY`
4. Value: Paste your Gemini API key from Step 1.

### 4. Enable GitHub Pages
1. Go to **Settings > Pages**.
2. Under "Build and deployment", select **Deploy from a branch**.
3. Choose the `main` branch and the `/ (root)` folder.
4. Click **Save**.

### 5. Manual First Run (Optional)
1. Go to the **Actions** tab in your GitHub repository.
2. Select **Daily Bursa Analysis** workflow.
3. Click **Run workflow** to generate your first report immediately.

## Disclaimer
This application provides AI-generated analysis for educational purposes. Always consult with a certified financial advisor before making investment decisions.

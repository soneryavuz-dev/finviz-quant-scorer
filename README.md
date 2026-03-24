# 🚀 Finviz & Yahoo Finance Quant Scorer

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Author](https://img.shields.io/badge/Developer-Soner%20Yavuz-green)](https://github.com/soneryavuz-dev)

An automated high-performance stock analysis tool that scrapes **Finviz** and **Yahoo Finance** data to perform automated multi-factor quant scoring (Profitability, Debt, Value) for global stock analysis.

---

## 📈 Overview
This project is designed for value investors and quantitative analysts. It automates the tedious process of gathering fundamental data and provides a sector-relative scoring system to identify undervalued "gems."

## 🧠 Methodology
The tool applies a **Percentile Ranking** approach within each sector:
* **Profitability (45%):** ROIC, Operating Margin, Gross Margin, EPS Growth, ROE.
* **Financial Health (15%):** Debt/Equity, LT Debt/Equity, Current Ratio.
* **Value (40%):** P/FCF, EV/EBIT (Calculated via TTM), PEG, P/E, P/S.

---

## ✨ Key Features
* **Full Data Integration:** Merges Finviz screener data with Yahoo Finance real-time TTM (Trailing Twelve Months) metrics.
* **EV/EBIT Calculation:** Automatically calculates Enterprise Value and TTM EBIT.
* **Smart Caching:** Avoids rate limits by storing data in local `.csv` caches (valid for 4 hours).
* **Professional Reporting:** Generates a formatted `.xlsx` report with conditional formatting.
* **Multi-threaded Scraping:** Uses `ThreadPoolExecutor` for high-speed data retrieval.

---

## 📊 Example Excel Report: The Power of Quant Scoring

### 📋 Overview & Basic Metrics
Provides a basic snapshot including company profile, sector, country, market cap, P/E ratios, and EPS history.
![Overview & Basic Metrics](images/1.png)

### 💰 Profitability & Financial Health
Visualizes key financial and profitability metrics like Gross Margin, Operating Margin, Debt/Equity ratios, and Returns (ROA, ROE, ROIC).
![Profitability & Financial Health](images/2.png)

### 📈 Advanced Data & Technicals
Includes advanced data points such as Insider and Institutional Transactions, Short Interest, technical indicators (RSI, Moving Averages), volatility, and 10-year performance.
![Advanced Data & Technicals](images/3.png)

### 🏆 Quant Scoring Results (The Key Output)
**This is the most critical section.** It highlights the calculated results of the quantitative scoring system:
* **Final_Score**: The ultimate relative ranking.
* **EV_EBIT**: Enterprise Value / EBIT ratio, a key valuation metric.
* **Profitability_Score**: Weighted profitability metrics.
![Quant Scoring Results](images/4.png)

### 🔍 Detailed Input Breakdown
A deeper look into the individual scores and other technical metrics, including `Value_Score`, `TTM_EBIT`, and `Enterprise_Value`.
![Detailed Input Breakdown](images/5.png)

---

## 🛠️ Installation & Usage

1. **Clone the repo:**
   ```bash
   git clone [https://github.com/soneryavuz-dev/finviz-quant-scorer.git](https://github.com/soneryavuz-dev/finviz-quant-scorer.git)
   cd finviz-quant-scorer
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the analyzer:**
   ```bash
   python main.py
   ```

---

## 👤 Author
Developed with 💡 by **Soner Yavuz**
* **GitHub:** [@soneryavuz-dev](https://github.com/soneryavuz-dev)

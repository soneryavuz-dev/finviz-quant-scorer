# 🚀 Finviz & Yahoo Finance Quant Scorer

[](https://www.python.org/downloads/)
[](https://opensource.org/licenses/MIT)
[](https://github.com/soneryavuz-dev)

An automated high-performance stock analysis tool that scrapes **Finviz** and **Yahoo Finance** data to perform automated multi-factor quant scoring (Profitability, Debt, Value) for global stock analysis.

-----

## 📈 Overview

This project is designed for value investors and quantitative analysts. It automates the tedious process of gathering fundamental data and provides a sector-relative scoring system to identify undervalued "gems."

## 🧠 Methodology

The tool applies a **Percentile Ranking** approach within each sector:

  * **Profitability (45%):** ROIC, Operating Margin, Gross Margin, EPS Growth, ROE.
  * **Financial Health (15%):** Debt/Equity, LT Debt/Equity, Current Ratio.
  * **Value (40%):** P/FCF, EV/EBIT (Calculated via TTM), PEG, P/E, P/S.

-----

## ✨ Key Features

  * **Full Data Integration:** Merges Finviz screener data with Yahoo Finance real-time TTM (Trailing Twelve Months) metrics.
  * **EV/EBIT Calculation:** Automatically calculates Enterprise Value and TTM EBIT for more accurate valuation.
  * **Smart Caching:** Avoids rate limits by storing data in local `.csv` caches (valid for 4 hours).
  * **Professional Reporting:** Generates a formatted `.xlsx` report with conditional formatting.
  * **Multi-threaded Scraping:** Uses `ThreadPoolExecutor` for high-speed data retrieval.

-----

## 📊 Example Excel Report: The Power of Quant Scoring

### 📋 Overview & Basic Metrics

Provides a basic snapshot including company profile, sector, country, market cap, P/E ratios, and EPS history.

### 💰 Profitability & Financial Health

Visualizes key metrics like Gross Margin, Operating Margin, Debt/Equity ratios, and Returns (ROA, ROE, ROIC).

### 📈 Advanced Data & Technicals

Includes Insider/Institutional Transactions, Short Interest, RSI, Moving Averages, and 10-year performance.

### 🏆 Quant Scoring Results (The Key Output)

This is the most critical section. It highlights the calculated results of the quantitative scoring system:

  * **Final\_Score:** The ultimate relative ranking.
  * **EV\_EBIT:** Enterprise Value / EBIT ratio.
  * **Profitability\_Score:** Weighted profitability metrics.

-----

## 🛠️ Installation & Usage

1.  **Clone the repo:**

    ```bash
    git clone https://github.com/soneryavuz-dev/finviz-quant-scorer.git
    cd finviz-quant-scorer
    ```

2.  **Install requirements:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the analyzer:**

    ```bash
    python main.py
    ```

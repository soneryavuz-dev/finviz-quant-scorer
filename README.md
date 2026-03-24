# 🚀 Finviz & Yahoo Finance Quant Scorer

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Author](https://img.shields.io/badge/Developer-Soner%20Yavuz-green)](https://github.com/soneryavuz-dev)

An automated high-performance stock analysis tool that scrapes **Finviz** and **Yahoo Finance** data to perform automated multi-factor quant scoring (Profitability, Debt, Value) for global stock analysis.

---

## 📈 Overview

This project is designed for value investors and quantitative analysts. It automates the tedious process of gathering fundamental data and provides a sector-relative scoring system to identify undervalued "gems."

### 🧠 Methodology
The tool applies a **Percentile Ranking** approach within each sector:
- **Profitability (45%)**: ROIC, Operating Margin, Gross Margin, EPS Growth, ROE.
- **Financial Health (15%)**: Debt/Equity, LT Debt/Equity, Current Ratio.
- **Value (40%)**: P/FCF, EV/EBIT (Calculated via TTM), PEG, P/E, P/S.

---

## ✨ Key Features

* **Full Data Integration:** Merges Finviz screener data with Yahoo Finance real-time TTM (Trailing Twelve Months) metrics.
* **EV/EBIT Calculation:** Automatically calculates Enterprise Value and TTM EBIT for more accurate valuation than simple P/E.
* **Smart Caching:** Avoids rate limits and saves time by storing data in local `.csv` caches (valid for 4 hours).
* **Professional Reporting:** Generates a formatted `.xlsx` report with conditional column widths and headers.
* **Multi-threaded Scraping:** Uses `ThreadPoolExecutor` for high-speed data retrieval.

---

## 🛠️ Installation & Usage

1. **Clone the repo:**
   ```bash
   git clone https://github.com/soneryavuz-dev/finviz-quant-scorer.git
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

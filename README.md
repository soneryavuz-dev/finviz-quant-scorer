# 🚀 Finviz & Yahoo Finance Quant Scorer

An automated stock analysis tool that combines **Finviz** web scraping with **Yahoo Finance** fundamental data to rank stocks using a proprietary quantitative methodology.

## ✨ Key Features
- **Multi-Source Data:** Scrapes Overview, Valuation, Financial, and Technical tabs from Finviz.
- **Advanced Metrics:** Fetches TTM EBIT and real-time Balance Sheet data via Yahoo Finance.
- **Smart Scoring:** Scores stocks within their **Sectors** based on:
  - **Profitability (45%):** ROIC, Oper. Margin, ROE, etc.
  - **Valuation (40%):** P/FCF, EV/EBIT, PEG, P/E.
  - **Financial Health (15%):** Debt/Equity, Current Ratio.
- **Automated Reporting:** Generates a formatted professional Excel report (`Stock_Analysis_Report.xlsx`).
- **Caching System:** Saves time and prevents API rate limits by caching data locally.

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/finviz-quant-scorer.git](https://github.com/YOUR_USERNAME/finviz-quant-scorer.git)

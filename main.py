import pandas as pd
import numpy as np
import time
import sys
import warnings
import logging
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# --- 1. SETTINGS & SILENCERS ---
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")
logging.getLogger('yfinance').setLevel(logging.CRITICAL)
logging.getLogger('yahooquery').setLevel(logging.CRITICAL)

# --- LIBRARY CHECK ---
# Note for GitHub users: Please use 'pip install -r requirements.txt' instead of this function.
# This function is kept for Google Colab compatibility.
def install_libs():
    required = ["finvizfinance", "pandas", "openpyxl", "yahooquery", "tqdm", "yfinance", "xlsxwriter"]
    try:
        import finvizfinance
        import yfinance
        import yahooquery
    except ImportError:
        print("⚠️ Missing libraries detected, installing...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + required + ["-q"])
            print("✅ Libraries installed successfully.")
        except Exception as e:
            print(f"❌ Library installation error: {e}")

install_libs()

try:
    from finvizfinance.screener.overview import Overview
    from finvizfinance.screener.valuation import Valuation
    from finvizfinance.screener.financial import Financial
    from finvizfinance.screener.ownership import Ownership
    from finvizfinance.screener.performance import Performance
    from finvizfinance.screener.technical import Technical
    from yahooquery import Ticker as YQTicker
    import yfinance as yf
    import xlsxwriter
except ImportError as e:
    print(f"❌ Critical import error: {e}. Please install libraries manually.")
    sys.exit()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def clean_mc_vectorized(series):
    series = series.astype(str).str.strip().str.upper()
    # Support for Trillion (T), Billion (B), Million (M), Thousand (K)
    multipliers = series.str.extract(r'([BMKT])')[0].map({
        'T': 1e12, 'B': 1e9, 'M': 1e6, 'K': 1e3
    }).fillna(1)
    
    clean_str = series.str.replace(r'[BMKT]', '', regex=True)
    numbers = pd.to_numeric(clean_str, errors='coerce').fillna(0)
    return numbers * multipliers

def safe_divide(a, b):
    return np.divide(a, b, out=np.zeros_like(a, dtype=float), where=b!=0)

# =============================================================================
# MODULE 1: FINVIZ DATA SCRAPING (ALL TABS)
# =============================================================================
def fetch_finviz_tab(name, screener_obj, filters):
    try:
        time.sleep(random.uniform(0.5, 1.5)) 
        screener_obj.set_filter(filters_dict=filters)
        df = screener_obj.screener_view(verbose=1) 
        if 'No.' in df.columns: df.drop(columns=['No.'], inplace=True)
        df['Ticker'] = df['Ticker'].astype(str).str.strip()
        return name, df
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return name, None

def get_finviz_data():
    print("\n=== [1/3] FETCHING FINVIZ DATA (MAIN LIST) ===")
    
    cache_file = 'cache_finviz_full.csv'
    cache_duration_hours = 4 
    
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < (cache_duration_hours * 3600):
            print(f"⚡ CACHE ACTIVE: Loading from disk ({file_age/60:.0f} mins ago).")
            try:
                df_cache = pd.read_csv(cache_file)
                df_cache['Ticker'] = df_cache['Ticker'].astype(str).str.strip()
                return df_cache
            except Exception as e: 
                print(f"Cache read error: {e}")
    
    print("⬇️ Scraping fresh data from Finviz...")
    filters = {'Market Cap.': '+Small (over $300mln)'}
    
    objs = {
        "Overview": Overview(), 
        "Valuation": Valuation(), 
        "Financial": Financial(),
        "Ownership": Ownership(), 
        "Performance": Performance(), 
        "Technical": Technical()
    }
    
    dfs = []
    with ThreadPoolExecutor(max_workers=3) as exc:
        futures = {exc.submit(fetch_finviz_tab, n, o, filters): n for n, o in objs.items()}
        for f in tqdm(as_completed(futures), total=len(objs), desc="Downloading Finviz"):
            n, d = f.result()
            if d is not None: dfs.append(d)
    
    if not dfs: return pd.DataFrame()
    
    # Merge operation: Join by Ticker, prevent column duplication
    master = dfs[0]
    for d in dfs[1:]:
        cols_to_use = d.columns.difference(master.columns).tolist()
        if 'Ticker' not in cols_to_use: cols_to_use.append('Ticker')
        master = pd.merge(master, d[cols_to_use], on='Ticker', how='inner')
    
    # Market Cap Filter
    mc_col = 'Market Cap' if 'Market Cap' in master.columns else 'Market Cap.'
    if mc_col in master.columns:
        master['MC_Numeric'] = clean_mc_vectorized(master[mc_col])
        final = master[master['MC_Numeric'] >= 1_000_000_000].drop(columns=['MC_Numeric'])
    else: final = master

    try: 
        final.to_csv(cache_file, index=False)
    except Exception as e: 
        print(f"Failed to save cache: {e}")
    
    print(f"✅ STOCKS AFTER FILTERING: {len(final)}")
    return final

# =============================================================================
# MODULE 2: QUANT SCORING
# =============================================================================
def apply_quant_scoring(df):
    print("\n=== [2/3] QUANT SCORING (STAGE 1) ===")
    if df.empty: return df
    df = df.copy()
    
    # Standardize column names
    rename_map = {
        'Forward P/E': 'Fwd P/E', 'EPS this Y': 'EPS This Y',
        'Gross Margin': 'Gross M', 'Oper. Margin': 'Oper M', 'Profit Margin': 'Profit M',
        'Current Ratio': 'Curr R', 'Quick Ratio': 'Quick R', 'LT Debt/Eq': 'LTDebt/Eq'
    }
    df.rename(columns=rename_map, inplace=True)
    
    cols_numeric = ['ROIC', 'Oper M', 'EPS This Y', 'Gross M', 'ROE', 'Profit M', 
                    'Debt/Eq', 'LTDebt/Eq', 'Curr R', 'Quick R', 
                    'P/FCF', 'PEG', 'P/E', 'P/S', 'P/B', 'P/C', 'Short Float']
    
    for c in cols_numeric:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[%/,]', '', regex=True), errors='coerce')
    
    if 'Sector' not in df.columns: df['Sector'] = 'General'
    
    score_dfs = []
    for _, grp in df.groupby('Sector', group_keys=False):
        grp = grp.copy()
        
        # Fill NaNs with median for calculation purposes only
        cols_in_grp = [c for c in cols_numeric if c in grp.columns]
        if cols_in_grp: grp[cols_in_grp] = grp[cols_in_grp].fillna(grp[cols_in_grp].median())
        
        def get_rank(s, asc=True): 
            if s.isnull().all(): return pd.Series(0, index=s.index)
            return s.rank(pct=True, ascending=asc) * 100
        
        # Scoring Logic
        p_score = pd.Series(0, index=grp.index)
        if 'ROIC' in grp:       p_score += get_rank(grp['ROIC'], True) * 0.18
        if 'Oper M' in grp:     p_score += get_rank(grp['Oper M'], True) * 0.08
        if 'Gross M' in grp:    p_score += get_rank(grp['Gross M'], True) * 0.08
        if 'EPS This Y' in grp: p_score += get_rank(grp['EPS This Y'], True) * 0.06
        if 'ROE' in grp:        p_score += get_rank(grp['ROE'], True) * 0.05
        grp['Profitability_Score'] = (p_score / 0.45).clip(0, 100).fillna(0)

        d_score = pd.Series(0, index=grp.index)
        if 'Debt/Eq' in grp:   d_score += get_rank(grp['Debt/Eq'], False) * 0.07
        if 'LTDebt/Eq' in grp: d_score += get_rank(grp['LTDebt/Eq'], False) * 0.05
        if 'Curr R' in grp:    d_score += get_rank(grp['Curr R'], True) * 0.03
        grp['Debt_Score'] = (d_score / 0.15).clip(0, 100).fillna(0)

        v_score = pd.Series(0, index=grp.index)
        if 'P/FCF' in grp: v_score += get_rank(grp['P/FCF'], False) * 0.16
        if 'PEG' in grp:   v_score += get_rank(grp['PEG'], False) * 0.12
        if 'P/E' in grp:   v_score += get_rank(grp['P/E'], False) * 0.05
        if 'P/S' in grp:   v_score += get_rank(grp['P/S'], False) * 0.05
        grp['Value_Score'] = (v_score / 0.38).clip(0, 100).fillna(0)

        penalty = np.where(grp.get('Short Float', 0) > 20, 15, 0)
        grp['Final_Score'] = ((grp['Profitability_Score']*0.45 + grp['Debt_Score']*0.15 + grp['Value_Score']*0.40) - penalty).clip(0, 100)
        score_dfs.append(grp)
        
    return pd.concat(score_dfs) if score_dfs else pd.DataFrame()

# =============================================================================
# MODULE 3: TTM EBIT AND BALANCE SHEET
# =============================================================================
def process_ttm_and_bs(chunk):
    res = []
    try:
        yq = YQTicker(chunk, validate=False) 
        try:
            df_inc = yq.income_statement(frequency='q', trailing=False)
            df_inc = df_inc.reset_index() if isinstance(df_inc, pd.DataFrame) else pd.DataFrame()
        except Exception: df_inc = pd.DataFrame()

        try:
            df_bs = yq.balance_sheet(frequency='q', trailing=False)
            df_bs = df_bs.reset_index() if isinstance(df_bs, pd.DataFrame) else pd.DataFrame()
        except Exception: df_bs = pd.DataFrame()

        if df_inc.empty: return []
        if 'asOfDate' in df_inc.columns: df_inc['asOfDate'] = pd.to_datetime(df_inc['asOfDate'])
        if not df_bs.empty and 'asOfDate' in df_bs.columns: df_bs['asOfDate'] = pd.to_datetime(df_bs['asOfDate'])

        tickers_in_chunk = df_inc['symbol'].unique()
        for s in tickers_in_chunk:
            metrics = {'Ticker': s}
            
            g_inc = df_inc[df_inc['symbol'] == s]
            candidates = ['OperatingIncome', 'EBIT', 'OperatingRevenue', 'NormalizedIncome']
            op_col = next((c for c in candidates if c in g_inc.columns), None)
            
            if op_col:
                ttm_ebit = g_inc.nlargest(4, 'asOfDate')[op_col].sum()
                metrics['TTM_EBIT'] = ttm_ebit
            else: metrics['TTM_EBIT'] = np.nan

            if not df_bs.empty:
                g_bs = df_bs[df_bs['symbol'] == s]
                if not g_bs.empty:
                    last_row = g_bs.nlargest(1, 'asOfDate').iloc[0]
                    d_cols = ['TotalDebt', 'LongTermDebtAndCapitalLeaseObligations', 'LongTermDebt']
                    d_col = next((c for c in d_cols if c in last_row.index), None)
                    metrics['Total_Debt'] = last_row[d_col] if d_col else 0
                    
                    c_cols = ['CashAndCashEquivalents', 'CashFinancial']
                    c_col = next((c for c in c_cols if c in last_row.index), None)
                    metrics['Cash'] = last_row[c_col] if c_col else 0
                else: metrics['Total_Debt'] = 0; metrics['Cash'] = 0
            else: metrics['Total_Debt'] = 0; metrics['Cash'] = 0
            
            res.append(metrics)
    except Exception: pass
    return res

def get_ttm_and_balance_sheet(tickers):
    print("\n=== [3/3] TTM DATA & EV CALCULATION ===")
    cache_file = 'cache_ttm_bs.csv'
    existing_data = pd.DataFrame()
    
    if os.path.exists(cache_file):
        try:
            existing_data = pd.read_csv(cache_file)
            existing_data['Ticker'] = existing_data['Ticker'].astype(str).str.strip()
        except Exception: pass

    existing_tickers = set(existing_data['Ticker'].tolist()) if not existing_data.empty else set()
    missing_tickers = [t for t in tickers if t not in existing_tickers]
    
    if not missing_tickers:
        print("✅ Data loaded from cache.")
        return existing_data[existing_data['Ticker'].isin(tickers)]

    print(f"⬇️ Fetching EBIT and Balance Sheet data for {len(missing_tickers)} stocks...")
    
    chunk_size = 50
    chunks = [missing_tickers[i:i+chunk_size] for i in range(0, len(missing_tickers), chunk_size)]
    new_res = []
    
    with ThreadPoolExecutor(max_workers=5) as exc:
        futures = [exc.submit(process_ttm_and_bs, c) for c in chunks]
        for f in tqdm(as_completed(futures), total=len(chunks), desc="Data Stream"):
            new_res.extend(f.result())
            
    df_new = pd.DataFrame(new_res)
    df_final = pd.concat([existing_data, df_new]).drop_duplicates(subset=['Ticker'], keep='last')
    try: df_final.to_csv(cache_file, index=False)
    except Exception: pass
    return df_final

# =============================================================================
# EV/EBIT INTEGRATION & FINAL SCORE UPDATE
# =============================================================================
def update_scores_with_ev_ebit(df):
    print("\n🔄 Calculating EV/EBIT Ratios and Updating Scores...")
    
    if 'Market Cap' in df.columns: mc_col = 'Market Cap'
    elif 'Market Cap.' in df.columns: mc_col = 'Market Cap.'
    else: return df

    df['MC_Numeric'] = clean_mc_vectorized(df[mc_col])
    df['Total_Debt'] = df['Total_Debt'].fillna(0)
    df['Cash'] = df['Cash'].fillna(0)
    
    df['Enterprise_Value'] = df['MC_Numeric'] + df['Total_Debt'] - df['Cash']
    df['TTM_EBIT'] = pd.to_numeric(df['TTM_EBIT'], errors='coerce')
    df['EV_EBIT'] = np.where(df['TTM_EBIT'] > 0, df['Enterprise_Value'] / df['TTM_EBIT'], np.nan)
    
    score_dfs = []
    for _, grp in df.groupby('Sector', group_keys=False):
        grp = grp.copy()
        
        if not grp['EV_EBIT'].isnull().all():
            ev_score = (1 - grp['EV_EBIT'].rank(pct=True, ascending=True)) * 100
        else: ev_score = 0
            
        grp['EV_EBIT_Score'] = ev_score.fillna(0)
        
        raw_val_score = (grp['Value_Score'] * 0.38) + (grp['EV_EBIT_Score'] * 0.15)
        grp['Value_Score'] = (raw_val_score / 0.53).clip(0, 100)
        
        penalty = np.where(grp.get('Short Float', 0) > 20, 15, 0)
        grp['Final_Score'] = ((grp['Profitability_Score']*0.45 + grp['Debt_Score']*0.15 + grp['Value_Score']*0.40) - penalty).clip(0, 100)
        score_dfs.append(grp)
        
    return pd.concat(score_dfs).sort_values('Final_Score', ascending=False)

# =============================================================================
# MAIN
# =============================================================================
def main():
    start_time = time.time()
    print("🚀 ADVANCED STOCK ANALYSIS BOT (Full Data Mode)...")
    
    # 1. Finviz Data
    df_main = get_finviz_data()
    if df_main.empty: 
        print("❌ No data found."); return

    # 2. Scoring
    df_scored = apply_quant_scoring(df_main)
    tickers = df_scored['Ticker'].unique().tolist()
    print(f"📋 Number of Stocks to Analyze: {len(tickers)}")
    
    # 3. TTM & Balance Sheet
    df_ttm_bs = get_ttm_and_balance_sheet(tickers)
    
    print("\n🔗 Merging tables...")
    final = df_scored.merge(df_ttm_bs, on='Ticker', how='left')
    
    # 4. EV/EBIT & Final Score
    final_updated = update_scores_with_ev_ebit(final)
    
    # --- FINAL COLUMN REORDERING ---
    calculated_cols = [
        'Final_Score', 'EV_EBIT', 'Profitability_Score', 'Debt_Score', 'Value_Score', 
        'EV_EBIT_Score', 'Enterprise_Value', 'TTM_EBIT', 
        'Total_Debt', 'Cash', 'MC_Numeric'
    ]
    
    meta_cols = ['Ticker', 'Company', 'Sector', 'Industry', 'Country', 'Exchange']
    meta_cols = [c for c in meta_cols if c in final_updated.columns]
    
    all_cols = final_updated.columns.tolist()
    exclude_cols = meta_cols + calculated_cols
    original_data_cols = [c for c in all_cols if c not in exclude_cols]
    
    score_cols_ordered = ['Final_Score', 'EV_EBIT', 'Profitability_Score', 'Debt_Score', 'Value_Score', 'TTM_EBIT', 'Enterprise_Value']
    score_cols_final = [c for c in score_cols_ordered if c in final_updated.columns]
    
    final_order = meta_cols + original_data_cols + score_cols_final
    final_report = final_updated[final_order]

    try:
        fname = 'Stock_Analysis_Report.xlsx'
        with pd.ExcelWriter(fname, engine='xlsxwriter') as writer:
            final_report.to_excel(writer, sheet_name='Analysis', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Analysis']
            
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white', 'border': 1})
            
            for col_num, value in enumerate(final_report.columns.values):
                worksheet.write(0, col_num, value, header_fmt)
                
                if value in meta_cols or value in score_cols_final:
                    worksheet.set_column(col_num, col_num, 14)
                else:
                    worksheet.set_column(col_num, col_num, 10)
            
        print(f"\n✅ PROCESS COMPLETE! Time taken: {(time.time() - start_time)/60:.1f} minutes.")
        print(f"📂 Report saved to: {os.path.abspath(fname)}")
        try:
            from google.colab import files
            files.download(fname)
        except ImportError: pass
        
    except Exception as e:
        print(f"❌ Save Error: {e}")
        final_report.to_csv("Stock_Analysis_Backup.csv", index=False)

if __name__ == "__main__":
    main()
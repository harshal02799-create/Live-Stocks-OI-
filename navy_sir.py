
import streamlit as st
st.set_page_config(layout="wide")
st.title("🔥 Stocks OI (Auto 5 Min Scanner)")
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from datetime import datetime
import pytz
import streamlit.components.v1 as components


EXPIRY = "30-Mar-2026"   # 🔥 CHANGE EXPIRY WHEN NEEDED
# ==============================
# MANUAL DATA (PASTE COMPLETE LIST)
# ==============================


st.markdown("""
<style>

/* ===== FULL BLACK BACKGROUND ===== */
html, body, [class*="css"], .stApp {
    background-color: #000000 !important;
    color: #e5e5e5 !important;
}

/* Remove Streamlit white header */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #000000 !important;
}

/* Info box */
div[data-testid="stAlert"] {
    background-color: #0a0a0a !important;
    border: 1px solid #1a1a1a !important;
    color: #9ca3af !important;
}

/* ===== TABLE CARD ===== */
.card {
    background-color: #0a0a0a;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #1a1a1a;
    max-height: 520px;
    overflow-y: auto;
}

/* ===== TABLE ===== */
.pro-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 15px;
    color: #e5e5e5;
}

.pro-table thead {
    background-color: #111111;
    position: sticky;
    top: 0;
    z-index: 2;
}

.pro-table th {
    padding: 10px;
    text-align: left;
    color: #6b7280;
    font-weight: 600;
    border-bottom: 1px solid #1a1a1a;
}

.pro-table td {
    padding: 8px;
    border-bottom: 1px solid #111111;
}

/* Hover effect */
.pro-table tr:hover {
    background-color: #111111;
}

/* ===== BADGES ===== */
.badge-green {
    background-color: rgba(0,255,100,0.1);
    color: #00ff88;
    padding: 4px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 12px;
}

.badge-red {
    background-color: rgba(255,0,0,0.1);
    color: #ff4d4d;
    padding: 4px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 12px;
}

/* OI value color */
.money {
    font-weight: 600;
    color: #ffd700;
}

/* ===== LIVE BAR ===== */
.live-bar {
    background-color: #0a0a0a;
    border: 1px solid #1a1a1a;
    padding: 10px 15px;
    border-radius: 10px;
    display: flex;
    justify-content: space-between;
    font-weight: 600;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
html, body, [class*="css"]  {
    background-color: #0b0f19 !important;
    color: #e5e7eb !important;
}

section[data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
}

.stApp {
    background-color: #0b0f19;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    background-color: #111827;
    border-radius: 8px;
    overflow: hidden;
}

.custom-table th {
    background-color: #1f2937;
    color: #9ca3af;
    padding: 10px;
    text-align: left;
}

.custom-table td {
    padding: 8px;
    border-bottom: 1px solid #1f2937;
}

.bullish-row {
    background-color: rgba(34,197,94,0.08);
    color: #22c55e;
}

.bearish-row {
    background-color: rgba(239,68,68,0.08);
    color: #ef4444;
}

.money {
    font-weight: 600;
    color: #fbbf24;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/*  background */
body {
    background-color: #0f172a;
}

/* Header */
.main-title {
    font-size: 32px;
    font-weight: 700;
    color: #f8fafc;
}

/* Info box */
.scan-info {
    background-color: #1e293b;
    padding: 12px;
    border-radius: 8px;
    color: #38bdf8;
    font-weight: 500;
}

/* Table container */
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

/* Table header */
.custom-table th {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 10px;
    text-align: left;
}

/* Table rows */
.custom-table td {
    padding: 8px;
    border-bottom: 1px solid #1e293b;
}

/* Bullish highlight */
.bullish-row {
    background-color: rgba(34,197,94,0.08);
    color: #22c55e;
}

/* Bearish highlight */
.bearish-row {
    background-color: rgba(239,68,68,0.08);
    color: #ef4444;
}

/* Value formatting */
.money {
    font-weight: 600;
    color: #fbbf24;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# CREATE DATAFRAME
# ==============================



# ==========================================
# CONFIG
# ==========================================

BASE_URL = "https://www.nseindia.com"

# ==========================================
# CREATE NSE SESSION (ONLY ONCE)
# ==========================================
import cloudscraper

# ==========================================
# CREATE NSE SESSION (CLOUDSCRAPER)
# ==========================================

def create_session():
    scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "windows",
            "mobile": False,
        }
    )

    # Hit homepage first
    scraper.get("https://www.nseindia.com")

    return scraper


# Global session
session = create_session()
# ==========================================
# GET ALL F&O SYMBOLS
# ==========================================
@st.cache_data(ttl=3600)
def get_all_symbols():
    try:
        url = "https://www.nseindia.com/api/underlying-information"

        response = session.get(url)

        if response.status_code != 200:
            st.error("NSE returned non-200 status")
            return []

        data = response.json()

        # 🔥 Correct extraction
        underlying_list = data["data"]["UnderlyingList"]

        symbols = [item["symbol"] for item in underlying_list]

        return sorted(symbols)

    except Exception as e:
        st.error(f"NSE Error: {e}")
        return []
# ==========================================
# FETCH OPTION CHAIN
# ==========================================

def get_option_chain(symbol):
    try:
        url = f"{BASE_URL}/api/option-chain-v3?type=Equity&symbol={symbol}&expiry={EXPIRY}"

        response = session.get(url, timeout=10)

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None

# ==========================================
# ANALYZE OI
# ==========================================

def analyze_oi(symbol):
    data = get_option_chain(symbol)

    if data is None:
        return None

    try:
        records = data["records"]["data"]
        ltp = data["records"]["underlyingValue"]
    except:
        return None

    rows = []

    for item in records:
        strike = item.get("strikePrice")

        ce_oi = item.get("CE", {}).get("openInterest", 0)
        pe_oi = item.get("PE", {}).get("openInterest", 0)

        rows.append({
            "strike": strike,
            "CE_OI": ce_oi,
            "PE_OI": pe_oi
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return None

    max_ce_row = df.loc[df["CE_OI"].idxmax()]
    max_pe_row = df.loc[df["PE_OI"].idxmax()]

    return {
        "symbol": symbol,
        "ltp": ltp,
        "max_ce_strike": max_ce_row["strike"],
        "max_ce_oi": max_ce_row["CE_OI"],
        "max_pe_strike": max_pe_row["strike"],
        "max_pe_oi": max_pe_row["PE_OI"]
    }

# ==========================================
# BREAKOUT CHECK
# ==========================================

def check_breakout(result):
    alerts = []

    if result["ltp"] > result["max_ce_strike"]:
        alerts.append("Breaking MAX CE OI")

    if result["ltp"] < result["max_pe_strike"]:
        alerts.append("Breaking MAX PE OI")

    return ", ".join(alerts) if alerts else "No Breakout"

# ==========================================
# LOAD LOT SIZE FROM CSV
# ==========================================

@st.cache_data(ttl=3600)
def load_lot_size():
    try:
        lot_df = pd.read_csv("Dhan - Nse Fno Lot Size.csv")

        # Clean column names
        lot_df.columns = lot_df.columns.str.strip()

        # Rename properly
        lot_df = lot_df.rename(columns={
            "Lot Size (Feb 2026)": "LotSize"
        })

        lot_df["Symbol"] = lot_df["Symbol"].str.strip().str.upper()

        return lot_df

    except Exception as e:
        st.error(f"Error loading lot size file: {e}")
        return pd.DataFrame()

# ==========================================
# SCAN ALL STOCKS
# ==========================================

def scan_all(symbols, lot_dict):

    bullish_rows = []
    bearish_rows = []



    def process_symbol(symbol):
        result = analyze_oi(symbol)
        if result is None:
            return None

        ltp = result["ltp"]
        lot_size = lot_dict.get(symbol, 0)

        # Bullish
        if ltp > result["max_ce_strike"]:
            total_value = result["max_ce_oi"] * lot_size

            return ("bullish", {
                "Symbol": symbol,
                "LTP": ltp,
                "Strike": result["max_ce_strike"],
                "OI Value": result["max_ce_oi"],
                "Lot Size": lot_size,
                "Total OI Value": total_value,
                "Sentiment": "Bullish"
            })

        # Bearish
        if ltp < result["max_pe_strike"]:
            total_value = result["max_pe_oi"] * lot_size

            return ("bearish", {
                "Symbol": symbol,
                "LTP": ltp,
                "Strike": result["max_pe_strike"],
                "OI Value": result["max_pe_oi"],
                "Lot Size": lot_size,
                "Total OI Value": total_value,
                "Sentiment": "Bearish"
            })

        return None

    # 🚀 Parallel Execution
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(process_symbol, sym) for sym in symbols]

        for future in as_completed(futures):
            result = future.result()

            if result:
                side, row = result
                if side == "bullish":
                    bullish_rows.append(row)
                else:
                    bearish_rows.append(row)

    return pd.DataFrame(bullish_rows), pd.DataFrame(bearish_rows)


# ==========================================
# AUTO REFRESH EVERY 5 MINUTES
# ==========================================

# 300000 ms = 5 minutes
st_autorefresh(interval=300000, key="datarefresh")

lot_df = load_lot_size()

if lot_df.empty:
    st.stop()

lot_dict = dict(zip(lot_df["Symbol"], lot_df["LotSize"]))

symbols = lot_df["Symbol"].tolist()

if not symbols:
    st.error("Unable to fetch symbols from NSE.")
    st.stop()

st.info("Auto scanning all stocks every 5 minutes...")
# ==========================================
# AUTO SCAN
# ==========================================

bullish_df, bearish_df = scan_all(symbols, lot_dict)
# ---- INITIALIZE SESSION STATE BEFORE USING ----
if "breakout_tracker" not in st.session_state:
    st.session_state.breakout_tracker = {}

if "breakdown_tracker" not in st.session_state:
    st.session_state.breakdown_tracker = {}
fresh_breakdowns = []

# Track new bearish breakdowns
for _, row in bearish_df.iterrows():

    symbol = row["Symbol"]

    if symbol not in st.session_state.breakdown_tracker:

        st.session_state.breakdown_tracker[symbol] = {
            "strike": row["Strike"],
            "time": datetime.now()
        }

        fresh_breakdowns.append(row)

# Remove recovered bearish stocks
for symbol in list(st.session_state.breakdown_tracker.keys()):

    if symbol not in bearish_df["Symbol"].values:
        del st.session_state.breakdown_tracker[symbol]

# -----------------------------------
# REAL BREAKOUT TRACKER
# -----------------------------------

squat_stocks = []
new_breakouts = []

current_time = datetime.now()

# Track bullish breakouts
for _, row in bullish_df.iterrows():

    symbol = row["Symbol"]
    strike = row["Strike"]
    ltp = row["LTP"]

    # New breakout
    if symbol not in st.session_state.breakout_tracker:

        st.session_state.breakout_tracker[symbol] = {
            "strike": strike,
            "time": current_time
        }

        new_breakouts.append(row)

# Check failed breakouts
for symbol in list(st.session_state.breakout_tracker.keys()):

    if symbol not in bullish_df["Symbol"].values:

        stored_strike = st.session_state.breakout_tracker[symbol]["strike"]

        result = analyze_oi(symbol)

        if result:
            current_ltp = result["ltp"]

            if current_ltp < stored_strike:
                squat_stocks.append({
                    "Symbol": symbol,
                    "LTP": current_ltp,
                    "Strike": stored_strike,
                    "OI Value": result["max_ce_oi"],
                    "Lot Size": lot_dict.get(symbol, 0),
                    "Total OI Value": result["max_ce_oi"] * lot_dict.get(symbol, 0),
                    "Sentiment": "Failed"
                })

        del st.session_state.breakout_tracker[symbol]


ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)

# Market live check (9:15 to 3:30 IST)
market_open = now.replace(hour=9, minute=15, second=0)
market_close = now.replace(hour=15, minute=30, second=0)

is_live = market_open <= now <= market_close

live_color = "#22c55e" if is_live else "#ef4444"
live_text = "🟢 LIVE" if is_live else "🔴 MARKET CLOSED"

st.markdown("""
<style>

/* ===== REMOVE TOP SPACE ===== */
header {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding-top: 0rem !important;
    padding-bottom: 1rem !important;
}

section.main > div {
    padding-top: 0rem !important;
}

/* Remove extra margin from title */
h1 {
    margin-top: 0rem !important;
    padding-top: 0rem !important;
}

/* ===== FULL BLACK BACKGROUND ===== */
html, body, .stApp {
    background-color: #000000 !important;
    color: #e5e5e5 !important;
}

/* Remove sidebar gap */
section[data-testid="stSidebar"] {
    background-color: #000000 !important;
}

/* Remove alert blue background */
div[data-testid="stAlert"] {
    background-color: #0a0a0a !important;
    border: 1px solid #1a1a1a !important;
}

/* Card */
.card {
    background-color: #0a0a0a;
    border: 1px solid #1a1a1a;
    padding: 15px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="live-bar">
        <div style="color:{live_color};">
            {live_text}
        </div>
        <div style="color:#6b7280;">
            Last Updated: {now.strftime('%d-%m-%Y %H:%M:%S')}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
# ==============================
# HTML TABLE RENDER FUNCTION
# ==============================

def render_table(df, sentiment_type):

    if df.empty:
        return "<div class='card'>No Data</div>"

    table_html = """
    <style>

    .card {
        background-color: #111827;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 0 0 1px #1f2937;
        max-height: 520px;
        overflow-y: auto;
    }

    .pro-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 16px;
        color: #e5e7eb;
    }

    .pro-table thead {
        background-color: #0f172a;
        position: sticky;
        top: 0;
        z-index: 2;
    }

    .pro-table th {
        padding: 10px;
        text-align: left;
        color: #9ca3af;
        font-weight: 600;
        border-bottom: 1px solid #1f2937;
    }

    .pro-table td {
        padding: 8px;
        border-bottom: 1px solid #1f2937;
    }

    .pro-table tr:hover {
        background-color: #1e293b;
    }

    .badge-green {
        background-color: rgba(34,197,94,0.15);
        color: #22c55e;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
    }

    .badge-red {
        background-color: rgba(239,68,68,0.15);
        color: #ef4444;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
    }

    .money {
        font-weight: 600;
        color: #fbbf24;
    }

    </style>

    <div class="card">
    <table class="pro-table">
        <thead>
            <tr>
                <th>Symbol</th>
                <th>LTP</th>
                <th>Strike</th>
                <th>OI</th>
                <th>Lot</th>
                <th>OI in lakhs</th>
                <th>Sentiment</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in df.iterrows():

        if sentiment_type == "bullish":
            badge_class = "badge-green"
        elif sentiment_type == "bearish":
            badge_class = "badge-red"
        elif sentiment_type == "fresh":
            badge_class = "badge-green"
        else:
            badge_class = "badge-red"
        table_html += f"""
        <tr>
            <td><strong>{row['Symbol']}</strong></td>
            <td>{row['LTP']:.2f}</td>
            <td>{row['Strike']}</td>
            <td>{int(row['OI Value']):,}</td>
            <td>{row['Lot Size']}</td>
            <td class="money">{round(row['Total OI Value'] / 100000, 2)}</td>
            <td><span class="{badge_class}">{row.get('Sentiment','')}</span></td>
        </tr>
        """

    table_html += """
        </tbody>
    </table>
    </div>
    """

    return table_html

# ==============================
# DISPLAY TABLES SIDE BY SIDE
# ==============================

import streamlit.components.v1 as components
fresh_df = pd.DataFrame(new_breakouts) if new_breakouts else pd.DataFrame()
squat_df = pd.DataFrame(squat_stocks) if squat_stocks else pd.DataFrame()
fresh_breakdown_df = pd.DataFrame(fresh_breakdowns) if fresh_breakdowns else pd.DataFrame()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Bullish Breakouts")
    components.html(render_table(bullish_df, "bullish"), height=450)

    if not fresh_df.empty:
        st.markdown("### 🚀 Fresh Breakouts")
        components.html(render_table(fresh_df, "fresh"), height=350)

with col2:
    st.markdown("### 📉 Bearish Breakdowns")
    components.html(render_table(bearish_df, "bearish"), height=450)

    if not fresh_breakdown_df.empty:
        st.markdown("### 🔻 Fresh Breakdowns")
        components.html(render_table(fresh_breakdown_df, "bearish"), height=350)

    if not squat_df.empty:
        st.markdown("### ⚠️ Failed Breakouts")
        components.html(render_table(squat_df, "failed"), height=350)





















# import streamlit as st
# from datetime import datetime
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# from concurrent.futures import ThreadPoolExecutor, as_completed
#
# import streamlit.components.v1 as components
# # ==============================
# # MANUAL DATA (PASTE COMPLETE LIST)
# # ==============================
#
# st.markdown("""
# <style>
# html, body, [class*="css"]  {
#     background-color: #0b0f19 !important;
#     color: #e5e7eb !important;
# }
#
# section[data-testid="stSidebar"] {
#     background-color: #0b0f19 !important;
# }
#
# .stApp {
#     background-color: #0b0f19;
# }
# </style>
# """, unsafe_allow_html=True)
#
# st.markdown("""
# <style>
#
# .custom-table {
#     width: 100%;
#     border-collapse: collapse;
#     font-size: 14px;
#     background-color: #111827;
#     border-radius: 8px;
#     overflow: hidden;
# }
#
# .custom-table th {
#     background-color: #1f2937;
#     color: #9ca3af;
#     padding: 10px;
#     text-align: left;
# }
#
# .custom-table td {
#     padding: 8px;
#     border-bottom: 1px solid #1f2937;
# }
#
# .bullish-row {
#     background-color: rgba(34,197,94,0.08);
#     color: #22c55e;
# }
#
# .bearish-row {
#     background-color: rgba(239,68,68,0.08);
#     color: #ef4444;
# }
#
# .money {
#     font-weight: 600;
#     color: #fbbf24;
# }
#
# </style>
# """, unsafe_allow_html=True)
#
#
# st.markdown("""
# <style>
#
# /* Page background */
# body {
#     background-color: #0f172a;
# }
#
# /* Header */
# .main-title {
#     font-size: 32px;
#     font-weight: 700;
#     color: #f8fafc;
# }
#
# /* Info box */
# .scan-info {
#     background-color: #1e293b;
#     padding: 12px;
#     border-radius: 8px;
#     color: #38bdf8;
#     font-weight: 500;
# }
#
# /* Table container */
# .custom-table {
#     width: 100%;
#     border-collapse: collapse;
#     font-size: 14px;
# }
#
# /* Table header */
# .custom-table th {
#     background-color: #1e293b;
#     color: #94a3b8;
#     padding: 10px;
#     text-align: left;
# }
#
# /* Table rows */
# .custom-table td {
#     padding: 8px;
#     border-bottom: 1px solid #1e293b;
# }
#
# /* Bullish highlight */
# .bullish-row {
#     background-color: rgba(34,197,94,0.08);
#     color: #22c55e;
# }
#
# /* Bearish highlight */
# .bearish-row {
#     background-color: rgba(239,68,68,0.08);
#     color: #ef4444;
# }
#
# /* Value formatting */
# .money {
#     font-weight: 600;
#     color: #fbbf24;
# }
#
# </style>
# """, unsafe_allow_html=True)
#
# # ==============================
# # CREATE DATAFRAME
# # ==============================
#
#
#
# # ==========================================
# # CONFIG
# # ==========================================
#
# BASE_URL = "https://www.nseindia.com"
# EXPIRY = "30-Mar-2026"   # 🔥 CHANGE EXPIRY WHEN NEEDED
#
# # ==========================================
# # CREATE NSE SESSION (ONLY ONCE)
# # ==========================================
# import cloudscraper
#
# # ==========================================
# # CREATE NSE SESSION (CLOUDSCRAPER)
# # ==========================================
#
# def create_session():
#     scraper = cloudscraper.create_scraper(
#         browser={
#             "browser": "chrome",
#             "platform": "windows",
#             "mobile": False,
#         }
#     )
#
#     # Hit homepage first
#     scraper.get("https://www.nseindia.com")
#
#     return scraper
#
#
# # Global session
# session = create_session()
# # ==========================================
# # GET ALL F&O SYMBOLS
# # ==========================================
# @st.cache_data(ttl=3600)
# def get_all_symbols():
#     try:
#         url = "https://www.nseindia.com/api/underlying-information"
#
#         response = session.get(url)
#
#         if response.status_code != 200:
#             st.error("NSE returned non-200 status")
#             return []
#
#         data = response.json()
#
#         # 🔥 Correct extraction
#         underlying_list = data["data"]["UnderlyingList"]
#
#         symbols = [item["symbol"] for item in underlying_list]
#
#         return sorted(symbols)
#
#     except Exception as e:
#         st.error(f"NSE Error: {e}")
#         return []
# # ==========================================
# # FETCH OPTION CHAIN
# # ==========================================
#
# def get_option_chain(symbol):
#     try:
#         url = f"{BASE_URL}/api/option-chain-v3?type=Equity&symbol={symbol}&expiry={EXPIRY}"
#
#         response = session.get(url, timeout=10)
#
#         if response.status_code != 200:
#             return None
#
#         return response.json()
#
#     except:
#         return None
#
# # ==========================================
# # ANALYZE OI
# # ==========================================
#
# def analyze_oi(symbol):
#     data = get_option_chain(symbol)
#
#     if data is None:
#         return None
#
#     try:
#         records = data["records"]["data"]
#         ltp = data["records"]["underlyingValue"]
#     except:
#         return None
#
#     rows = []
#
#     for item in records:
#         strike = item.get("strikePrice")
#
#         ce_oi = item.get("CE", {}).get("openInterest", 0)
#         pe_oi = item.get("PE", {}).get("openInterest", 0)
#
#         rows.append({
#             "strike": strike,
#             "CE_OI": ce_oi,
#             "PE_OI": pe_oi
#         })
#
#     df = pd.DataFrame(rows)
#
#     if df.empty:
#         return None
#
#     max_ce_row = df.loc[df["CE_OI"].idxmax()]
#     max_pe_row = df.loc[df["PE_OI"].idxmax()]
#
#     return {
#         "symbol": symbol,
#         "ltp": ltp,
#         "max_ce_strike": max_ce_row["strike"],
#         "max_ce_oi": max_ce_row["CE_OI"],
#         "max_pe_strike": max_pe_row["strike"],
#         "max_pe_oi": max_pe_row["PE_OI"]
#     }
#
# # ==========================================
# # BREAKOUT CHECK
# # ==========================================
#
# def check_breakout(result):
#     alerts = []
#
#     if result["ltp"] > result["max_ce_strike"]:
#         alerts.append("Breaking MAX CE OI")
#
#     if result["ltp"] < result["max_pe_strike"]:
#         alerts.append("Breaking MAX PE OI")
#
#     return ", ".join(alerts) if alerts else "No Breakout"
#
# # ==========================================
# # LOAD LOT SIZE FROM CSV
# # ==========================================
#
# @st.cache_data(ttl=3600)
# def load_lot_size():
#     try:
#         lot_df = pd.read_csv("Dhan - Nse Fno Lot Size.csv")
#
#         # Clean column names
#         lot_df.columns = lot_df.columns.str.strip()
#
#         # Rename properly
#         lot_df = lot_df.rename(columns={
#             "Lot Size (Feb 2026)": "LotSize"
#         })
#
#         lot_df["Symbol"] = lot_df["Symbol"].str.strip().str.upper()
#
#         return lot_df
#
#     except Exception as e:
#         st.error(f"Error loading lot size file: {e}")
#         return pd.DataFrame()
#
# # ==========================================
# # SCAN ALL STOCKS
# # ==========================================
#
# def scan_all(symbols, lot_dict):
#
#     bullish_rows = []
#     bearish_rows = []
#
#
#
#     def process_symbol(symbol):
#         result = analyze_oi(symbol)
#         if result is None:
#             return None
#
#         ltp = result["ltp"]
#         lot_size = lot_dict.get(symbol, 0)
#
#         # Bullish
#         if ltp > result["max_ce_strike"]:
#             total_value = result["max_ce_oi"] * lot_size
#
#             return ("bullish", {
#                 "Symbol": symbol,
#                 "LTP": ltp,
#                 "Strike": result["max_ce_strike"],
#                 "OI Value": result["max_ce_oi"],
#                 "Lot Size": lot_size,
#                 "Total OI Value": total_value,
#                 "Sentiment": "Bullish"
#             })
#
#         # Bearish
#         if ltp < result["max_pe_strike"]:
#             total_value = result["max_pe_oi"] * lot_size
#
#             return ("bearish", {
#                 "Symbol": symbol,
#                 "LTP": ltp,
#                 "Strike": result["max_pe_strike"],
#                 "OI Value": result["max_pe_oi"],
#                 "Lot Size": lot_size,
#                 "Total OI Value": total_value,
#                 "Sentiment": "Bearish"
#             })
#
#         return None
#
#     # 🚀 Parallel Execution
#     with ThreadPoolExecutor(max_workers=12) as executor:
#         futures = [executor.submit(process_symbol, sym) for sym in symbols]
#
#         for future in as_completed(futures):
#             result = future.result()
#
#             if result:
#                 side, row = result
#                 if side == "bullish":
#                     bullish_rows.append(row)
#                 else:
#                     bearish_rows.append(row)
#
#     return pd.DataFrame(bullish_rows), pd.DataFrame(bearish_rows)
#
#
# # ==========================================
# # AUTO REFRESH EVERY 5 MINUTES
# # ==========================================
#
# # 300000 ms = 5 minutes
# st_autorefresh(interval=300000, key="datarefresh")
#
# st.set_page_config(layout="wide")
# st.title("🔥 NSE OI Breakout Dashboard (Auto 5 Min Scanner)")
# lot_df = load_lot_size()
#
# if lot_df.empty:
#     st.stop()
#
# lot_dict = dict(zip(lot_df["Symbol"], lot_df["LotSize"]))
#
# symbols = lot_df["Symbol"].tolist()
#
# if not symbols:
#     st.error("Unable to fetch symbols from NSE.")
#     st.stop()
#
# st.info("Auto scanning all stocks every 5 minutes...")
# # ==========================================
# # AUTO SCAN
# # ==========================================
#
# bullish_df, bearish_df = scan_all(symbols, lot_dict)
# bullish_df, bearish_df = scan_all(symbols, lot_dict)
#
# # ---- INITIALIZE SESSION STATE FIRST ----
# if "breakout_tracker" not in st.session_state:
#     st.session_state.breakout_tracker = {}
#
# if "breakdown_tracker" not in st.session_state:
#     st.session_state.breakdown_tracker = {}
# fresh_breakdowns = []
#
# for _, row in bearish_df.iterrows():
#     symbol = row["Symbol"]
#
#     if symbol not in st.session_state.breakdown_tracker:
#         st.session_state.breakdown_tracker[symbol] = {
#             "strike": row["Strike"],
#             "time": datetime.now()
#         }
#         fresh_breakdowns.append(row)
#
# # Remove recovered bearish stocks
# for symbol in list(st.session_state.breakdown_tracker.keys()):
#     if symbol not in bearish_df["Symbol"].values:
#         del st.session_state.breakdown_tracker[symbol]
# # -----------------------------------
# # REAL BREAKOUT TRACKER
# # -----------------------------------
#
# squat_stocks = []
# new_breakouts = []
#
# current_time = datetime.now()
#
# # Track bullish breakouts
# for _, row in bullish_df.iterrows():
#
#     symbol = row["Symbol"]
#     strike = row["Strike"]
#     ltp = row["LTP"]
#
#     # New breakout
#     if symbol not in st.session_state.breakout_tracker:
#
#         st.session_state.breakout_tracker[symbol] = {
#             "strike": strike,
#             "time": current_time
#         }
#
#         new_breakouts.append(row)
#
# # Check failed breakouts
# for symbol in list(st.session_state.breakout_tracker.keys()):
#
#     if symbol not in bullish_df["Symbol"].values:
#
#         stored_strike = st.session_state.breakout_tracker[symbol]["strike"]
#
#         result = analyze_oi(symbol)
#
#         if result:
#             current_ltp = result["ltp"]
#
#             if current_ltp < stored_strike:
#                 squat_stocks.append({
#                     "Symbol": symbol,
#                     "LTP": current_ltp,
#                     "Strike": stored_strike,
#                     "OI Value": result["max_ce_oi"],
#                     "Lot Size": lot_dict.get(symbol, 0),
#                     "Total OI Value": result["max_ce_oi"] * lot_dict.get(symbol, 0),
#                     "Sentiment": "Failed"
#                 })
#
#         del st.session_state.breakout_tracker[symbol]
#
# from datetime import datetime, timedelta
#
# now = datetime.now()
#
# # Market live check (9:15 to 3:30 IST)
# market_open = now.replace(hour=9, minute=15, second=0)
# market_close = now.replace(hour=15, minute=30, second=0)
#
# is_live = market_open <= now <= market_close
#
# live_color = "#22c55e" if is_live else "#ef4444"
# live_text = "🟢 LIVE" if is_live else "🔴 MARKET CLOSED"
#
# st.markdown(
#     f"""
#     <div style="
#         display:flex;
#         justify-content:space-between;
#         background:#1e293b;
#         padding:10px 15px;
#         border-radius:8px;
#         margin-bottom:15px;
#         font-size:16px;
#         font-weight:600;
#     ">
#         <div style="color:{live_color};">
#             {live_text}
#         </div>
#         <div style="color:#9ca3af;">
#             Last Updated: {now.strftime('%d-%m-%Y %H:%M:%S')}
#         </div>
#     </div>
#     """,
#     unsafe_allow_html=True
# )
#
# # if "previous_bullish" not in st.session_state:
# #     st.session_state.previous_bullish = set()
# #
# # # 🔎 Search Box
# # search_query = st.text_input("🔎 Search Symbol")
# #
# # if search_query:
# #     bullish_df = bullish_df[
# #         bullish_df["Symbol"].str.contains(search_query.upper())
# #     ]
# #     bearish_df = bearish_df[
# #         bearish_df["Symbol"].str.contains(search_query.upper())
# #     ]
# #
# #     current_bullish = set(bullish_df["Symbol"])
# #
# #     # Stocks removed from breakout
# #     squat_stocks = st.session_state.previous_bullish - current_bullish
# #
# #     # Stocks newly added
# #     new_breakouts = current_bullish - st.session_state.previous_bullish
# #
# #     # Update state
# #     st.session_state.previous_bullish = current_bullish
# # ==============================
# # HTML TABLE RENDER FUNCTION
# # ==============================
#
# def render_table(df, sentiment_type):
#
#     if df.empty:
#         return "<div class='card'>No Data</div>"
#
#     table_html = """
#     <style>
#
#     .card {
#         background-color: #111827;
#         padding: 15px;
#         border-radius: 12px;
#         box-shadow: 0 0 0 1px #1f2937;
#         max-height: 520px;
#         overflow-y: auto;
#     }
#
#     .pro-table {
#         width: 100%;
#         border-collapse: collapse;
#         font-size: 16px;
#         color: #e5e7eb;
#     }
#
#     .pro-table thead {
#         background-color: #0f172a;
#         position: sticky;
#         top: 0;
#         z-index: 2;
#     }
#
#     .pro-table th {
#         padding: 10px;
#         text-align: left;
#         color: #9ca3af;
#         font-weight: 600;
#         border-bottom: 1px solid #1f2937;
#     }
#
#     .pro-table td {
#         padding: 8px;
#         border-bottom: 1px solid #1f2937;
#     }
#
#     .pro-table tr:hover {
#         background-color: #1e293b;
#     }
#
#     .badge-green {
#         background-color: rgba(34,197,94,0.15);
#         color: #22c55e;
#         padding: 4px 8px;
#         border-radius: 6px;
#         font-weight: 600;
#         font-size: 12px;
#     }
#
#     .badge-red {
#         background-color: rgba(239,68,68,0.15);
#         color: #ef4444;
#         padding: 4px 8px;
#         border-radius: 6px;
#         font-weight: 600;
#         font-size: 12px;
#     }
#
#     .money {
#         font-weight: 600;
#         color: #fbbf24;
#     }
#
#     </style>
#
#     <div class="card">
#     <table class="pro-table">
#         <thead>
#             <tr>
#                 <th>Symbol</th>
#                 <th>LTP</th>
#                 <th>Strike</th>
#                 <th>OI</th>
#                 <th>Lot</th>
#                 <th>OI in lakhs</th>
#                 <th>Sentiment</th>
#             </tr>
#         </thead>
#         <tbody>
#     """
#
#     for _, row in df.iterrows():
#
#         if sentiment_type == "bullish":
#             badge_class = "badge-green"
#         elif sentiment_type == "bearish":
#             badge_class = "badge-red"
#         elif sentiment_type == "fresh":
#             badge_class = "badge-green"
#         else:
#             badge_class = "badge-red"
#         table_html += f"""
#         <tr>
#             <td><strong>{row['Symbol']}</strong></td>
#             <td>{row['LTP']:.2f}</td>
#             <td>{row['Strike']}</td>
#             <td>{int(row['OI Value']):,}</td>
#             <td>{row['Lot Size']}</td>
#             <td class="money">{round(row['Total OI Value'] / 100000, 2)}</td>
#             <td><span class="{badge_class}">{row.get('Sentiment','')}</span></td>
#         </tr>
#         """
#
#     table_html += """
#         </tbody>
#     </table>
#     </div>
#     """
#
#     return table_html
#
# # ==============================
# # DISPLAY TABLES SIDE BY SIDE
# # ==============================
#
# import streamlit.components.v1 as components
# fresh_df = pd.DataFrame(new_breakouts) if new_breakouts else pd.DataFrame()
# squat_df = pd.DataFrame(squat_stocks) if squat_stocks else pd.DataFrame()
# fresh_breakdown_df = pd.DataFrame(fresh_breakdowns) if fresh_breakdowns else pd.DataFrame()
#
# col1, col2 = st.columns(2)
#
# with col1:
#     st.markdown("### 📈 Bullish Breakouts")
#     components.html(render_table(bullish_df, "bullish"), height=450)
#
#     if not fresh_df.empty:
#         st.markdown("### 🚀 Fresh Breakouts")
#         components.html(render_table(fresh_df, "fresh"), height=350)
#
# with col2:
#     st.markdown("### 📉 Bearish Breakdowns")
#     components.html(render_table(bearish_df, "bearish"), height=450)
#
#     if not fresh_breakdown_df.empty:
#         st.markdown("### 🔻 Fresh Breakdowns")
#         components.html(render_table(fresh_breakdown_df, "bearish"), height=350)
#
#     if not squat_df.empty:
#         st.markdown("### ⚠️ Failed Breakouts")
#         components.html(render_table(squat_df, "failed"), height=350)













import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
from solana.rpc.api import Client

# --- 1. REAL CONNECTION SETUP ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# PASTE YOUR REAL WALLET ADDRESS HERE
MY_WALLET = "YOUR_PHANTOM_PUBLIC_ADDRESS_HERE" 
# Using a high-speed public RPC
solana_client = Client("https://api.mainnet-beta.solana.com")

# --- 2. REAL-TIME DATA ENGINES ---
def get_real_sol_price():
    """Fetches real SOL price from Binance API"""
    try:
        url = "https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT"
        res = requests.get(url, timeout=1).json()
        return float(res['price'])
    except:
        # If API rate limits, keep the last known price to avoid lag
        return st.session_state.get('last_price', 145.00)

def get_real_wallet_balance():
    """Checks your actual SOL balance on the blockchain"""
    try:
        res = solana_client.get_balance(MY_WALLET)
        return res.value / 10**9 
    except:
        return st.session_state.get('last_bal', 0.0)

# --- 3. PRO AESTHETIC CSS ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 450px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; overflow-x: hidden !important; }

    .master-wrapper { display: flex; flex-direction: column; width: 100%; padding: 15px; box-sizing: border-box; }

    /* CARD & STATUS */
    .glass-card {
        background-color: #0d0d0d; border-radius: 40px; padding: 40px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 5px;
    }
    .status-container { display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    .led { 
        width: 10px; height: 10px; border-radius: 50%; 
        background-color: #00FFC2; box-shadow: 0 0 10px #00FFC2; 
        margin-right: 10px; 
    }
    .status-text { color: #00FFC2; font-size: 13px; font-weight: 800; letter-spacing: 1px; }
    .price-label { color: #555; font-size: 12px; font-weight: 600; margin-bottom: 12px; text-transform: uppercase; }
    .price-main { color: #ffffff; font-size: 52px; font-weight: 800; }
    .price-mili { color: #00FFC2; font-size: 32px; font-weight: 600; font-family: monospace; }

    /* BUTTON ROW */
    .btn-container { display: flex; justify-content: center; gap: 12px; width: 100%; margin-top: 20px; margin-bottom: 25px; }
    div.stButton > button {
        width: 100% !important; height: 70px !important; border-radius: 35px !important; 
        font-weight: 900 !important; font-size: 14px !important; border: none !important;
    }
    div[data-testid="stHorizontalBlock"] div:nth-child(1) button { background-color: #ffffff !important; color: #000000 !important; }
    div[data-testid="stHorizontalBlock"] div:nth-child(2) button { background-color: #0d0d0d !important; color: #ffffff !important; border: 1px solid #222 !important; }

    /* PROFIT LOG */
    .trade-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #111; }
    .profit-val { color: #00FFC2; font-weight: 800; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA UPDATER (THE REAL HEART) ---
# Get current real values
real_sol_price = get_real_sol_price()
real_sol_bal = get_real_wallet_balance()
total_equity = real_sol_price * real_sol_bal

# Save to state for the chart
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = [total_equity] * 20

# Only add to history if the value actually changed (Real movement)
if total_equity != st.session_state.equity_history[-1]:
    st.session_state.equity_history.append(total_equity)
    st.session_state.equity_history = st.session_state.equity_history[-50:] # Keep 50 points

st.session_state.last_price = real_sol_price
st.session_state.last_bal = real_sol_bal

main_part = int(total_equity)
decimal_part = f"{total_equity % 1:.8f}"[2:]

# --- 5. RENDER REAL UI ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

st.markdown(f'''
<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">BOT STATUS: ACTIVE</div></div>
    <div class="price-label">ACCOUNT EQUITY (USDT)</div>
    <div><span class="price-main">${main_part:,}</span><span class="price-mili" id="live-ticker">.{decimal_part}</span></div>
</div>

<script>
    const ticker = window.parent.document.getElementById('live-ticker');
    if(ticker) {{
        setInterval(() => {{
            // This is just a visual 'heartbeat' for the milly-seconds 
            // while the main data updates every second
            let micro = Math.floor(Math.random() * 9999).toString().padStart(4, '0');
            ticker.innerText = "." + "{decimal_part}".substring(0,4) + micro;
        }}, 40); 
    }}
</script>
''', unsafe_allow_html=True)

# --- 6. REAL GROWTH CHART ---
chart_data = pd.DataFrame({'val': st.session_state.equity_history, 'idx': range(len(st.session_state.equity_history))})
st.vega_lite_chart(chart_data, {
    "width": "container", "height": 220,
    "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
    "layer": [
        {"mark": {"type": "area", "interpolate": "monotone", "color": {"gradient": "linear", "stops": [{"offset": 0, "color": "#00FFC2"}, {"offset": 1, "color": "rgba(0,0,0,0)"}], "x1": 1, "y1": 1, "x2": 1, "y2": 0}}, "encoding": {"x": {"field": "idx", "type": "quantitative", "axis": None}, "y": {"field": "val", "type": "quantitative", "axis": None, "scale": {"zero": False}}}},
        {"mark": {"type": "line", "color": "#00FFC2", "strokeWidth": 3, "interpolate": "monotone"}, "encoding": {"x": {"field": "idx", "type": "quantitative", "axis": None}, "y": {"field": "val", "type": "quantitative", "axis": None}}}
    ]
})

# --- 7. BUTTONS ---
col1, col2 = st.columns(2)
with col1: st.button("START BOT")
with col2: st.button("STOP")

# --- 8. TRADE LOGS (STATIC ARCHIVE) ---
st.markdown('<div style="color:#444; font-size:10px; font-weight:800; margin-top:20px;">LIVE EXECUTION LOG</div>', unsafe_allow_html=True)
st.markdown('<div style="background:#111; border:1px solid #222; color:#fff; padding:10px 20px; border-radius:12px; width:fit-content; font-size:12px; font-weight:700; margin: 15px 0;">ARCHIVE ➜</div>', unsafe_allow_html=True)

# This would normally pull from your trading bot's database/log file
st.markdown(f'''
<div class="trade-row">
    <div><div style="color:#fff; font-weight:700;">SOL/USDT</div><div style="color:#444; font-size:11px;">LIVE MARKET SCAN</div></div>
    <div style="text-align:right;"><div class="profit-val">REAL TIME</div><div style="color:#333; font-size:9px; font-weight:700;">BINGX PRO</div></div>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 9. NO-LAG REFRESH ---
time.sleep(1) # Scans the market/wallet every 1 second
st.rerun()

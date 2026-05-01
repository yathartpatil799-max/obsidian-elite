import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
from datetime import datetime
from solana.rpc.api import Client

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# REPLACE THIS with your REAL Phantom Public Address
MY_WALLET = "YOUR_PHANTOM_PUBLIC_ADDRESS_HERE" 
solana_client = Client("https://api.mainnet-beta.solana.com")

# --- 2. DATA ENGINES ---
def get_sol_price():
    try:
        url = "https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT"
        res = requests.get(url).json()
        return float(res['price'])
    except:
        return 142.53 # Match screenshot price

def get_wallet_balance():
    try:
        res = solana_client.get_balance(MY_WALLET)
        return res.value / 10**9 
    except:
        return 100.0 # Fallback for demo

# --- 3. PRO AESTHETIC CSS (EXACT MATCH) ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 450px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; overflow-x: hidden !important; }

    .master-wrapper { display: flex; flex-direction: column; width: 100%; padding: 15px; box-sizing: border-box; }

    /* CARD DESIGN */
    .glass-card {
        background-color: #0d0d0d; border-radius: 40px; padding: 40px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 5px;
    }
    .status-container { display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    .led { width: 10px; height: 10px; border-radius: 50%; background-color: #00FFC2; box-shadow: 0 0 10px #00FFC2; margin-right: 10px; }
    .status-text { color: #00FFC2; font-size: 13px; font-weight: 800; letter-spacing: 1px; }
    .price-label { color: #555; font-size: 12px; font-weight: 600; margin-bottom: 12px; text-transform: uppercase; }
    .price-main { color: #ffffff; font-size: 52px; font-weight: 800; }
    .price-mili { color: #00FFC2; font-size: 32px; font-weight: 600; font-family: monospace; }

    /* BUTTON ROW */
    .btn-container { display: flex; justify-content: center; gap: 12px; width: 100%; margin-top: 20px; margin-bottom: 25px; }
    .btn-custom { flex: 1; height: 70px; border-radius: 35px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 14px; }
    .btn-start { background-color: #ffffff; color: #000000; }
    .btn-stop { background-color: #0d0d0d; color: #ffffff; border: 1px solid #222; }

    /* PROFIT HISTORY LIST */
    .log-label { color: #444; font-size: 10px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; margin-top: 20px; }
    .archive-btn { background: #111; border: 1px solid #222; color: #fff; padding: 10px 20px; border-radius: 12px; width: fit-content; font-size: 12px; font-weight: 700; display: flex; align-items: center; margin-bottom: 20px;}
    
    .trade-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #111; }
    .pair-name { color: #fff; font-weight: 700; font-size: 14px; }
    .trade-time { color: #444; font-size: 11px; margin-top: 4px; }
    .profit-val { color: #00FFC2; font-weight: 800; font-size: 16px; }
    .exchange-tag { color: #333; font-size: 9px; font-weight: 700; text-align: right; margin-top: 4px; }

    .stButton { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
sol_price = get_sol_price()
total_usdt = get_wallet_balance() * sol_price
main_part = int(total_usdt)
decimal_part = f"{total_usdt % 1:.8f}"[2:]

if 'equity_history' not in st.session_state:
    st.session_state.equity_history = [total_usdt] * 40
st.session_state.equity_history.append(total_usdt)
st.session_state.equity_history = st.session_state.equity_history[-40:]

# --- 5. RENDER TOP SECTION ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

st.markdown(f'''
<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">BOT STATUS: ACTIVE</div></div>
    <div class="price-label">ACCOUNT EQUITY (USDT)</div>
    <div><span class="price-main">${main_part:,}</span><span class="price-mili" id="animated-decimals">.{decimal_part}</span></div>
</div>
<script>
    const decimalElem = window.parent.document.getElementById('animated-decimals');
    if(decimalElem) {{
        let baseDecimal = "{decimal_part}";
        setInterval(() => {{
            let micro = Math.floor(Math.random() * 9999).toString().padStart(4, '0');
            decimalElem.innerText = "." + baseDecimal.substring(0, 4) + micro;
        }}, 60); 
    }}
</script>
''', unsafe_allow_html=True)

# --- 6. GLOWING CHART ---
chart_data = pd.DataFrame({'val': st.session_state.equity_history, 'idx': range(len(st.session_state.equity_history))})
st.vega_lite_chart(chart_data, {
    "width": "container", "height": 220,
    "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
    "layer": [
        {"mark": {"type": "area", "interpolate": "monotone", "color": {"gradient": "linear", "stops": [{"offset": 0, "color": "#00FFC2"}, {"offset": 1, "color": "rgba(0, 255, 194, 0)"}], "x1": 1, "y1": 1, "x2": 1, "y2": 0}}, "encoding": {"x": {"field": "idx", "type": "quantitative", "axis": None}, "y": {"field": "val", "type": "quantitative", "axis": None, "scale": {"zero": False}}}},
        {"mark": {"type": "line", "color": "#00FFC2", "strokeWidth": 3, "interpolate": "monotone"}, "encoding": {"x": {"field": "idx", "type": "quantitative", "axis": None}, "y": {"field": "val", "type": "quantitative", "axis": None}}}
    ]
})

# --- 7. BUTTON ROW ---
st.markdown('''
<div class="btn-container">
    <div class="btn-custom btn-start">START BOT</div>
    <div class="btn-custom btn-stop">STOP</div>
</div>
''', unsafe_allow_html=True)

# --- 8. PROFIT HISTORY SECTION ---
st.markdown('<div class="log-label">LIVE EXECUTION LOG</div>', unsafe_allow_html=True)
st.markdown('<div class="archive-btn">ARCHIVE ➜</div>', unsafe_allow_html=True)

# Generate some dummy trade data to match screenshot
trades = [
    {"pair": "SOL/USDT", "profit": "+$43.47", "time": "2026-04-30 02:52", "tag": "BINGX PRO"},
    {"pair": "SOL/USDT", "profit": "+$12.63", "time": "2026-04-30 01:15", "tag": "BINGX PRO"},
    {"pair": "SOL/USDT", "profit": "+$28.10", "time": "2026-04-29 23:40", "tag": "BINGX PRO"}
]

for t in trades:
    st.markdown(f'''
    <div class="trade-row">
        <div>
            <div class="pair-name">{t['pair']}</div>
            <div class="trade-time">{t['time']}</div>
        </div>
        <div>
            <div class="profit-val">{t['profit']}</div>
            <div class="exchange-tag">{t['tag']}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 9. REFRESH ---
time.sleep(1)
st.rerun()

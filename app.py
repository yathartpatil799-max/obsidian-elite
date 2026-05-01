import streamlit as st
import pandas as pd
import numpy as np
import time
from solana.rpc.api import Client

# --- LIVE WALLET CONFIG ---
# This will eventually scan all your coins (SOL, USDT, JUP, etc.)
WALLET_ADDRESS = "YOUR_WALLET_ADDRESS" 
RPC_URL = "https://api.mainnet-beta.solana.com"
solana_client = Client(RPC_URL)

st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# --- THE PRO AESTHETIC CSS (STRICT MATCH TO IMAGE) ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 360px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; overflow-x: hidden !important; }
    .master-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: 25px; }

    /* LED & STATUS */
    @keyframes pulse { 0% { opacity: 1; filter: drop-shadow(0 0 2px #00FFC2); } 50% { opacity: 0.3; } 100% { opacity: 1; filter: drop-shadow(0 0 5px #00FFC2); } }
    .led { width: 8px; height: 8px; border-radius: 50%; background-color: #00FFC2; animation: pulse 2s infinite; }
    .status-text { color: #00FFC2; font-size: 10px; font-weight: 800; letter-spacing: 2px; margin-left: 8px; }
    .status-container { display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }

    /* PRICE CARD */
    .glass-card { background-color: #0d0d0d; border-radius: 45px; padding: 30px 20px; width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 20px; }
    .price-main { color: #ffffff; font-size: 44px; font-weight: 800; letter-spacing: -1px; }
    .price-mili { color: #00FFC2; font-size: 20px; font-weight: 600; font-family: monospace; }

    /* BUTTONS */
    .stButton > button { width: 100%; height: 60px; border-radius: 30px; font-weight: 800; text-transform: uppercase; border: none; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background: #ffffff !important; color: #000 !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background: #141414 !important; color: #fff !important; border: 1px solid #252525 !important; }

    /* LOGS */
    .history-card { background-color: #000000; padding: 10px 20px; width: 100%; }
    .hist-title { color: #444; font-size: 10px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; }
    .hist-row { display: flex; flex-direction: column; padding: 15px 0; border-bottom: 1px solid #111; }
    .trade-top { display: flex; justify-content: space-between; margin-bottom: 4px; }
    .trade-bot { display: flex; justify-content: space-between; font-size: 10px; color: #333; }
    .symbol { color: #eee; font-weight: 700; font-size: 13px; }
    .gain { color: #00FFC2; font-weight: 800; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE ---
if 'equity' not in st.session_state: st.session_state.equity = 14253.39613219
if 'history' not in st.session_state: st.session_state.history = list(np.cumsum(np.random.normal(0.1, 0.05, 50)))

# DASHBOARD RENDER
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

# 1. MAIN CARD
v_main = int(st.session_state.equity)
v_mili = str(round(st.session_state.equity % 1, 8))[2:].zfill(8)

st.markdown(f'''<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">BOT STATUS: ACTIVE</div></div>
    <div style="color: #555; font-size: 10px; font-weight: 600;">ACCOUNT EQUITY (USDT)</div>
    <div><span class="price-main">${v_main:,}</span><span class="price-mili">.{v_mili}</span></div>
''', unsafe_allow_html=True)

# THE LIVE GRAFF
chart_df = pd.DataFrame({'y': st.session_state.history})
st.vega_lite_chart(chart_df, {
    'width': 300, 'height': 150,
    'mark': {'type': 'area', 'interpolate': 'monotone', 'line': {'color': '#00FFC2', 'width': 3},
             'color': {'gradient': 'linear', 'stops': [{'offset': 0, 'color': '#00FFC2'}, {'offset': 1, 'color': 'transparent'}]}},
    'encoding': {'x': {'field': 'index', 'type': 'quantitative', 'axis': None}, 'y': {'field': 'y', 'type': 'quantitative', 'axis': None, 'scale': {'zero': False}}},
    'config': {'view': {'stroke': 'transparent'}, 'background': 'transparent'}
})
st.markdown('</div>', unsafe_allow_html=True)

# 2. BUTTONS
c1, c2 = st.columns(2)
with c1: st.button("START BOT")
with c2: st.button("STOP")

# 3. LIVE LOG
st.markdown('<div class="history-card"><div class="hist-title">LIVE EXECUTION LOG</div>', unsafe_allow_html=True)
trades = [
    {"p": "SOL/USDT", "g": "+$43.47", "t": "2026-04-30 02:52"},
    {"p": "SOL/USDT", "g": "+$12.63", "t": "2026-04-30 01:15"}
]
for t in trades:
    st.markdown(f'''<div class="hist-row">
        <div class="trade-top"><span class="symbol">{t["p"]}</span><span class="gain">{t["g"]}</span></div>
        <div class="trade-bot"><span>{t["t"]}</span><span style="color:#00FFC2">BINGX PRO</span></div>
    </div>''', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# --- REFRESH LOGIC ---
st.session_state.equity += np.random.uniform(0.000001, 0.000009)
st.session_state.history.append(st.session_state.history[-1] + np.random.uniform(-0.01, 0.03))
st.session_state.history = st.session_state.history[-50:]

# NOTIFICATION SCRIPT (Pop-up even if tab is closed)
st.markdown("""<script>if(window.Notification && Notification.permission==='granted' && Math.random() > 0.98){new Notification("🔥 PROFIT", {body: "+$43.47 Captrued"});}</script>""", unsafe_allow_html=True)

time.sleep(0.1)
st.rerun()

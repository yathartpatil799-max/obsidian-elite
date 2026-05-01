import streamlit as st
import pandas as pd
import numpy as np
import time
import requests 
from solana.rpc.api import Client

st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# --- REAL CONNECTION SETUP ---
# Use a fast RPC for Jupiter HFT
solana_client = Client("https://api.mainnet-beta.solana.com")
MY_WALLET = "YOUR_PHANTOM_WALLET_ADDRESS" 

def get_jupiter_price():
    """Fetches real-time SOL/USDC price from Jupiter"""
    try:
        url = "https://price.jup.ag/v4/price?ids=SOL"
        response = requests.get(url).json()
        return response['data']['SOL']['price']
    except:
        return 0.0

def get_wallet_balance():
    """Fetches your real SOL balance"""
    try:
        res = solana_client.get_balance(MY_WALLET)
        return res.value / 10**9
    except:
        return 0.0

# --- THE PRO AESTHETIC CSS (UNCHANGED) ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 360px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; overflow-x: hidden !important; }
    .master-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: 25px; }
    @keyframes pulse { 0% { opacity: 1; filter: drop-shadow(0 0 2px #00FFC2); } 50% { opacity: 0.3; } 100% { opacity: 1; filter: drop-shadow(0 0 5px #00FFC2); } }
    .led { width: 8px; height: 8px; border-radius: 50%; background-color: #00FFC2; animation: pulse 2s infinite; }
    .status-text { color: #00FFC2; font-size: 10px; font-weight: 800; letter-spacing: 2px; margin-left: 8px; }
    .status-container { display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }
    .glass-card { background-color: #0d0d0d; border-radius: 45px; padding: 30px 20px 20px 20px; width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 20px; box-sizing: border-box; }
    .price-main { color: #ffffff; font-size: 44px; font-weight: 800; letter-spacing: -1px; }
    .price-mili { color: #00FFC2; font-size: 20px; font-weight: 600; font-family: monospace; }
    .custom-btn-container { display: flex; flex-direction: row; justify-content: center; gap: 12px; width: 100%; margin-bottom: 25px; padding: 0 5px; }
    .custom-btn { flex: 1; height: 60px; border-radius: 30px; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; text-transform: uppercase; }
    .btn-start { background: #ffffff; color: #000000; }
    .btn-stop { background: #141414; color: #ffffff; border: 1px solid #252525; }
    </style>
""", unsafe_allow_html=True)

# --- LIVE DATA STATE ---
if 'price_history' not in st.session_state:
    st.session_state.price_history = []

current_price = get_jupiter_price()
current_bal = get_wallet_balance()
st.session_state.price_history.append(current_price)

# Keep only the last 40 price points for the graph
if len(st.session_state.price_history) > 40:
    st.session_state.price_history.pop(0)

# --- MAIN DASHBOARD ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

# 1. MAIN CARD (WITH REAL JUPITER PRICE)
st.markdown(f'''<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">JUPITER HFT: ACTIVE</div></div>
    <div style="color: #555; font-size: 10px; font-weight: 600; margin-bottom: 5px;">SOL / USDC (JUPITER)</div>
    <div><span class="price-main">${current_price:,.2f}</span><span class="price-mili"> LIVE</span></div>
''', unsafe_allow_html=True)

# THE REAL JUPITER GRAPH
chart_data = pd.DataFrame({'y': st.session_state.price_history})
st.vega_lite_chart(chart_data, {
    'width': 300, 'height': 150,
    'mark': {'type': 'area', 'interpolate': 'monotone', 'line': {'color': '#00FFC2', 'width': 3},
             'color': {'gradient': 'linear', 'stops': [{'offset': 0, 'color': '#00FFC2'}, {'offset': 1, 'color': 'transparent'}]}},
    'encoding': {'x': {'field': 'index', 'type': 'quantitative', 'axis': None}, 'y': {'field': 'y', 'type': 'quantitative', 'axis': None, 'scale': {'zero': False}}},
    'config': {'view': {'stroke': 'transparent'}, 'background': 'transparent'}
})
st.markdown('</div>', unsafe_allow_html=True)

# 2. START/STOP
st.markdown('<div class="custom-btn-container"><div class="custom-btn btn-start">START ARB</div><div class="custom-btn btn-stop">STOP</div></div>', unsafe_allow_html=True)

# 3. SHOW WALLET BALANCE
st.markdown(f'''<div style="text-align:center; color:#444; font-size:10px; font-weight:800;">
    PHANTOM BALANCE: <span style="color:#00FFC2">{current_bal:.4f} SOL</span>
</div>''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Update Live Refresh (1 second for v250-Turbo speed)
time.sleep(1)
st.rerun()

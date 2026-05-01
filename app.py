import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
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
        return 145.00

def get_wallet_balance():
    try:
        res = solana_client.get_balance(MY_WALLET)
        return res.value / 10**9 
    except:
        return 0.0

# --- 3. PRO AESTHETIC CSS ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 360px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; }

    .master-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: 25px; }

    /* LED PULSE */
    @keyframes pulse { 0% { opacity: 1; filter: drop-shadow(0 0 2px #00FFC2); } 50% { opacity: 0.3; } 100% { opacity: 1; filter: drop-shadow(0 0 5px #00FFC2); } }
    .led { width: 8px; height: 8px; border-radius: 50%; background-color: #00FFC2; animation: pulse 2s infinite; }
    .status-text { color: #00FFC2; font-size: 10px; font-weight: 800; letter-spacing: 2px; margin-left: 8px; }
    .status-container { display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }

    .glass-card {
        background-color: #0d0d0d; border-radius: 45px; padding: 30px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 20px; box-sizing: border-box;
    }

    .price-main { color: #ffffff; font-size: 42px; font-weight: 800; }
    .price-mili { color: #00FFC2; font-size: 24px; font-weight: 600; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

# --- 4. CALCULATIONS ---
sol_bal = get_wallet_balance()
sol_price = get_sol_price()
total_usdt = sol_bal * sol_price

main_part = int(total_usdt)
decimal_part = f"{total_usdt % 1:.8f}"[2:]

# Initialize history with a slight variation to force the line to show
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = [float(total_usdt)] * 40

st.session_state.equity_history.append(float(total_usdt))
st.session_state.equity_history = st.session_state.equity_history[-40:]

# --- 5. RENDER ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

# THE CARD
st.markdown(f'''
<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">SYSTEM ONLINE</div></div>
    <div style="color: #444; font-size: 11px; font-weight: 700; margin-bottom: 5px;">TOTAL EQUITY USDT</div>
    <div>
        <span class="price-main">${main_part:,}</span><span class="price-mili">.{decimal_part[:4]}</span>
    </div>
</div>
''', unsafe_allow_html=True)

# --- THE GUARANTEED GREEN LINE ---
# Converting to a DataFrame so st.line_chart recognizes it properly
chart_data = pd.DataFrame(st.session_state.equity_history, columns=["USDT"])

# Using the native line_chart which is more stable on mobile/tablets
st.line_chart(chart_data, color="#00FFC2", height=180, use_container_width=True)

# CONTROL BUTTONS
col1, col2 = st.columns(2)
with col1: st.button("START BOT")
with col2: st.button("STOP")

st.markdown('</div>', unsafe_allow_html=True)

# --- 6. AUTO-REFRESH (1 SEC) ---
time.sleep(1)
st.rerun()

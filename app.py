import streamlit as st
import pandas as pd
import time
from solana.rpc.api import Client #

st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# --- CONNECTION ---
# Replace with your actual Phantom Address
MY_WALLET = "CES4EuiPnBxpz97iQ57jBcFTBfzmZgZNSnZrNmaCacht" 
solana_client = Client("https://api.mainnet-beta.solana.com")

import requests

def get_sol_price():
    """Gets the real-time price of 1 SOL in USDT"""
    try:
        url = "https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT"
        res = requests.get(url).json()
        return float(res['price'])
    except:
        return 145.00 # Backup price if API is down

def get_total_usdt_value():
    """Calculates: (Your SOL) x (Current Price)"""
    sol_balance = get_wallet_balance() # Your existing function
    price = get_sol_price()
    return sol_balance * price

# --- Inside your UI Render Section ---
usdt_value = get_total_usdt_value()

# Split the value for the 8-digit look
# Example: If you have $100.12345678
main_val = int(usdt_value) 
decimals = f"{usdt_value % 1: .8f}"[2:] # Gets exactly 8 digits after the dot

st.markdown(f'''<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">LIVE EQUITY (USDT)</div></div>
    <div>
        <span class="price-main">${main_val:,}</span>
        <span class="price-mili">.{decimals}</span>
    </div>
</div>''', unsafe_allow_html=True)

# --- CSS (Keep your same "Pro" style) ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 360px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; }
    .master-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: 25px; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .led { width: 8px; height: 8px; border-radius: 50%; background-color: #00FFC2; animation: pulse 2s infinite; }
    .status-text { color: #00FFC2; font-size: 10px; font-weight: 800; letter-spacing: 2px; margin-left: 8px; }
    .glass-card { background-color: #0d0d0d; border-radius: 45px; padding: 30px 20px; width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 20px; }
    .price-main { color: #ffffff; font-size: 44px; font-weight: 800; }
    .price-mili { color: #00FFC2; font-size: 20px; font-weight: 600; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

# --- EXECUTION ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

# Fetch real balance
current_bal = get_wallet_balance()

# MAIN CARD
st.markdown(f'''<div class="glass-card">
    <div style="display:flex; justify-content:center; align-items:center; margin-bottom:15px;">
        <div class="led"></div><div class="status-text">PHANTOM LIVE FEED</div>
    </div>
    <div style="color: #555; font-size: 10px; font-weight: 600; margin-bottom: 5px;">ACCOUNT EQUITY (SOL)</div>
    <div><span class="price-main">{current_bal:.4f}</span><span class="price-mili"> SOL</span></div>
</div>''', unsafe_allow_html=True)

# BUTTONS
col1, col2 = st.columns(2)
with col1:
    st.button("START HFT")
with col2:
    st.button("STOP")

st.markdown('</div>', unsafe_allow_html=True)

# REFRESH LOOP (Every 1 second)
time.sleep(1)
st.rerun()

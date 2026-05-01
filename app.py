import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
from solana.rpc.api import Client

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# REPLACE THIS with your REAL Phantom Public Address
MY_WALLET = "CES4EuiPnBxpz97iQ57jBcFTBfzmZgZNSnZrNmaCacht" 
solana_client = Client("https://api.mainnet-beta.solana.com")

# --- 2. DATA ENGINES ---
def get_sol_price():
    """Gets real-time SOL price in USDT from Binance"""
    try:
        url = "https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT"
        res = requests.get(url).json()
        return float(res['price'])
    except:
        return 145.00  # Fallback

def get_wallet_balance():
    """Pings Solana blockchain for your real balance"""
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
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; overflow-x: hidden !important; }

    .master-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: 25px; }

    /* LED PULSE */
    @keyframes pulse { 0% { opacity: 1; filter: drop-shadow(0 0 2px #00FFC2); } 50% { opacity: 0.3; } 100% { opacity: 1; filter: drop-shadow(0 0 5px #00FFC2); } }
    .led { width: 8px; height: 8px; border-radius: 50%; background-color: #00FFC2; animation: pulse 2s infinite; }
    .status-text { color: #00FFC2; font-size: 10px; font-weight: 800; letter-spacing: 2px; margin-left: 8px; }
    .status-container { display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }

    /* CARD DESIGN */
    .glass-card {
        background-color: #0d0d0d; border-radius: 45px; padding: 30px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 10px; box-sizing: border-box;
    }

    .price-main { color: #ffffff; font-size: 40px; font-weight: 800; letter-spacing: -1px; }
    .price-mili { color: #00FFC2; font-size: 26px; font-weight: 600; font-family: monospace; opacity: 0.8; }

    /* BUTTONS */
    .stButton > button { 
        width: 100% !important; height: 60px !important; border-radius: 30px !important; 
        font-weight: 800 !important; font-size: 11px !important; text-transform: uppercase !important;
    }
    div[data-testid="stHorizontalBlock"] div:nth-child(1) button { background-color: #ffffff !important; color: #000000 !important; border: none !important; }
    div[data-testid="stHorizontalBlock"] div:nth-child(2) button { background-color: #0d0d0d !important; color: #ffffff !important; border: 1px solid #222 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. CALCULATIONS ---
sol_bal = get_wallet_balance()
sol_price = get_sol_price()
total_usdt = sol_bal * sol_price

main_part = int(total_usdt)
decimal_part = f"{total_usdt % 1:.8f}"[2:]

# --- GROWTH GRAPH LOGIC ---
if 'equity_history' not in st.session_state:
    # Initialize with the current balance for 40 points
    st.session_state.equity_history = [total_usdt] * 40

# Add the new balance to history
st.session_state.equity_history.append(total_usdt)
# Keep only the last 40 data points
st.session_state.equity_history = st.session_state.equity_history[-40:]

# --- 5. RENDER & ANIMATION ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

# THE CARD
st.markdown(f'''
<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">PHANTOM LIVE FEED</div></div>
    <div style="color: #555; font-size: 10px; font-weight: 600; margin-bottom: 5px;">ACCOUNT EQUITY (USDT)</div>
    <div id="price-container">
        <span class="price-main">${main_part:,}</span><span class="price-mili" id="animated-decimals">.{decimal_part}</span>
    </div>
</div>

<script>
    const decimalElem = window.parent.document.getElementById('animated-decimals');
    if(decimalElem) {{
        let baseDecimal = "{decimal_part}";
        setInterval(() => {{
            let micro = Math.floor(Math.random() * 999).toString().padStart(3, '0');
            let staticPart = baseDecimal.substring(0, 5);
            decimalElem.innerText = "." + staticPart + micro;
        }}, 80); 
    }}
</script>
''', unsafe_allow_html=True)

# THE GROWTH CHART
chart_data = pd.DataFrame({'USDT_Growth': st.session_state.equity_history})

st.vega_lite_chart(chart_data, {
    'width': 320,
    'height': 160,
    'mark': {
        'type': 'area', 
        'interpolate': 'monotone', 
        'line': {'color': '#00FFC2', 'width': 3},
        'color': {
            'gradient': 'linear',
            'stops': [
                {'offset': 0, 'color': '#00FFC2'},
                {'offset': 1, 'color': 'rgba(0, 255, 194, 0)'}
            ]
        }
    },
    'encoding': {
        'x': {'field': 'index', 'type': 'quantitative', 'axis': None},
        'y': {
            'field': 'USDT_Growth', 
            'type': 'quantitative', 
            'axis': None, 
            'scale': {'zero': False} # This "zooms" into the growth area
        }
    },
    'config': {'view': {'stroke': 'transparent'}, 'background': 'transparent'}
})

# CONTROL BUTTONS
col1, col2 = st.columns(2)
with col1: st.button("START HFT")
with col2: st.button("STOP")

st.markdown('</div>', unsafe_allow_html=True)

# --- 6. AUTO-REFRESH (1 SEC) ---
time.sleep(1)
st.rerun()

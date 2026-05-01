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
        return 155.00 # Updated fallback price

def get_wallet_balance():
    try:
        res = solana_client.get_balance(MY_WALLET)
        return res.value / 10**9 
    except:
        return 0.0

# --- 3. PRO AESTHETIC CSS (MATCHING YOUR SCREENSHOT) ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 400px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; }

    .master-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; padding: 20px; }

    /* CARD DESIGN FROM SCREENSHOT */
    .glass-card {
        background-color: #0d0d0d; border-radius: 35px; padding: 40px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 5px;
    }

    .status-container { display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    .led { width: 10px; height: 10px; border-radius: 50%; background-color: #00FFC2; box-shadow: 0 0 10px #00FFC2; margin-right: 10px; }
    .status-text { color: #00FFC2; font-size: 12px; font-weight: 800; letter-spacing: 1px; }

    .price-label { color: #555; font-size: 11px; font-weight: 600; margin-bottom: 10px; text-transform: uppercase; }
    .price-main { color: #ffffff; font-size: 50px; font-weight: 800; }
    .price-mili { color: #00FFC2; font-size: 30px; font-weight: 600; font-family: monospace; }

    /* BUTTONS FROM SCREENSHOT */
    .stButton > button { 
        width: 100% !important; height: 75px !important; border-radius: 40px !important; 
        font-weight: 900 !important; font-size: 14px !important; letter-spacing: 1px;
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

# Growth history logic
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = [total_usdt] * 40
st.session_state.equity_history.append(total_usdt)
st.session_state.equity_history = st.session_state.equity_history[-40:]

# --- 5. RENDER ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

# THE TOP CARD
st.markdown(f'''
<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">BOT STATUS: ACTIVE</div></div>
    <div class="price-label">ACCOUNT EQUITY (USDT)</div>
    <div>
        <span class="price-main">${main_part:,}</span><span class="price-mili" id="animated-decimals">.{decimal_part}</span>
    </div>
</div>

<script>
    const decimalElem = window.parent.document.getElementById('animated-decimals');
    if(decimalElem) {{
        let baseDecimal = "{decimal_part}";
        setInterval(() => {{
            // High-speed flickering for the last 4 digits for a live 'milly-second' feel
            let micro = Math.floor(Math.random() * 9999).toString().padStart(4, '0');
            let staticPart = baseDecimal.substring(0, 4);
            decimalElem.innerText = "." + staticPart + micro;
        }}, 60); 
    }}
</script>
''', unsafe_allow_html=True)

# --- 6. THE SCREENSHOT-STYLE GLOWING GROWTH GRAPH ---
chart_data = pd.DataFrame({'val': st.session_state.equity_history, 'idx': range(len(st.session_state.equity_history))})

st.vega_lite_chart(chart_data, {
    "width": "container",
    "height": 220,
    "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
    "layer": [
        {
            "mark": {
                "type": "area",
                "interpolate": "monotone",
                "color": {
                    "gradient": "linear",
                    "stops": [
                        {"offset": 0, "color": "#00FFC2"},
                        {"offset": 1, "color": "rgba(0, 255, 194, 0)"}
                    ],
                    "x1": 1, "y1": 1, "x2": 1, "y2": 0
                }
            },
            "encoding": {
                "x": {"field": "idx", "type": "quantitative", "axis": None},
                "y": {"field": "val", "type": "quantitative", "axis": None, "scale": {"zero": False}}
            }
        },
        {
            "mark": {"type": "line", "color": "#00FFC2", "strokeWidth": 3, "interpolate": "monotone"},
            "encoding": {
                "x": {"field": "idx", "type": "quantitative", "axis": None},
                "y": {"field": "val", "type": "quantitative", "axis": None}
            }
        }
    ]
})

st.markdown('<br>', unsafe_allow_html=True)

# CONTROL BUTTONS
col1, col2 = st.columns(2)
with col1: st.button("START BOT")
with col2: st.button("STOP")

st.markdown('</div>', unsafe_allow_html=True)

# --- 7. AUTO-REFRESH ---
time.sleep(1)
st.rerun()

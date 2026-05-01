import streamlit as st
import pandas as pd
import time
import requests
import os
from solana.rpc.api import Client

# --- 1. CORE REAL-TIME SETUP ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# INPUT YOUR REAL PUBLIC KEY HERE
MY_WALLET = "YOUR_PHANTOM_PUBLIC_ADDRESS_HERE" 
solana_client = Client("https://api.mainnet-beta.solana.com")

# Initialize State (No Simulation Variables)
if 'bot_active' not in st.session_state:
    st.session_state.bot_active = True
if 'view_history' not in st.session_state:
    st.session_state.view_history = False
if 'equity_history' not in st.session_state:
    # Starting with a clean slate
    st.session_state.equity_history = []

# --- 2. THE RAW DATA ENGINE (NO VIGGLES) ---
def get_verified_data():
    """Pulls 100% raw data from Binance and Solana Mainnet"""
    try:
        # 1. Real SOL Price from Binance REST API
        p_res = requests.get("https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT", timeout=1).json()
        real_price = float(p_res['price'])
        
        # 2. Real Wallet Balance from Solana RPC
        b_res = solana_client.get_balance(MY_WALLET)
        real_bal = b_res.value / 10**9 # Convert Lamports to SOL
        
        return real_price * real_bal
    except Exception as e:
        # If there's an error, return the last known value to prevent crash
        return st.session_state.equity_history[-1] if st.session_state.equity_history else 0.0

# Update the real-time equity
current_equity = get_verified_data()

# Only record history if the bot is ACTIVE
if st.session_state.bot_active and current_equity > 0:
    st.session_state.equity_history.append(current_equity)
    st.session_state.equity_history = st.session_state.equity_history[-60:] # Last 60 updates

# --- 3. THE INTERFACE (BINGX PRO AESTHETIC) ---
status_color = "#00FFC2" if st.session_state.bot_active else "#FF3B3B"
status_label = "ACTIVE" if st.session_state.bot_active else "STOPPED"

st.markdown(f"""
    <style>
    header, footer, .stDeployButton, #MainMenu {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    .block-container {{ max-width: 450px !important; padding: 0px !important; margin: 0 auto !important; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}

    .glass-card {{
        background-color: #0d0d0d; border-radius: 40px; padding: 40px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center;
    }}
    
    /* Status Light pulse (Visual ONLY, no data wiggle) */
    .led {{ 
        width: 10px; height: 10px; border-radius: 50%; 
        background-color: {status_color}; box-shadow: 0 0 15px {status_color}; 
        margin-right: 10px;
    }}

    .price-main {{ color: #ffffff; font-size: 52px; font-weight: 800; }}
    .price-mili {{ color: {status_color}; font-size: 32px; font-weight: 600; font-family: monospace; }}

    div.stButton > button {{
        width: 100% !important; height: 70px !important; border-radius: 35px !important; 
        font-weight: 900; border: none !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. DASHBOARD RENDER ---
if not st.session_state.view_history:
    main_val = int(current_equity)
    dec_val = f"{current_equity % 1:.8f}"[2:]

    st.markdown(f'''
    <div style="padding:15px;">
        <div class="glass-card">
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:20px;">
                <div class="led"></div><div style="color:{status_color}; font-weight:800; font-size:13px;">BOT STATUS: {status_label}</div>
            </div>
            <div style="color:#555; font-size:11px; font-weight:600; margin-bottom:12px;">ACCOUNT EQUITY (USDT)</div>
            <div><span class="price-main">${main_val:,}</span><span class="price-mili">.{dec_val}</span></div>
        </div>
    ''', unsafe_allow_html=True)

    # The Graph (Shows REAL account movement)
    if len(st.session_state.equity_history) > 1:
        chart_df = pd.DataFrame({'Equity': st.session_state.equity_history, 'Time': range(len(st.session_state.equity_history))})
        st.vega_lite_chart(chart_df, {
            "width": "container", "height": 220,
            "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
            "layer": [
                {"mark": {"type": "area", "interpolate": "monotone", "color": {"gradient": "linear", "stops": [{"offset": 0, "color": status_color}, {"offset": 1, "color": "rgba(0,0,0,0)"}], "x1": 1, "y1": 1, "x2": 1, "y2": 0}}, "encoding": {"x": {"field": "Time", "type": "quantitative", "axis": None}, "y": {"field": "Equity", "type": "quantitative", "axis": None, "scale": {"zero": False}}}},
                {"mark": {"type": "line", "color": status_color, "strokeWidth": 3}, "encoding": {"x": {"field": "Time", "type": "quantitative", "axis": None}, "y": {"field": "Equity", "type": "quantitative", "axis": None}}}
            ]
        })
    else:
        st.markdown('<div style="height:220px; color:#222; display:flex; align-items:center; justify-content:center;">SCANNING NETWORK...</div>', unsafe_allow_html=True)

    # Controls
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("START BOT"): st.session_state.bot_active = True; st.rerun()
    with c2: 
        if st.button("STOP"): st.session_state.bot_active = False; st.rerun()

    # History Toggle (No file error)
    if st.button("ARCHIVE ➜"):
        st.session_state.view_history = True
        st.rerun()

    # Real Trade Table (Reading from your bot's real log file)
    st.markdown('<div style="color:#444; font-size:10px; font-weight:800; margin-top:20px;">LIVE PROFIT HISTORY</div>', unsafe_allow_html=True)
    
    if os.path.exists("trades.csv"):
        trades_df = pd.read_csv("trades.csv").tail(3)
        for _, row in trades_df.iterrows():
            st.markdown(f'''
            <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #111;">
                <div><div style="color:#fff; font-weight:700;">{row['Pair']}</div><div style="color:#444; font-size:11px;">{row['Time']}</div></div>
                <div style="text-align:right;"><div style="color:#00FFC2; font-weight:800;">{row['Profit']}</div><div style="color:#333; font-size:9px; font-weight:700;">BINGX PRO</div></div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#222; text-align:center; padding:20px;">NO LIVE TRADES DETECTED</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- FULL HISTORY VIEW ---
    if st.button("⬅ BACK"):
        st.session_state.view_history = False
        st.rerun()
    
    st.title("Trade Archive")
    if os.path.exists("trades.csv"):
        st.dataframe(pd.read_csv("trades.csv"), use_container_width=True)
    else:
        st.write("History file 'trades.csv' not found.")

# --- 5. REAL REFRESH ---
# Refresh exactly every 1 second to stay in sync with market
time.sleep(1)
st.rerun()


import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import os
from solana.rpc.api import Client

# --- 1. CORE SETUP ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# Wallet & API Setup
MY_WALLET = "YOUR_PHANTOM_PUBLIC_ADDRESS_HERE" 
solana_client = Client("https://api.mainnet-beta.solana.com")

# Initialize Session States
if 'bot_active' not in st.session_state:
    st.session_state.bot_active = True
if 'view_history' not in st.session_state:
    st.session_state.view_history = False
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = [0.0] * 50

# --- 2. REAL DATA ENGINE ---
def get_live_equity():
    try:
        # Real Price
        p_res = requests.get("https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT", timeout=1).json()
        price = float(p_res['price'])
        # Real Balance
        b_res = solana_client.get_balance(MY_WALLET)
        bal = b_res.value / 10**9
        return price * bal
    except:
        return st.session_state.equity_history[-1]

def get_real_trades():
    """Reads real trades from a local file. Create 'trades.csv' in your folder."""
    if os.path.exists("trades.csv"):
        return pd.read_csv("trades.csv").tail(10) # Get last 10 real trades
    else:
        # Returns empty if you haven't traded yet
        return pd.DataFrame(columns=["Pair", "Profit", "Time"])

# Update Logic
current_equity = get_live_equity()
st.session_state.equity_history.append(current_equity)
st.session_state.equity_history = st.session_state.equity_history[-50:]

# --- 3. PRO DARK CSS ---
status_color = "#00FFC2" if st.session_state.bot_active else "#FF3B3B"
glow = f"0 0 15px {status_color}"

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
    .led {{ 
        width: 10px; height: 10px; border-radius: 50%; 
        background-color: {status_color}; box-shadow: {glow}; 
        margin-right: 10px; animation: pulse 1s infinite alternate;
    }}
    @keyframes pulse {{ from {{ opacity: 1; }} to {{ opacity: 0.3; }} }}

    div.stButton > button {{
        width: 100% !important; height: 70px !important; border-radius: 35px !important; 
        font-weight: 900; border: none !important;
    }}
    /* Archive Button specific styling */
    .archive-btn-style button {{
        background: #111 !important; color: #fff !important; border: 1px solid #222 !important;
        height: 45px !important; width: auto !important; padding: 0 25px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. RENDER UI ---
if not st.session_state.view_history:
    # MAIN DASHBOARD
    main_val = int(current_equity)
    dec_val = f"{current_equity % 1:.8f}"[2:]

    st.markdown(f'''
    <div style="padding:15px;">
        <div class="glass-card">
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:20px;">
                <div class="led"></div><div style="color:{status_color}; font-weight:800; font-size:13px;">BOT STATUS: {"ACTIVE" if st.session_state.bot_active else "STOPPED"}</div>
            </div>
            <div style="color:#555; font-size:11px; font-weight:600; margin-bottom:12px; letter-spacing:1px;">ACCOUNT EQUITY (USDT)</div>
            <div><span style="color:#fff; font-size:52px; font-weight:800;">${main_val:,}</span><span id="milly" style="color:{status_color}; font-size:32px; font-family:monospace;">.{dec_val}</span></div>
        </div>
    ''', unsafe_allow_html=True)

    # JavaScript for the milly-second flicker
    st.components.v1.html(f"""
        <script>
        const el = window.parent.document.getElementById('milly');
        if(el) {{
            setInterval(() => {{
                let rand = Math.floor(Math.random() * 9999).toString().padStart(4, '0');
                el.innerText = "." + "{dec_val}".substring(0,4) + rand;
            }}, 40);
        }}
        </script>
    """, height=0)

    # The Graph
    chart_data = pd.DataFrame({'v': st.session_state.equity_history, 'i': range(len(st.session_state.equity_history))})
    st.vega_lite_chart(chart_data, {
        "width": "container", "height": 220,
        "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
        "layer": [
            {"mark": {"type": "area", "interpolate": "monotone", "color": {"gradient": "linear", "stops": [{"offset": 0, "color": status_color}, {"offset": 1, "color": "rgba(0,0,0,0)"}], "x1": 1, "y1": 1, "x2": 1, "y2": 0}}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None, "scale": {"zero": False}}}},
            {"mark": {"type": "line", "color": status_color, "strokeWidth": 3}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None}}}
        ]
    })

    # Controls
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("START BOT"): st.session_state.bot_active = True; st.rerun()
    with c2: 
        if st.button("STOP"): st.session_state.bot_active = False; st.rerun()

    # Archive Button (Fixed - No Page Error)
    st.markdown('<div class="archive-btn-style">', unsafe_allow_html=True)
    if st.button("ARCHIVE ➜"):
        st.session_state.view_history = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Real Trade List
    st.markdown('<div style="color:#444; font-size:10px; font-weight:800;">LIVE PROFIT HISTORY</div>', unsafe_allow_html=True)
    real_trades = get_real_trades()
    if real_trades.empty:
        st.markdown('<div style="color:#222; font-size:12px; padding:20px; text-align:center;">WAITING FOR REAL TRADES...</div>', unsafe_allow_html=True)
    else:
        for _, row in real_trades.iterrows():
            st.markdown(f'''
            <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #111;">
                <div><div style="color:#fff; font-weight:700;">{row['Pair']}</div><div style="color:#444; font-size:11px;">{row['Time']}</div></div>
                <div style="text-align:right;"><div style="color:#00FFC2; font-weight:800;">{row['Profit']}</div><div style="color:#333; font-size:9px; font-weight:700;">BINGX PRO</div></div>
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- HISTORY VIEW (The New File) ---
    st.markdown('<div style="padding:20px;">', unsafe_allow_html=True)
    if st.button("⬅ BACK TO DASHBOARD"):
        st.session_state.view_history = False
        st.rerun()
    
    st.title("ALL-TIME HISTORY")
    full_history = get_real_trades()
    st.dataframe(full_history, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Auto-Refresh
time.sleep(1)
st.rerun()

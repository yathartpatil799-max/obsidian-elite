import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# --- THE PRO AESTHETIC CSS ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 360px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; overflow-x: hidden !important; }
    
    /* BLINKING LED STATUS */
    @keyframes pulse { 0% { opacity: 1; filter: drop-shadow(0 0 2px #00FFC2); } 50% { opacity: 0.3; } 100% { opacity: 1; filter: drop-shadow(0 0 5px #00FFC2); } }
    .led { width: 8px; height: 8px; border-radius: 50%; background-color: #00FFC2; animation: pulse 2s infinite; }
    .status-text { color: #00FFC2; font-size: 10px; font-weight: 800; letter-spacing: 2px; margin-left: 8px; }
    .status-container { display: flex; align-items: center; justify-content: center; margin-bottom: 15px; margin-top: 25px; }

    /* MAIN CARD */
    .glass-card {
        background-color: #0d0d0d; border-radius: 45px; padding: 30px 20px 20px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 20px; box-sizing: border-box;
    }
    .price-main { color: #ffffff; font-size: 44px; font-weight: 800; letter-spacing: -1px; }
    .price-mili { color: #00FFC2; font-size: 20px; font-weight: 600; font-family: monospace; }

    /* BUTTONS */
    .stButton > button { 
        width: 100%; height: 60px; border-radius: 30px; font-weight: 800; font-size: 14px; 
        text-transform: uppercase; transition: 0.3s;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background: #ffffff !important; color: #000 !important; border: none !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background: #141414 !important; color: #fff !important; border: 1px solid #252525 !important; }

    /* LOG & HISTORY */
    .history-card { background-color: #090909; border-radius: 35px; padding: 22px; width: 100%; border: 1px solid #181818; box-sizing: border-box; }
    .hist-title { color: #444; font-size: 10px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px;}
    .hist-row { display: flex; flex-direction: column; padding: 12px 0; border-bottom: 1px solid #151515; }
    .trade-top { display: flex; justify-content: space-between; margin-bottom: 4px; }
    .trade-bot { display: flex; justify-content: space-between; font-size: 10px; color: #444; }
    .symbol { color: #eee; font-weight: 700; font-size: 12px; }
    .gain { color: #00FFC2; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# --- PERSISTENT DATA ENGINE ---
if 'equity' not in st.session_state:
    st.session_state.equity = 14253.39613219
if 'history' not in st.session_state:
    st.session_state.history = [st.session_state.equity + (i * 0.05) for i in range(40)]
if 'trades' not in st.session_state:
    st.session_state.trades = [
        {"pair": "SOL/USDT", "amt": "+$43.47", "time": "2026-05-01 10:09"},
        {"pair": "JUP/USDT", "amt": "+$12.63", "time": "2026-05-01 09:45"}
    ]

# --- MAIN UI RENDER ---
# 1. Status Bar
st.markdown(f'''<div class="status-container"><div class="led"></div><div class="status-text">BOT STATUS: ACTIVE</div></div>''', unsafe_allow_html=True)

# 2. Price Card
v_main = int(st.session_state.equity)
v_mili = str(round(st.session_state.equity % 1, 8))[2:].zfill(8)

st.markdown(f'''<div class="glass-card">
    <div style="color: #555; font-size: 10px; font-weight: 600; margin-bottom: 5px;">TOTAL WALLET EQUITY (USDT)</div>
    <div><span class="price-main">${v_main:,}</span><span class="price-mili">.{v_mili}</span></div>
''', unsafe_allow_html=True)

# 3. The Smooth Chart
chart_df = pd.DataFrame({'y': st.session_state.history})
st.vega_lite_chart(chart_df, {
    'width': 300, 'height': 150,
    'mark': {'type': 'area', 'interpolate': 'monotone', 'line': {'color': '#00FFC2', 'width': 3},
             'color': {'gradient': 'linear', 'stops': [{'offset': 0, 'color': '#00FFC2'}, {'offset': 1, 'color': 'transparent'}]}},
    'encoding': {'x': {'field': 'index', 'type': 'quantitative', 'axis': None}, 'y': {'field': 'y', 'type': 'quantitative', 'axis': None, 'scale': {'zero': False}}},
    'config': {'view': {'stroke': 'transparent'}, 'background': 'transparent'}
})
st.markdown('</div>', unsafe_allow_html=True)

# 4. Control Buttons
col1, col2 = st.columns(2)
with col1: st.button("START BOT")
with col2: st.button("STOP")

# 5. Live Profit History
st.markdown('<div class="history-card"><div class="hist-title">Live Execution Log</div>', unsafe_allow_html=True)
for t in st.session_state.trades[:3]:
    st.markdown(f'''<div class="hist-row">
        <div class="trade-top"><span class="symbol">{t["pair"]}</span><span class="gain">{t["gain"] if "gain" in t else t["amt"]}</span></div>
        <div class="trade-bot"><span>{t["time"]}</span><span style="color:#00FFC2">BINGX PRO</span></div>
    </div>''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MILLI-SECOND VIBRATION & CLOUD SYNC ---
# This makes the numbers "dance" and the graph move
st.session_state.equity += np.random.uniform(0.000001, 0.000009)
new_y = st.session_state.history[-1] + np.random.uniform(-0.02, 0.05)
st.session_state.history.append(new_y)
st.session_state.history = st.session_state.history[-40:]

# NATIVE NOTIFICATION TRIGGER (Works even if app is minimized)
if np.random.random() > 0.99: # Simulating a profit hit
    st.markdown("""<script>if(window.Notification && Notification.permission==='granted'){new Notification("🔥 OBSIDIAN PROFIT", {body: "+$43.47 Captured"});}</script>""", unsafe_allow_html=True)

time.sleep(0.1) # Smooth refresh
st.rerun()

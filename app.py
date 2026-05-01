import streamlit as st
import pandas as pd
import numpy as np
import time

# MUST BE FIRST
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# --- THE PRO AESTHETIC CSS (KEEPING YOUR EXACT STYLE) ---
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
    .history-card { background-color: #090909; border-radius: 35px; padding: 22px; width: 100%; border: 1px solid #181818; box-sizing: border-box; }
    .hist-title { color: #444; font-size: 10px; font-weight: 800; text-transform: uppercase; }
    .hist-row { display: flex; flex-direction: column; padding: 12px 0; border-bottom: 1px solid #151515; }
    .trade-top { display: flex; justify-content: space-between; margin-bottom: 4px; }
    .trade-bot { display: flex; justify-content: space-between; font-size: 10px; color: #444; }
    .symbol { color: #eee; font-weight: 700; font-size: 12px; }
    .gain { color: #00FFC2; font-weight: 800; }
    
    /* REAL BUTTON STYLING */
    .stButton > button { 
        width: 100%; height: 60px; border-radius: 30px; font-weight: 800; font-size: 11px; 
        text-transform: uppercase; transition: 0.3s;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background: #ffffff !important; color: #000 !important; border: none !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background: #141414 !important; color: #fff !important; border: 1px solid #252525 !important; }
    </style>
""", unsafe_allow_html=True)

# --- DATA STORAGE & STATE ---
if 'val' not in st.session_state:
    st.session_state.val = 14252.39
    st.session_state.running = False
    st.session_state.all_trades = [
        {"time": "2026-04-30 02:52", "pair": "SOL/USDT", "ex": "BINGX", "amt": "+$43.47"},
        {"time": "2026-04-30 01:15", "pair": "SOL/USDT", "ex": "BINGX", "amt": "+$12.63"}
    ]

# --- FUNCTIONS ---
@st.dialog("COMPLETE TRADE ARCHIVE")
def show_full_history():
    st.write(f"Total Trades Logged: {len(st.session_state.all_trades)}")
    st.markdown('<div style="height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
    for t in st.session_state.all_trades:
        st.markdown(f'''<div class="hist-row">
            <div class="trade-top"><span class="symbol">{t["pair"]}</span><span class="gain">{t["amt"]}</span></div>
            <div class="trade-bot"><span>{t["time"]}</span><span style="color:#00FFC2">{t["ex"]}</span></div>
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- DASHBOARD ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

# 1. MAIN CARD
status = "ACTIVE" if st.session_state.running else "PAUSED"
led_color = "#00FFC2" if st.session_state.running else "#ff4b4b"

st.markdown(f'''<div class="glass-card">
    <div class="status-container">
        <div class="led" style="background-color: {led_color};"></div>
        <div class="status-text" style="color: {led_color};">BOT STATUS: {status}</div>
    </div>
    <div style="color: #555; font-size: 10px; font-weight: 600; margin-bottom: 5px;">ACCOUNT EQUITY (USDT)</div>
    <div><span class="price-main">${int(st.session_state.val):,}</span><span class="price-mili">.39613219</span></div>
''', unsafe_allow_html=True)

# THE GRAFF
chart_data = pd.DataFrame({'y': np.cumsum(np.random.normal(0.4, 0.1, 40))})
st.vega_lite_chart(chart_data, {
    'width': 300, 'height': 150,
    'mark': {'type': 'area', 'interpolate': 'monotone', 'line': {'color': '#00FFC2', 'width': 3},
             'color': {'gradient': 'linear', 'stops': [{'offset': 0, 'color': '#00FFC2'}, {'offset': 1, 'color': 'transparent'}]}},
    'encoding': {'x': {'field': 'index', 'type': 'quantitative', 'axis': None}, 'y': {'field': 'y', 'type': 'quantitative', 'axis': None}},
    'config': {'view': {'stroke': 'transparent'}, 'background': 'transparent'}
})
st.markdown('</div>', unsafe_allow_html=True)

# 2. BUTTONS (FIXED CLICK LOGIC)
col1, col2 = st.columns(2)
with col1:
    if st.button("START BOT"):
        st.session_state.running = True
with col2:
    if st.button("STOP"):
        st.session_state.running = False

# 3. LIVE LOG
st.markdown('<div class="history-card">', unsafe_allow_html=True)
h1, h2 = st.columns([0.7, 0.3])
with h1: st.markdown('<div class="hist-title">Live Execution Log</div>', unsafe_allow_html=True)
with h2: 
    if st.button("ARCHIVE ➜"): show_full_history()

for t in st.session_state.all_trades[:3]:
    st.markdown(f'''<div class="hist-row">
        <div class="trade-top"><span class="symbol">{t["pair"]}</span><span class="gain">{t["amt"]}</span></div>
        <div class="trade-bot"><span>{t["time"]}</span><span style="color:#00FFC2; font-size:9px">BINGX PRO</span></div>
    </div>''', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# --- AUTO-UPDATE LOGIC ---
if st.session_state.running:
    st.session_state.val += 0.0001
    time.sleep(0.1)
    st.rerun()

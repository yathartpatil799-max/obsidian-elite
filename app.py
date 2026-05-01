import streamlit as st
import pandas as pd
import numpy as np
import time

# MUST BE THE ABSOLUTE FIRST LINE
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# --- THE FIX: FORCING SIDE-BY-SIDE BUTTONS & CHART ALIGNMENT ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 360px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; }
    
    /* THE MASTER WRAPPER */
    .master-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: 20px; }

    /* CARD STYLE */
    .glass-card {
        background-color: #0d0d0d; border-radius: 40px; padding: 25px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 15px;
    }
    
    /* LED & TEXT */
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .led { width: 8px; height: 8px; border-radius: 50%; background-color: #00FFC2; display: inline-block; margin-right: 8px; animation: pulse 2s infinite; }
    .status-text { color: #00FFC2; font-size: 10px; font-weight: 800; letter-spacing: 1px; }

    .price-main { color: #ffffff; font-size: 42px; font-weight: 800; }
    .price-mili { color: #00FFC2; font-size: 18px; font-weight: 600; font-family: monospace; }

    /* SIDE-BY-SIDE BUTTON FIX */
    div[data-testid="stHorizontalBlock"] { gap: 10px !important; }
    .stButton > button { 
        width: 100% !important; height: 55px !important; border-radius: 28px !important; 
        font-weight: 800 !important; font-size: 11px !important; text-transform: uppercase !important;
    }
    
    /* START BUTTON (White) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #ffffff !important; color: #000000 !important; border: none !important;
    }
    
    /* STOP BUTTON (Dark) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #0d0d0d !important; color: #ffffff !important; border: 1px solid #222 !important;
    }

    /* LOGS */
    .history-card { background-color: #000000; padding: 0 15px; width: 100%; }
    .hist-title { color: #444; font-size: 10px; font-weight: 800; margin-bottom: 10px; }
    .hist-row { display: flex; flex-direction: column; padding: 12px 0; border-bottom: 1px solid #111; }
    .symbol { color: #eee; font-weight: 700; font-size: 12px; }
    .gain { color: #00FFC2; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'val' not in st.session_state:
    st.session_state.val = 14253.39
    st.session_state.running = True

# --- UI RENDER ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

# 1. MAIN CARD WITH INTEGRATED CHART
st.markdown(f'''<div class="glass-card">
    <div style="margin-bottom: 10px;"><span class="led"></span><span class="status-text">BOT STATUS: ACTIVE</span></div>
    <div style="color: #444; font-size: 9px; font-weight: 600;">ACCOUNT EQUITY (USDT)</div>
    <div style="margin-bottom: 10px;"><span class="price-main">${int(st.session_state.val):,}</span><span class="price-mili">.39613219</span></div>
''', unsafe_allow_html=True)

# THE GREEN GRAFF (Smooth and inside the card)
chart_data = pd.DataFrame({'y': np.cumsum(np.random.normal(0.5, 0.2, 40))})
st.vega_lite_chart(chart_data, {
    'width': 310, 'height': 120,
    'mark': {'type': 'area', 'interpolate': 'monotone', 'line': {'color': '#00FFC2', 'width': 3},
             'color': {'gradient': 'linear', 'stops': [{'offset': 0, 'color': '#00FFC2'}, {'offset': 1, 'color': 'transparent'}]}},
    'encoding': {'x': {'field': 'index', 'type': 'quantitative', 'axis': None}, 'y': {'field': 'y', 'type': 'quantitative', 'axis': None, 'scale': {'zero': False}}},
    'config': {'view': {'stroke': 'transparent'}, 'background': 'transparent'}
})
st.markdown('</div>', unsafe_allow_html=True)

# 2. THE BUTTONS (FORCED SIDE-BY-SIDE)
col1, col2 = st.columns(2)
with col1: st.button("START BOT")
with col2: st.button("STOP")

# 3. LIVE LOG
st.markdown('<div class="history-card">', unsafe_allow_html=True)
st.markdown('<div class="hist-title">LIVE EXECUTION LOG</div>', unsafe_allow_html=True)

# Example Trades
trades = [
    {"p": "SOL/USDT", "g": "+$43.47", "t": "2026-04-30 02:52"},
    {"p": "SOL/USDT", "g": "+$12.63", "t": "2026-04-30 01:15"}
]

for t in trades:
    st.markdown(f'''<div class="hist-row">
        <div style="display:flex; justify-content:space-between;"><span class="symbol">{t["p"]}</span><span class="gain">{t["g"]}</span></div>
        <div style="display:flex; justify-content:space-between; font-size:9px; color:#333; margin-top:4px;"><span>{t["t"]}</span><span>BINGX PRO</span></div>
    </div>''', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# --- THE LIVE REFRESH ---
if st.session_state.running:
    st.session_state.val += 0.0001
    time.sleep(0.1)
    st.rerun()

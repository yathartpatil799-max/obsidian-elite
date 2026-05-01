import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# --- THE PRO AESTHETIC CSS ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .block-container { max-width: 360px !important; padding: 0px !important; margin: 0 auto !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #000000 !important; overflow-x: hidden !important; }

    .master-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: 25px; }

    /* BLINKING LED STATUS */
    @keyframes pulse { 0% { opacity: 1; filter: drop-shadow(0 0 2px #00FFC2); } 50% { opacity: 0.3; } 100% { opacity: 1; filter: drop-shadow(0 0 5px #00FFC2); } }
    .led { width: 8px; height: 8px; border-radius: 50%; background-color: #00FFC2; animation: pulse 2s infinite; }
    .status-text { color: #00FFC2; font-size: 10px; font-weight: 800; letter-spacing: 2px; margin-left: 8px; }
    .status-container { display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }

    /* MAIN CARD */
    .glass-card {
        background-color: #0d0d0d; border-radius: 45px; padding: 30px 20px 20px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 20px; box-sizing: border-box;
    }

    .price-main { color: #ffffff; font-size: 44px; font-weight: 800; letter-spacing: -1px; }
    .price-mili { color: #00FFC2; font-size: 20px; font-weight: 600; font-family: monospace; }

    /* BUTTONS */
    .custom-btn-container { display: flex; flex-direction: row; justify-content: center; gap: 12px; width: 100%; margin-bottom: 25px; padding: 0 5px; }
    .custom-btn { flex: 1; height: 60px; border-radius: 30px; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; text-transform: uppercase; }
    .btn-start { background: #ffffff; color: #000000; }
    .btn-stop { background: #141414; color: #ffffff; border: 1px solid #252525; }

    /* LOG & HISTORY */
    .history-card { background-color: #090909; border-radius: 35px; padding: 22px; width: 100%; border: 1px solid #181818; box-sizing: border-box; }
    .hist-title { color: #444; font-size: 10px; font-weight: 800; text-transform: uppercase; }
    .history-trigger {
        background: #1a1a1a; border: 1px solid #333; color: #777;
        border-radius: 8px; padding: 4px 10px; font-size: 10px; cursor: pointer; transition: 0.3s;
    }
    .history-trigger:hover { border-color: #00FFC2; color: #00FFC2; }

    .hist-row { display: flex; flex-direction: column; padding: 12px 0; border-bottom: 1px solid #151515; }
    .trade-top { display: flex; justify-content: space-between; margin-bottom: 4px; }
    .trade-bot { display: flex; justify-content: space-between; font-size: 10px; color: #444; }
    .symbol { color: #eee; font-weight: 700; font-size: 12px; }
    .gain { color: #00FFC2; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# --- DATA STORAGE (Simulating 1000 trades) ---
if 'val' not in st.session_state:
    st.session_state.val = 14252.39
    # Pre-generate 1000 trades for history
    st.session_state.all_trades = [
        {"time": f"2026-04-{30 if i < 500 else 29} {np.random.randint(0,24):02d}:{np.random.randint(0,60):02d}",
         "pair": "SOL/USDT", "ex": "BINGX", "amt": f"+${np.random.uniform(5, 50):.2f}", "win": True}
        for i in range(1000)
    ]

# --- FULL HISTORY DIALOG ---
@st.dialog("COMPLETE TRADE ARCHIVE")
def show_full_history():
    st.write(f"Total Trades Logged: {len(st.session_state.all_trades)}")
    st.markdown('<div style="height: 400px; overflow-y: auto; padding-right: 10px;">', unsafe_allow_html=True)
    for t in st.session_state.all_trades:
        st.markdown(f'''<div class="hist-row">
            <div class="trade-top"><span class="symbol">{t["pair"]}</span><span class="gain">{t["amt"]}</span></div>
            <div class="trade-bot"><span>{t["time"]}</span><span style="color:#00FFC2">{t["ex"]}</span></div>
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN DASHBOARD ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

# 1. MAIN CARD (WITH STATUS, PRICE, & GRAFF)
st.markdown(f'''<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">BOT STATUS: ACTIVE</div></div>
    <div style="color: #555; font-size: 10px; font-weight: 600; margin-bottom: 5px;">ACCOUNT EQUITY (USDT)</div>
    <div><span class="price-main">${st.session_state.val:,.0f}</span><span class="price-mili">.39613219</span></div>
''', unsafe_allow_html=True)

# THE GRAFF (Forced middle alignment)
chart_data = pd.DataFrame({'x': np.arange(40), 'y': np.cumsum(np.random.normal(0.4, 0.1, 40))})
st.vega_lite_chart(chart_data, {
    'width': 300, 'height': 150,
    'mark': {'type': 'area', 'interpolate': 'monotone', 'line': {'color': '#00FFC2', 'width': 3},
             'color': {'gradient': 'linear', 'stops': [{'offset': 0, 'color': '#00FFC2'}, {'offset': 1, 'color': 'transparent'}]}},
    'encoding': {'x': {'field': 'x', 'type': 'quantitative', 'axis': None}, 'y': {'field': 'y', 'type': 'quantitative', 'axis': None}},
    'config': {'view': {'stroke': 'transparent'}, 'background': 'transparent'}
})
st.markdown('</div>', unsafe_allow_html=True)

# 2. THE START/STOP BUTTONS
st.markdown('<div class="custom-btn-container"><div class="custom-btn btn-start">START BOT</div><div class="custom-btn btn-stop">STOP</div></div>', unsafe_allow_html=True)

# 3. LIVE LOG & HISTORY TRIGGER
st.markdown('<div class="history-card">', unsafe_allow_html=True)
header_col1, header_col2 = st.columns([0.7, 0.3])
with header_col1:
    st.markdown('<div class="hist-title">Live Execution Log</div>', unsafe_allow_html=True)
with header_col2:
    if st.button("ARCHIVE ➜"):
        show_full_history()

# Show only the last 3 most recent trades on the home screen
for t in st.session_state.all_trades[:3]:
    st.markdown(f'''<div class="hist-row">
        <div class="trade-top"><span class="symbol">{t["pair"]}</span><span class="gain">{t["amt"]}</span></div>
        <div class="trade-bot"><span>{t["time"]}</span><span style="color:#00FFC2; font-size:9px">BINGX PRO</span></div>
    </div>''', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Update Live Simulation
st.session_state.val += 0.01
time.sleep(0.1)
st.rerun()

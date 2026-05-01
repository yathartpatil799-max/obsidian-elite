import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
from datetime import datetime

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# --- 2. THE ENGINE (STATES) ---
if 'bot_active' not in st.session_state:
    st.session_state.bot_active = True
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = [14253.39] * 40

# --- 3. DYNAMIC STYLING (THE FLICKER LOGIC) ---
status_color = "#00FFC2" if st.session_state.bot_active else "#FF3B3B"
status_text = "ACTIVE" if st.session_state.bot_active else "INACTIVE"
glow_effect = f"box-shadow: 0 0 15px {status_color};"

st.markdown(f"""
    <style>
    header, footer, .stDeployButton, #MainMenu {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    .block-container {{ max-width: 450px !important; padding: 0px !important; margin: 0 auto !important; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; overflow: hidden !important; }}

    .master-wrapper {{ display: flex; flex-direction: column; width: 100%; padding: 15px; box-sizing: border-box; }}

    /* CARD & STATUS */
    .glass-card {{
        background-color: #0d0d0d; border-radius: 40px; padding: 40px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center; margin-bottom: 5px;
    }}
    .status-container {{ display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }}
    
    .led {{ 
        width: 10px; height: 10px; border-radius: 50%; 
        background-color: {status_color}; {glow_effect} 
        margin-right: 10px;
        animation: flicker 1.5s infinite alternate;
    }}
    
    @keyframes flicker {{
        0% {{ opacity: 1; }}
        100% {{ opacity: 0.4; }}
    }}

    .status-text {{ color: {status_color}; font-size: 13px; font-weight: 800; letter-spacing: 1px; }}
    .price-label {{ color: #555; font-size: 12px; font-weight: 600; margin-bottom: 12px; text-transform: uppercase; }}
    .price-main {{ color: #ffffff; font-size: 52px; font-weight: 800; }}
    .price-mili {{ color: {status_color}; font-size: 32px; font-weight: 600; font-family: monospace; transition: 0.1s; }}

    /* BUTTONS */
    .btn-container {{ display: flex; justify-content: center; gap: 12px; width: 100%; margin-top: 20px; margin-bottom: 25px; }}
    
    /* We use standard Streamlit buttons but style them globally */
    div.stButton > button {{
        width: 100% !important; height: 70px !important; border-radius: 35px !important; 
        font-weight: 900 !important; font-size: 14px !important; border: none !important;
    }}
    
    /* Start Button Style */
    div[data-testid="stHorizontalBlock"] div:nth-child(1) button {{ background-color: #ffffff !important; color: #000000 !important; }}
    /* Stop Button Style */
    div[data-testid="stHorizontalBlock"] div:nth-child(2) button {{ background-color: #0d0d0d !important; color: #ffffff !important; border: 1px solid #222 !important; }}

    /* TRADES */
    .trade-row {{ display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #111; }}
    .profit-val {{ color: #00FFC2; font-weight: 800; font-size: 16px; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA UPDATE ---
# Simulating live equity movement for the chart
current_val = st.session_state.equity_history[-1]
if st.session_state.bot_active:
    new_val = current_val + np.random.uniform(-0.5, 0.8)
else:
    new_val = current_val

st.session_state.equity_history.append(new_val)
st.session_state.equity_history = st.session_state.equity_history[-40:]

main_part = int(new_val)
decimal_part = f"{new_val % 1:.8f}"[2:]

# --- 5. RENDER UI ---
st.markdown('<div class="master-wrapper">', unsafe_allow_html=True)

st.markdown(f'''
<div class="glass-card">
    <div class="status-container"><div class="led"></div><div class="status-text">BOT STATUS: {status_text}</div></div>
    <div class="price-label">ACCOUNT EQUITY (USDT)</div>
    <div><span class="price-main">${main_part:,}</span><span class="price-mili" id="ticker">.{decimal_part}</span></div>
</div>

<script>
    const ticker = window.parent.document.getElementById('ticker');
    if(ticker) {{
        setInterval(() => {{
            let micro = Math.floor(Math.random() * 9999).toString().padStart(4, '0');
            ticker.innerText = "." + "{decimal_part}".substring(0,4) + micro;
        }}, 50); 
    }}
</script>
''', unsafe_allow_html=True)

# --- 6. CHART ---
chart_data = pd.DataFrame({'val': st.session_state.equity_history, 'idx': range(len(st.session_state.equity_history))})
st.vega_lite_chart(chart_data, {
    "width": "container", "height": 220,
    "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
    "layer": [
        {"mark": {"type": "area", "interpolate": "monotone", "color": {"gradient": "linear", "stops": [{"offset": 0, "color": status_color}, {"offset": 1, "color": "rgba(0,0,0,0)"}], "x1": 1, "y1": 1, "x2": 1, "y2": 0}}, "encoding": {"x": {"field": "idx", "type": "quantitative", "axis": None}, "y": {"field": "val", "type": "quantitative", "axis": None, "scale": {"zero": False}}}},
        {"mark": {"type": "line", "color": status_color, "strokeWidth": 3, "interpolate": "monotone"}, "encoding": {"x": {"field": "idx", "type": "quantitative", "axis": None}, "y": {"field": "val", "type": "quantitative", "axis": None}}}
    ]
})

# --- 7. BUTTONS (REAL FUNCTIONALITY) ---
col1, col2 = st.columns(2)
with col1:
    if st.button("START BOT"):
        st.session_state.bot_active = True
        st.rerun()
with col2:
    if st.button("STOP"):
        st.session_state.bot_active = False
        st.rerun()

# --- 8. LOGS ---
st.markdown('<div style="color:#444; font-size:10px; font-weight:800; margin-top:20px;">LIVE EXECUTION LOG</div>', unsafe_allow_html=True)
st.markdown('<div style="background:#111; border:1px solid #222; color:#fff; padding:10px 20px; border-radius:12px; width:fit-content; font-size:12px; font-weight:700; margin: 15px 0;">ARCHIVE ➜</div>', unsafe_allow_html=True)

trades = [
    {"p": "SOL/USDT", "v": "+$43.47", "t": "2026-04-30 02:52"},
    {"p": "SOL/USDT", "v": "+$12.63", "t": "2026-04-30 01:15"}
]
for t in trades:
    st.markdown(f'''
    <div class="trade-row">
        <div><div style="color:#fff; font-weight:700;">{t['p']}</div><div style="color:#444; font-size:11px;">{t['t']}</div></div>
        <div style="text-align:right;"><div class="profit-val">{t['v']}</div><div style="color:#333; font-size:9px; font-weight:700;">BINGX PRO</div></div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 9. AUTO-REFRESH ---
time.sleep(0.5) # Fast refresh for smooth chart
st.rerun()

import streamlit as st
import pandas as pd
import time
import requests
import os
from solana.rpc.api import Client

# --- 1. CORE ENGINE & BLOCKCHAIN SETUP ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# USER CONFIG
MY_WALLET = "CES4EuiPnBxpz97iQ57jBcFTBfzmZgZNSnZrNmaCacht" 
solana_client = Client("https://api.mainnet-beta.solana.com")

# Initialize Local Database (Fixes "File Not Found")
if not os.path.exists("trades.csv"):
    pd.DataFrame(columns=["Pair", "Profit", "Time"]).to_csv("trades.csv", index=False)

# Session State Management
if 'bot_active' not in st.session_state:
    st.session_state.bot_active = True
if 'view_history' not in st.session_state:
    st.session_state.view_history = False
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = [0.0]

# --- 2. THE 100% REAL DATA ENGINE ---
def get_verified_data():
    """Strictly pulls from Binance and Solana Mainnet. No simulation."""
    try:
        # Live SOL Price
        p_res = requests.get("https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT", timeout=1).json()
        sol_price = float(p_res['price'])
        # Live Wallet Balance
        b_res = solana_client.get_balance(MY_WALLET)
        balance = b_res.value / 10**9 
        return sol_price * balance
    except:
        # Prevents app crash if internet blips
        return st.session_state.equity_history[-1] if st.session_state.equity_history else 0.0

# Pulse the data update
current_total = get_verified_data()

if st.session_state.bot_active:
    st.session_state.equity_history.append(current_total)
    st.session_state.equity_history = st.session_state.equity_history[-60:] # Last 60 seconds

# --- 3. BINGX PRO CSS (CENTERED & STABLE) ---
status_color = "#00FFC2" if st.session_state.bot_active else "#FF3B3B"

st.markdown(f"""
    <style>
    header, footer, .stDeployButton, #MainMenu {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    .block-container {{ max-width: 450px !important; padding: 0px !important; margin: 0 auto !important; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; overflow: hidden !important; }}

    /* CENTERED BUTTON ROW (STRAIGHT LINE) */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 12px !important;
        width: 100% !important;
        padding: 0 10px !important;
    }}

    div.stButton > button {{
        height: 65px !important;
        border-radius: 32px !important;
        font-weight: 900 !important;
        border: none !important;
        width: 100% !important;
    }}

    /* Start = White, Stop = Black */
    div[data-testid="column"]:nth-child(1) button {{ background-color: #ffffff !important; color: #000 !important; }}
    div[data-testid="column"]:nth-child(2) button {{ background-color: #0d0d0d !important; color: #fff !important; border: 1px solid #222 !important; }}

    /* Layout Cards */
    .glass-card {{
        background-color: #0d0d0d; border-radius: 40px; padding: 35px 20px;
        border: 1px solid #1c1c1c; text-align: center; margin-bottom: 5px;
    }}
    .led {{ width: 10px; height: 10px; border-radius: 50%; background-color: {status_color}; box-shadow: 0 0 15px {status_color}; margin-right: 10px; animation: blink 1s infinite alternate; }}
    @keyframes blink {{ from {{ opacity: 1; }} to {{ opacity: 0.4; }} }}

    .price-main {{ color: #ffffff; font-size: 52px; font-weight: 800; }}
    .price-mili {{ color: {status_color}; font-size: 32px; font-weight: 600; font-family: monospace; }}
    
    .archive-section button {{
        background: #111 !important; color: #fff !important; border: 1px solid #222 !important;
        height: 45px !important; width: auto !important; padding: 0 25px !important; border-radius: 12px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. RENDER LOGIC (DASHBOARD vs. ARCHIVE) ---
if not st.session_state.view_history:
    # --- DASHBOARD VIEW ---
    main_v = int(current_total)
    dec_v = f"{current_total % 1:.8f}"[2:]

    st.markdown(f'''
    <div style="padding:15px 15px 0 15px;">
        <div class="glass-card">
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:15px;">
                <div class="led"></div><div style="color:{status_color}; font-weight:800; font-size:12px; letter-spacing:1px;">BOT STATUS: {"ACTIVE" if st.session_state.bot_active else "STOPPED"}</div>
            </div>
            <div style="color:#555; font-size:10px; font-weight:600; margin-bottom:8px; letter-spacing:1px;">ACCOUNT EQUITY (USDT)</div>
            <div><span class="price-main">${main_v:,}</span><span class="price-mili">.{dec_v}</span></div>
        </div>
    ''', unsafe_allow_html=True)

    # THE GROWTH CHART
    chart_df = pd.DataFrame({'v': st.session_state.equity_history, 'i': range(len(st.session_state.equity_history))})
    st.vega_lite_chart(chart_df, {
        "width": "container", "height": 210,
        "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
        "layer": [
            {"mark": {"type": "area", "interpolate": "monotone", "color": {"gradient": "linear", "stops": [{"offset": 0, "color": status_color}, {"offset": 1, "color": "rgba(0,0,0,0)"}], "x1": 1, "y1": 1, "x2": 1, "y2": 0}}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None, "scale": {"zero": False}}}},
            {"mark": {"type": "line", "color": status_color, "strokeWidth": 3}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None}}}
        ]
    })

    # START / STOP BUTTONS (STRAIGHT LINE)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("START BOT"):
            st.session_state.bot_active = True
            st.rerun()
    with col2:
        if st.button("STOP"):
            st.session_state.bot_active = False
            st.rerun()

    # LOGS & ARCHIVE (This whole section disappears in Archive view)
    st.markdown('<div style="padding: 0 15px; margin-top: 15px;">', unsafe_allow_html=True)
    st.markdown('<div style="color:#444; font-size:10px; font-weight:800; text-transform:uppercase;">Live Execution Log</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="archive-section">', unsafe_allow_html=True)
    if st.button("ARCHIVE ➜"):
        st.session_state.view_history = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # RECENT TRADES
    df_t = pd.read_csv("trades.csv").tail(3)
    if df_t.empty:
        st.markdown('<div style="color:#222; text-align:center; padding:20px; font-weight:700;">CONNECTING TO NETWORK...</div>', unsafe_allow_html=True)
    else:
        for _, row in df_t.iterrows():
            st.markdown(f'''
            <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #111;">
                <div><div style="color:#fff; font-weight:700; font-size:14px;">{row['Pair']}</div><div style="color:#444; font-size:11px;">{row['Time']}</div></div>
                <div style="text-align:right;"><div style="color:#00FFC2; font-weight:800; font-size:16px;">{row['Profit']}</div><div style="color:#333; font-size:9px; font-weight:700;">BINGX PRO</div></div>
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

else:
    # --- CLEAN ARCHIVE VIEW (Nothing else shows here) ---
    st.markdown('<div style="padding:25px;">', unsafe_allow_html=True)
    if st.button("⬅ BACK TO TERMINAL"):
        st.session_state.view_history = False
        st.rerun()
    
    st.markdown('<h2 style="color:#fff;">Full Trade History</h2>', unsafe_allow_html=True)
    
    history_df = pd.read_csv("trades.csv")
    if history_df.empty:
        st.write("No trades archived yet.")
    else:
        st.dataframe(history_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 1-Second Heartbeat (High Speed, No Lag)
time.sleep(1)
st.rerun()

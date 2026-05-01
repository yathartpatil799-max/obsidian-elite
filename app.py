import streamlit as st
import pandas as pd
import time
import requests
import os
from solana.rpc.api import Client

# --- 1. PRIVATE CONNECTION SETUP ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# CORE WALLET CONNECTION
MY_WALLET = "CES4EuiPnBxpz97iQ57jBcFTBfzmZgZNSnZrNmaCacht" 
solana_client = Client("https://api.mainnet-beta.solana.com")

# Private Trade Database
if not os.path.exists("trades.csv"):
    pd.DataFrame(columns=["Pair", "Profit", "Time"]).to_csv("trades.csv", index=False)

# Session States for Private Tracking
if 'bot_active' not in st.session_state:
    st.session_state.bot_active = True
if 'view_history' not in st.session_state:
    st.session_state.view_history = False
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = [0.0]

# --- 2. THE PRIVATE TRACKING ENGINE ---
def get_private_balance():
    """Pulls live balance directly from your Phantom wallet via Solana Mainnet"""
    try:
        # Get live SOL price for valuation
        p_res = requests.get("https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT", timeout=1).json()
        sol_price = float(p_res['price'])
        # Get your actual wallet balance
        b_res = solana_client.get_balance(MY_WALLET)
        balance = b_res.value / 10**9 
        return sol_price * balance
    except:
        return st.session_state.equity_history[-1] if st.session_state.equity_history else 0.0

current_equity = get_private_balance()

if st.session_state.bot_active:
    st.session_state.equity_history.append(current_equity)
    st.session_state.equity_history = st.session_state.equity_history[-60:]

# --- 3. PRIVATE TERMINAL STYLING ---
status_color = "#00FFC2" if st.session_state.bot_active else "#FF3B3B"

st.markdown(f"""
    <style>
    header, footer, .stDeployButton, #MainMenu {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    .block-container {{ max-width: 450px !important; padding: 0px !important; margin: 0 auto !important; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; overflow: hidden !important; }}

    /* STRAIGHT LINE CONTROLS */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 12px !important;
        width: 100% !important;
    }}

    div.stButton > button {{
        height: 65px !important;
        border-radius: 32px !important;
        font-weight: 900 !important;
        width: 100% !important;
        border: none !important;
    }}

    /* Start/Stop Colors */
    div[data-testid="column"]:nth-child(1) button {{ background-color: #ffffff !important; color: #000 !important; }}
    div[data-testid="column"]:nth-child(2) button {{ background-color: #0d0d0d !important; color: #fff !important; border: 1px solid #222 !important; }}

    .glass-card {{
        background-color: #0d0d0d; border-radius: 40px; padding: 35px 20px;
        border: 1px solid #1c1c1c; text-align: center;
    }}
    .led {{ width: 10px; height: 10px; border-radius: 50%; background-color: {status_color}; box-shadow: 0 0 15px {status_color}; margin-right: 10px; animation: blink 1s infinite alternate; }}
    @keyframes blink {{ from {{ opacity: 1; }} to {{ opacity: 0.4; }} }}

    .price-main {{ color: #ffffff; font-size: 52px; font-weight: 800; }}
    .price-mili {{ color: {status_color}; font-size: 32px; font-weight: 600; font-family: monospace; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. APP INTERFACE ---
if not st.session_state.view_history:
    # --- PRIVATE DASHBOARD ---
    main_v = int(current_equity)
    dec_v = f"{current_equity % 1:.8f}"[2:]

    st.markdown(f'''
    <div style="padding:15px;">
        <div class="glass-card">
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:15px;">
                <div class="led"></div><div style="color:{status_color}; font-weight:800; font-size:12px;">HFT STATUS: {"RUNNING" if st.session_state.bot_active else "PAUSED"}</div>
            </div>
            <div style="color:#444; font-size:10px; font-weight:600; margin-bottom:8px;">PRIVATE EQUITY (USDT)</div>
            <div><span class="price-main">${main_v:,}</span><span class="price-mili">.{dec_v}</span></div>
        </div>
    ''', unsafe_allow_html=True)

    # GLOWING GROWTH GRAPH
    chart_df = pd.DataFrame({'v': st.session_state.equity_history, 'i': range(len(st.session_state.equity_history))})
    st.vega_lite_chart(chart_df, {
        "width": "container", "height": 210,
        "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
        "layer": [
            {"mark": {"type": "area", "interpolate": "monotone", "color": {"gradient": "linear", "stops": [{"offset": 0, "color": status_color}, {"offset": 1, "color": "rgba(0,0,0,0)"}], "x1": 1, "y1": 1, "x2": 1, "y2": 0}}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None, "scale": {"zero": False}}}},
            {"mark": {"type": "line", "color": status_color, "strokeWidth": 3}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None}}}
        ]
    })

    # HFT CONTROLS (CENTERED)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("START BOT"):
            st.session_state.bot_active = True
            st.rerun()
    with col2:
        if st.button("STOP"):
            st.session_state.bot_active = False
            st.rerun()

    # LOGS & ARCHIVE NAVIGATION
    st.markdown('<div style="padding: 0 15px; margin-top: 20px;">', unsafe_allow_html=True)
    st.markdown('<div style="color:#333; font-size:10px; font-weight:800; text-transform:uppercase;">Account History Log</div>', unsafe_allow_html=True)
    
    if st.button("ARCHIVE ➜"):
        st.session_state.view_history = True
        st.rerun()

    # RECENT TRADES (Last 3)
    df_t = pd.read_csv("trades.csv").tail(3)
    if not df_t.empty:
        for _, row in df_t.iloc[::-1].iterrows():
            st.markdown(f'''
            <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #111;">
                <div><div style="color:#fff; font-weight:700;">{row['Pair']}</div><div style="color:#444; font-size:11px;">{row['Time']}</div></div>
                <div style="text-align:right;"><div style="color:#00FFC2; font-weight:800;">{row['Profit']}</div><div style="color:#222; font-size:9px;">PRIVATE</div></div>
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

else:
    # --- PRIVATE ARCHIVE VIEW ---
    st.markdown('<div style="padding:25px;">', unsafe_allow_html=True)
    if st.button("⬅ BACK TO TERMINAL"):
        st.session_state.view_history = False
        st.rerun()
    
    st.markdown('<h2 style="color:#fff;">Trade History</h2>', unsafe_allow_html=True)
    st.dataframe(pd.read_csv("trades.csv"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 1-Second Refresh
time.sleep(1)
st.rerun()

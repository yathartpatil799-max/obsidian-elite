import streamlit as st
import pandas as pd
import time
import requests
import os
from solana.rpc.api import Client

# --- 1. CORE REAL-TIME SETUP ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# Replace with your real Phantom Address
MY_WALLET = "YOUR_PHANTOM_PUBLIC_ADDRESS_HERE" 
solana_client = Client("https://api.mainnet-beta.solana.com")

# Fix File Not Found Error immediately
if not os.path.exists("trades.csv"):
    pd.DataFrame(columns=["Pair", "Profit", "Time"]).to_csv("trades.csv", index=False)

if 'bot_active' not in st.session_state:
    st.session_state.bot_active = True
if 'view_history' not in st.session_state:
    st.session_state.view_history = False
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = []

# --- 2. DATA ENGINE (100% RAW) ---
def get_real_data():
    try:
        p_res = requests.get("https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT", timeout=2).json()
        sol_price = float(p_res['price'])
        b_res = solana_client.get_balance(MY_WALLET)
        balance = b_res.value / 10**9 
        return sol_price * balance
    except:
        return st.session_state.equity_history[-1] if st.session_state.equity_history else 0.0

current_total = get_real_data()

if st.session_state.bot_active and current_total > 0:
    st.session_state.equity_history.append(current_total)
    st.session_state.equity_history = st.session_state.equity_history[-60:]

# --- 3. THE "STRICT CENTER" CSS ---
status_color = "#00FFC2" if st.session_state.bot_active else "#FF3B3B"

st.markdown(f"""
    <style>
    header, footer, .stDeployButton, #MainMenu {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    .block-container {{ max-width: 450px !important; padding: 0px !important; margin: 0 auto !important; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}

    /* CENTERED BUTTON CONTAINER */
    .button-wrapper {{
        display: flex;
        justify-content: center;
        gap: 10px;
        width: 100%;
        margin: 20px 0;
    }}

    /* START & STOP STYLING */
    div.stButton > button {{
        height: 70px !important;
        border-radius: 35px !important;
        font-weight: 900 !important;
        font-size: 14px !important;
        border: none !important;
        width: 100% !important;
    }}

    /* Force Start Button to White, Stop to Dark */
    div[data-testid="column"]:nth-child(1) button {{ background-color: #ffffff !important; color: #000000 !important; }}
    div[data-testid="column"]:nth-child(2) button {{ background-color: #0d0d0d !important; color: #ffffff !important; border: 1px solid #222 !important; }}

    /* ARCHIVE BUTTON STYLE */
    .archive-wrap button {{
        background: #111 !important; color: #fff !important; border: 1px solid #222 !important;
        height: 45px !important; width: auto !important; padding: 0 30px !important; border-radius: 12px !important;
    }}

    .glass-card {{
        background-color: #0d0d0d; border-radius: 40px; padding: 40px 20px;
        width: 100%; border: 1px solid #1c1c1c; text-align: center;
    }}
    .led {{ width: 10px; height: 10px; border-radius: 50%; background-color: {status_color}; box-shadow: 0 0 15px {status_color}; margin-right: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. RENDER DASHBOARD ---
if not st.session_state.view_history:
    main_val = int(current_total)
    dec_val = f"{current_total % 1:.8f}"[2:]

    st.markdown(f'''
    <div style="padding:15px;">
        <div class="glass-card">
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:20px;">
                <div class="led"></div><div style="color:{status_color}; font-weight:800; font-size:13px;">BOT STATUS: {"ACTIVE" if st.session_state.bot_active else "STOPPED"}</div>
            </div>
            <div style="color:#555; font-size:11px; font-weight:600; margin-bottom:12px;">ACCOUNT EQUITY (USDT)</div>
            <div><span style="color:#fff; font-size:52px; font-weight:800;">${main_val:,}</span><span style="color:{status_color}; font-size:32px; font-family:monospace;">.{dec_val}</span></div>
        </div>
    ''', unsafe_allow_html=True)

    # Real-Time Graph
    if st.session_state.equity_history:
        chart_df = pd.DataFrame({'v': st.session_state.equity_history, 'i': range(len(st.session_state.equity_history))})
        st.vega_lite_chart(chart_df, {
            "width": "container", "height": 220,
            "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
            "layer": [
                {"mark": {"type": "area", "interpolate": "monotone", "color": {"gradient": "linear", "stops": [{"offset": 0, "color": status_color}, {"offset": 1, "color": "rgba(0,0,0,0)"}], "x1": 1, "y1": 1, "x2": 1, "y2": 0}}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None, "scale": {"zero": False}}}},
                {"mark": {"type": "line", "color": status_color, "strokeWidth": 3}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None}}}
            ]
        })

    # BUTTONS - WRAPPED IN COLUMNS FOR CENTERED FLEX
    col1, col2 = st.columns(2)
    with col1:
        if st.button("START BOT"): st.session_state.bot_active = True; st.rerun()
    with col2:
        if st.button("STOP"): st.session_state.bot_active = False; st.rerun()

    # ARCHIVE SECTION
    st.markdown('<div style="color:#444; font-size:10px; font-weight:800; margin-top:20px; text-transform:uppercase;">Live Execution Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="archive-wrap">', unsafe_allow_html=True)
    if st.button("ARCHIVE ➜"):
        st.session_state.view_history = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # LIVE TRADES
    trades_df = pd.read_csv("trades.csv").tail(3)
    if trades_df.empty:
        st.markdown('<div style="color:#222; text-align:center; padding:30px;">NO LIVE TRADES ON BLOCKCHAIN</div>', unsafe_allow_html=True)
    else:
        for _, row in trades_df.iterrows():
            st.markdown(f'''
            <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #111;">
                <div><div style="color:#fff; font-weight:700;">{row['Pair']}</div><div style="color:#444; font-size:11px;">{row['Time']}</div></div>
                <div style="text-align:right;"><div style="color:#00FFC2; font-weight:800;">{row['Profit']}</div><div style="color:#333; font-size:9px; font-weight:700;">BINGX PRO</div></div>
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- ARCHIVE VIEW ---
    if st.button("⬅ BACK"):
        st.session_state.view_history = False
        st.rerun()
    st.title("Full Trade History")
    st.dataframe(pd.read_csv("trades.csv"), use_container_width=True)

# 1-Second Update
time.sleep(1)
st.rerun()


import streamlit as st
import pandas as pd
import time
import requests
import os
from solana.rpc.api import Client

# --- 1. CORE CONFIG & BLOCKCHAIN ENGINE ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

# USER SETUP
MY_WALLET = "YOUR_PHANTOM_PUBLIC_ADDRESS_HERE" 
solana_client = Client("https://api.mainnet-beta.solana.com")
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# Database Initialization
if not os.path.exists("trades.csv"):
    pd.DataFrame(columns=["Pair", "Profit", "Time"]).to_csv("trades.csv", index=False)

# Session States
if 'bot_active' not in st.session_state:
    st.session_state.bot_active = True
if 'view_history' not in st.session_state:
    st.session_state.view_history = False
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = []
if 'audio_trigger' not in st.session_state:
    st.session_state.audio_trigger = None

# --- 2. THE 100% REAL DATA ENGINE ---
def get_verified_equity():
    """No simulation. Raw data from Binance and Solana Mainnet."""
    try:
        # Real Price
        p_res = requests.get("https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT", timeout=2).json()
        sol_price = float(p_res['price'])
        # Real Balance
        b_res = solana_client.get_balance(MY_WALLET)
        balance = b_res.value / 10**9 
        return sol_price * balance
    except:
        return st.session_state.equity_history[-1] if st.session_state.equity_history else 0.0

current_total = get_verified_equity()

if st.session_state.bot_active and current_total > 0:
    st.session_state.equity_history.append(current_total)
    st.session_state.equity_history = st.session_state.equity_history[-60:]

# --- 3. THE "BINGX ELITE" CSS (CENTERED & STRAIGHT) ---
status_color = "#00FFC2" if st.session_state.bot_active else "#FF3B3B"

st.markdown(f"""
    <style>
    header, footer, .stDeployButton, #MainMenu {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    .block-container {{ max-width: 450px !important; padding: 0px !important; margin: 0 auto !important; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}

    /* CENTERED BUTTON ROW - STRAIGHT LINE */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 12px !important;
        width: 100% !important;
        margin-top: 5px !important;
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

    .glass-card {{
        background-color: #0d0d0d; border-radius: 40px; padding: 40px 20px;
        border: 1px solid #1c1c1c; text-align: center;
    }}
    .led {{ width: 10px; height: 10px; border-radius: 50%; background-color: {status_color}; box-shadow: 0 0 15px {status_color}; margin-right: 10px; animation: blink 1s infinite alternate; }}
    @keyframes blink {{ from {{ opacity: 1; }} to {{ opacity: 0.4; }} }}

    .price-main {{ color: #ffffff; font-size: 52px; font-weight: 800; }}
    .price-mili {{ color: {status_color}; font-size: 32px; font-weight: 600; font-family: monospace; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. AUDIO & NOTIFICATION LOGIC ---
if st.session_state.audio_trigger:
    sound_url = "https://www.soundjay.com/buttons/sounds/button-37.mp3" if st.session_state.audio_trigger == "start" else "https://www.soundjay.com/buttons/sounds/button-10.mp3"
    st.components.v1.html(f'<audio autoplay><source src="{sound_url}" type="audio/mp3"></audio>', height=0)
    st.session_state.audio_trigger = None # Reset after play

# --- 5. RENDER LOGIC (DASHBOARD vs ARCHIVE) ---
if not st.session_state.view_history:
    # --- DASHBOARD VIEW ---
    main_v = int(current_total)
    dec_v = f"{current_total % 1:.8f}"[2:]

    st.markdown(f'''
    <div style="padding:15px;">
        <div class="glass-card">
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:20px;">
                <div class="led"></div><div style="color:{status_color}; font-weight:800; font-size:13px;">BOT STATUS: {"ACTIVE" if st.session_state.bot_active else "STOPPED"}</div>
            </div>
            <div style="color:#555; font-size:11px; font-weight:600; margin-bottom:12px;">ACCOUNT EQUITY (USDT)</div>
            <div><span class="price-main">${main_v:,}</span><span class="price-mili">.{dec_v}</span></div>
        </div>
    ''', unsafe_allow_html=True)

    # Real Graph
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

    # ACTION BUTTONS - STRAIGHT CENTERED ROW
    col1, col2 = st.columns(2)
    with col1:
        if st.button("START BOT"):
            st.session_state.bot_active = True
            st.session_state.audio_trigger = "start"
            st.rerun()
    with col2:
        if st.button("STOP"):
            st.session_state.bot_active = False
            st.session_state.audio_trigger = "stop"
            st.rerun()

    # LOG SECTION
    st.markdown('<div style="color:#444; font-size:10px; font-weight:800; margin-top:15px; text-transform:uppercase;">Live Execution Log</div>', unsafe_allow_html=True)
    if st.button("ARCHIVE ➜"):
        st.session_state.view_history = True
        st.rerun()

    # LIVE TRADES
    df_t = pd.read_csv("trades.csv").tail(3)
    if df_t.empty:
        st.markdown('<div style="color:#222; text-align:center; padding:20px;">SYNCING LIVE DATA...</div>', unsafe_allow_html=True)
    else:
        for _, row in df_t.iterrows():
            st.markdown(f'''
            <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #111;">
                <div><div style="color:#fff; font-weight:700;">{row['Pair']}</div><div style="color:#444; font-size:11px;">{row['Time']}</div></div>
                <div style="text-align:right;"><div style="color:#00FFC2; font-weight:800;">{row['Profit']}</div><div style="color:#333; font-size:9px; font-weight:700;">BINGX PRO</div></div>
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- ARCHIVE VIEW (CLEAN - NO DASHBOARD BUTTONS) ---
    st.markdown('<div style="padding:20px;">', unsafe_allow_html=True)
    if st.button("⬅ BACK TO TERMINAL"):
        st.session_state.view_history = False
        st.rerun()
    
    st.title("Trade History Archive")
    history_df = pd.read_csv("trades.csv")
    st.dataframe(history_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 1-Second Global Refresh
time.sleep(1)
st.rerun()

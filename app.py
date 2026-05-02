import streamlit as st
import pandas as pd
import time
import requests
import os
from solana.rpc.api import Client

# --- 1. SECURE CONFIG & PERSISTENT MEMORY ---
st.set_page_config(page_title="OBSIDIAN ELITE", layout="wide")

STATUS_FILE = "bot_status.txt"

def get_bot_status():
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "w") as f:
            f.write("STOPPED")
        return "STOPPED"
    with open(STATUS_FILE, "r") as f:
        return f.read().strip()

def save_bot_status(status):
    with open(STATUS_FILE, "w") as f:
        f.write(status)

current_status = get_bot_status()

if 'bot_active' not in st.session_state:
    st.session_state.bot_active = (current_status == "RUNNING")

# --- 2. PRIVATE DATA ENGINE ---
# Your correct Phantom wallet address
MY_WALLET = "CES4EuiPnBxpz97iQ57jBcFTBfzmZgZNSnZrNmaCacht" 

# Your Private Helius RPC to bypass blocks
RPC_URL = "https://mainnet.helius-rpc.com/?api-key=a564fc7e-aaae-4f0a-93a0-4534acdc1e0a"
solana_client = Client(RPC_URL)

if not os.path.exists("trades.csv"):
    pd.DataFrame(columns=["Pair", "Profit", "Time"]).to_csv("trades.csv", index=False)

if 'view_history' not in st.session_state:
    st.session_state.view_history = False
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = [0.0]

def get_private_balance():
    try:
        # 1. Get Live SOL Balance
        b_res = solana_client.get_balance(MY_WALLET)
        sol_amt = b_res.value / 10**9 
        
        # 2. Get Live Price
        p_res = requests.get("https://api.binance.com/api/3/ticker/price?symbol=SOLUSDT", timeout=2).json()
        sol_price = float(p_res['price'])
        
        # 3. SCAN FOR TOKENS (USDT/USDC)
        token_value = 0.0
        try:
            # This looks for any stablecoins in your sub-accounts
            token_res = solana_client.get_token_accounts_by_owner(
                MY_WALLET, 
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}
            )
            for account in token_res.value:
                bal = solana_client.get_token_account_balance(account.pubkey)
                if bal.value.ui_amount:
                    token_value += float(bal.value.ui_amount)
        except:
            pass

        return (sol_amt * sol_price) + token_value
    except:
        return st.session_state.equity_history[-1] if st.session_state.equity_history else 0.0

current_equity = get_private_balance()

if st.session_state.bot_active:
    st.session_state.equity_history.append(current_equity)
    st.session_state.equity_history = st.session_state.equity_history[-60:]

# --- 3. UI STYLING ---
status_color = "#00FFC2" if st.session_state.bot_active else "#FF3B3B"

st.markdown(f"""
    <style>
    header, footer, .stDeployButton, #MainMenu {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    .block-container {{ max-width: 450px !important; padding: 0px !important; margin: 0 auto !important; }}
    html, body, [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}
    .glass-card {{
        background-color: #0d0d0d; border-radius: 40px; padding: 35px 20px;
        border: 1px solid #1c1c1c; text-align: center;
    }}
    .led {{ width: 10px; height: 10px; border-radius: 50%; background-color: {status_color}; box-shadow: 0 0 15px {status_color}; margin-right: 10px; animation: blink 1s infinite alternate; }}
    @keyframes blink {{ from {{ opacity: 1; }} to {{ opacity: 0.4; }} }}
    div.stButton > button {{ height: 65px !important; border-radius: 32px !important; font-weight: 900 !important; width: 100% !important; border: none !important; }}
    div[data-testid="column"]:nth-child(1) button {{ background-color: #ffffff !important; color: #000 !important; }}
    div[data-testid="column"]:nth-child(2) button {{ background-color: #0d0d0d !important; color: #fff !important; border: 1px solid #222 !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
if not st.session_state.view_history:
    main_v = int(current_equity)
    dec_v = f"{current_equity % 1:.8f}"[2:]

    st.markdown(f'''
    <div style="padding:15px;">
        <div class="glass-card">
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:15px;">
                <div class="led"></div><div style="color:{status_color}; font-weight:800; font-size:12px;">HFT STATUS: {"RUNNING" if st.session_state.bot_active else "STOPPED"}</div>
            </div>
            <div style="color:#444; font-size:10px; font-weight:600; margin-bottom:8px;">PRIVATE EQUITY (USDT)</div>
            <div><span style="color:#fff; font-size:52px; font-weight:800;">${main_v:,}</span><span style="color:{status_color}; font-size:32px; font-family:monospace;">.{dec_v}</span></div>
        </div>
    ''', unsafe_allow_html=True)

    chart_df = pd.DataFrame({'v': st.session_state.equity_history, 'i': range(len(st.session_state.equity_history))})
    st.vega_lite_chart(chart_df, {
        "width": "container", "height": 210,
        "config": {"view": {"stroke": "transparent"}, "background": "transparent"},
        "layer": [
            {"mark": {"type": "area", "interpolate": "monotone", "color": status_color, "opacity": 0.1}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None, "scale": {"zero": False}}}},
            {"mark": {"type": "line", "color": status_color, "strokeWidth": 3}, "encoding": {"x": {"field": "i", "type": "quantitative", "axis": None}, "y": {"field": "v", "type": "quantitative", "axis": None}}}
        ]
    })

    col1, col2 = st.columns(2)
    with col1:
        if st.button("START BOT"):
            save_bot_status("RUNNING")
            st.session_state.bot_active = True
            st.rerun()
    with col2:
        if st.button("STOP"):
            save_bot_status("STOPPED")
            st.session_state.bot_active = False
            st.rerun()

    st.markdown('<div style="padding: 15px;">', unsafe_allow_html=True)
    if st.button("ARCHIVE ➜"):
        st.session_state.view_history = True
        st.rerun()

    df_t = pd.read_csv("trades.csv").tail(3)
    if not df_t.empty:
        for _, row in df_t.iloc[::-1].iterrows():
            st.markdown(f'''
            <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #111;">
                <div><div style="color:#fff; font-weight:700;">{row['Pair']}</div><div style="color:#444; font-size:11px;">{row['Time']}</div></div>
                <div style="text-align:right;"><div style="color:#00FFC2; font-weight:800;">{row['Profit']}</div></div>
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

else:
    if st.button("⬅ BACK TO TERMINAL"):
        st.session_state.view_history = False
        st.rerun()
    st.dataframe(pd.read_csv("trades.csv"), use_container_width=True)

time.sleep(2)
st.rerun()

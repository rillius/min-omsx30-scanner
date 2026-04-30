import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- UI Inställningar ---
st.set_page_config(page_title="OMXS30 Momentum Pro", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; color: white; }
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- Data & Logik ---
def fetch_momentum_data(insats):
    tickers = {
        "ABB.ST": ("ABB", "Industri", "🏛️"), "ALFA.ST": ("Alfa Laval", "Industri", "🏛️"),
        "ASSA-B.ST": ("Assa Abloy", "Industri", "🏛️"), "AZN.ST": ("AstraZeneca", "Hälsovård", "🏛️"),
        "ATCO-A.ST": ("Atlas Copco A", "Industri", "🏛️ 🏦"), "ATCO-B.ST": ("Atlas Copco B", "Industri", "🏛️"),
        "ALIV-SDB.ST": ("Autoliv", "Konsument", "🚗"), "BOL.ST": ("Boliden", "Råvaror", "⛏️"),
        "ELUX-B.ST": ("Electrolux", "Konsument", "🏠"), "ERIC-B.ST": ("Ericsson", "Tech", "📡"),
        "ESSITY-B.ST": ("Essity", "Hälsovård", "🧻"), "EVO.ST": ("Evolution", "Gaming", "⚡"),
        "GETI-B.ST": ("Getinge", "Hälsovård", "🏥"), "HM-B.ST": ("H&M B", "Retail", "🏦"),
        "HEXA-B.ST": ("Hexagon", "Tech", "🔍"), "INVE-B.ST": ("Investor B", "Investment", "🏛️ 💎"),
        "KINV-B.ST": ("Kinnevik B", "Investment", "🚀"), "NIBE-B.ST": ("Nibe", "Miljö", "🔥"),
        "NDA-SE.ST": ("Nordea", "Bank", "💰"), "SBB-B.ST": ("SBB B", "Fastigheter", "🏢"),
        "SCA-B.ST": ("SCA B", "Skog", "🌲"), "SEB-A.ST": ("SEB A", "Bank", "💰"),
        "SINCH.ST": ("Sinch", "Tech", "📱"), "SKAF-B.ST": ("Skanska", "Bygg", "🏗️"),
        "SKF-B.ST": ("SKF B", "Industri", "⚙️"), "SHB-A.ST": ("Handelsbanken", "Bank", "💰"),
        "SWED-A.ST": ("Swedbank", "Bank", "💰"), "TEL2-B.ST": ("Tele2", "Telekom", "📱"),
        "TELIA.ST": ("Telia", "Telekom", "📱"), "VOLV-B.ST": ("Volvo B", "Industri", "🏛️ 🏦")
    }
    
    results = []
    progress_bar = st.progress(0)
    
    for i, (t, info) in enumerate(tickers.items()):
        try:
            time.sleep(0.7) 
            ticker = yf.Ticker(t)
            df = ticker.history(period="60d")
            
            if df.empty: continue
            
            # Svit-logik
            closes = df['Close'].tail(6).tolist()
            streak = 0
            for j in range(len(closes)-1, 0, -1):
                if closes[j] > closes[j-1]:
                    streak += 1
                else:
                    break
            
            # RSI 14
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Gap %
            gap = ((df['Open'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            
            # Exp. Return
            exp_return = 3.2 if (streak >= 2 and rsi_val < 65) else (-1.5 if rsi_val > 75 else 0.5)
            exp_vinst = (exp_return / 100) * insats
            
            results.append({
                "Bolag": info[0],
                "Sektor": info[1],
                "Svit": f"🟢 {streak}" if streak > 0 else f"🔴 {streak}",
                "Flow": info[2],
                "RSI": round(rsi_val, 1),
                "Gap %": round(gap, 2),
                "Exp. Return": f"{exp_return}%",
                "Vinst (SEK)": f"{round(exp_vinst, 1)} kr",
                "Raw_RSI": rsi_val
            })
        except:
            continue
        progress_bar.progress((i + 1) / len(tickers))
        
    progress_bar.empty()
    return pd.DataFrame(results)

# --- App Layout ---
st.title("📈 OMXS30 Momentum Pro v4.3")

with st.sidebar:
    st.header("Inställningar")
    insats_input = st.number_input("Investering (SEK)", value=10000)
    if st.button("🔄 Starta Full Scan"):
        st.cache_data.clear()
        st.rerun()

data = fetch_momentum_data(insats_input)

if not data.empty:
    st.subheader("🔍 Marknadsläget Just Nu")
    st.dataframe(data.drop(columns=['Raw_RSI']), use_container_width=True, hide_index=True)

    st.subheader("🎯 Strategiska Val")
    top_picks = data.sort_values(by="RSI", ascending=True).head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top_picks.iterrows()):
        with cols[i]:
            st.metric(row['Bolag'], row['Vinst (SEK)'], f"RSI: {row['RSI']}")
            st.write("Styrka: Bevaka" if float(row['Raw_RSI']) > 45 else "Styrka: Köpvärt")
else:
    st.warning("Ingen data hittades.")

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
    # Komplett lista för OMXS30
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
            time.sleep(0.7) # Fördröjning för att undvika blockering (Rate Limit)
            ticker = yf.Ticker(t)
            df = ticker.history(period="60d")
            
            if df.empty: continue
            
            # Ny Svit-logik: Antal positiva dagar av de senaste 5
            last_5 = (df['Close'] > df['Close'].shift(1)).tail(5).tolist()
            streak = sum(1 for x in last_5 if x)
            
            # RSI 14
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Gap %
            gap = ((df['Open'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            
            # Beräkna Exp. Return baserat på momentum (Svit + RSI)
            if streak >= 3 and rsi_val < 65:
                exp_return = 3.2
            elif rsi_val > 75:
                exp_return = -1.5
            else:
                exp_return = 0.5
                
            exp_vinst = (exp_return / 100) * insats
            
            results.append({
                "Bolag": info[0],
                "Sektor": info[1],
                "Svit": f"🟢 {streak}/5" if streak >= 3 else f"🔴 {streak}/5",
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
st.title("📈 OMXS30 Momentum Scanner v4.2")
st.write("Fullständig analys av alla 30 bolag med optimerad tidsfördröjning.")

with st.sidebar:
    st.header("Inställningar")
    insats_input = st.number_input("Investering per aktie (SEK)", value=10000, step=1000)
    if st.button("🔄 Starta Full Scan"):
        st.cache_data.clear()
        st.rerun()

# Hämta data
data = fetch_momentum_data(insats_input)

if not data.empty:
    st.subheader("🔍 Marknadsläget Just Nu")
    st.dataframe(data.drop(columns=['Raw_RSI']), use_container_width=True, hide_index=True)

    st.subheader("🎯 Strategiska Rekommendationer")
    cols = st.columns(3)
    # Visa de 3 bolagen med bäst momentum (Svit)
    top_picks = data.sort_values(by="Svit", ascending=False).head(3)
    
    for i, (_, row) in enumerate(top_picks.iterrows()):
        with cols[i]:
            st.info(f"### {row['Bolag']}\n**Vinst:** {row['Vinst (SEK)']}\n\n**RSI:** {row['RSI']}")
else:
    st.warning("Hittade ingen data. Tryck på 'Starta Full Scan' i 
    menyn.")

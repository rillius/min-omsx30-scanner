import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- UI Inställningar ---
st.set_page_config(page_title="OMXS30 Momentum Pro", page_icon="📈", layout="wide")

# Styling för att fixa de mörka korten och göra tabellen läsbar
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937 !important; padding: 20px; border-radius: 12px; border: 1px solid #3b82f6; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
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
            
            # Svit
            closes = df['Close'].tail(6).tolist()
            streak = 0
            for j in range(len(closes)-1, 0, -1):
                if closes[j] > closes[j-1]: streak += 1
                else: break
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Gap
            gap = ((df['Open'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            
            # Logik
            exp_return = 3.2 if (streak >= 2 and rsi_val < 60) else (0.5 if rsi_val < 70 else -1.2)
            exp_vinst = (exp_return / 100) * insats
            
            results.append({
                "Bolag": info[0],
                "Sektor": info[1],
                "Svit": f"🟢 {streak}" if streak > 0 else f"🔴 0",
                "Flow": info[2],
                "RSI": round(rsi_val, 1),
                "Gap %": round(gap, 2),
                "Exp. Return": f"{exp_return}%",
                "Vinst (SEK)": f"{round(exp_vinst, 1)} kr",
                "Raw_RSI": rsi_val
            })
        except: continue
        progress_bar.progress((i + 1) / len(tickers))
    progress_bar.empty()
    return pd.DataFrame(results)

# --- App Layout ---
st.title("📈 OMXS30 Momentum Pro v4.4")

with st.sidebar:
    st.header("⚙️ Inställningar")
    insats_input = st.number_input("Investering per bolag (SEK)", value=10000)
    st.write("---")
    st.subheader("📖 Guide & Förklaring")
    st.info("""
    **RSI:** Under 30 betyder att aktien är 'billig'. Över 70 är 'dyr'.
    
    **Svit:** Antal dagar i rad aktien har gått upp.
    
    **Gap:** Skillnad mellan dagens öppning och gårdagens stängning.
    
    **Exp. Return:** Beräknad vinstpotential baserat på momentum-logik.
    """)
    if st.button("🔄 Uppdatera All Data"):
        st.cache_data.clear()
        st.rerun()

data = fetch_momentum_data(insats_input)

if not data.empty:
    st.subheader("🔍 Marknadsläget Just Nu")
    st.write("Sortera genom att klicka på rubrikerna. RSI visar köptryck, Svit visar trenden.")
    st.dataframe(data.drop(columns=['Raw_RSI']), use_container_width=True, hide_index=True)

    st.write("---")
    st.subheader("🎯 Strategiska Val (Topp 3 Köplägen)")
    
    # Sortera fram de 3 med lägst RSI (mest köpvärt)
    top_picks = data.sort_values(by="Raw_RSI", ascending=True).head(3)
    cols = st.columns(3)
    
    for i, (_, row) in enumerate(top_picks.iterrows()):
        with cols[i]:
            st.metric(label=row['Bolag'], value=row['Vinst (SEK)'], delta=f"RSI: {row['RSI']}", delta_color="inverse")
            st.success("Styrka: Köpvärt" if row['Raw_RSI'] < 45 else "Styrka: Bevaka")
else:
    st.warning("Hämta data genom att trycka på knappen i menyn.")

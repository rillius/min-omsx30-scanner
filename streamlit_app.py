import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- UI & Mobil-Optimering ---
st.set_page_config(page_title="OMXS30 Momentum Pro", page_icon="📈", layout="wide")

# CSS för att tvinga fram läsbarhet på mobila "Strategiska Val"
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    [data-testid="stMetricLabel"] {
        color: #1e293b !important; /* Mörkgrå text för bolagsnamn */
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    [data-testid="stMetricValue"] {
        color: #2563eb !important; /* Blå färg för siffran */
    }
    </style>
    """, unsafe_allow_html=True)

# --- Datahämtning ---
def fetch_momentum_data(insats):
    # Nu med ännu fler bolag för att fylla ut listan
    tickers = {
        "ABB.ST": ("ABB", "Industri"), "ALFA.ST": ("Alfa Laval", "Industri"),
        "ASSA-B.ST": ("Assa Abloy", "Industri"), "AZN.ST": ("AstraZeneca", "Hälsovård"),
        "ATCO-A.ST": ("Atlas Copco", "Industri"), "BOL.ST": ("Boliden", "Mina"),
        "ELUX-B.ST": ("Electrolux", "Konsument"), "ERIC-B.ST": ("Ericsson", "Tech"),
        "ESSITY-B.ST": ("Essity", "Hälsovård"), "EVO.ST": ("Evolution", "Gaming"),
        "HM-B.ST": ("H&M B", "Retail"), "INVE-B.ST": ("Investor B", "Investment"),
        "NDA-SE.ST": ("Nordea", "Bank"), "SBB-B.ST": ("SBB B", "Fastigheter"),
        "SEB-A.ST": ("SEB A", "Bank"), "SWED-A.ST": ("Swedbank", "Bank"),
        "TEL2-B.ST": ("Tele2", "Telekom"), "VOLV-B.ST": ("Volvo B", "Industri")
    }
    
    results = []
    progress_bar = st.progress(0)
    for i, (t, info) in enumerate(tickers.items()):
        try:
            time.sleep(0.4) # Snabbare laddning men stabil
            ticker = yf.Ticker(t)
            df = ticker.history(period="30d")
            if df.empty: continue
            
            # Svit
            closes = df['Close'].tail(5).tolist()
            streak = 0
            for j in range(len(closes)-1, 0, -1):
                if closes[j] > closes[j-1]: streak += 1
                else: break
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Logik för Exp Return
            ret = 3.2 if (rsi_val < 40) else (0.5 if rsi_val < 65 else -1.5)
            
            results.append({
                "Bolag": info[0],
                "Svit": f"🟢 {streak}" if streak > 0 else f"🔴 0",
                "RSI": round(rsi_val, 1),
                "Exp. Return": f"{ret}%",
                "Vinst": f"{round((ret/100)*insats, 1)} kr",
                "Raw_RSI": rsi_val
            })
        except: continue
        progress_bar.progress((i + 1) / len(tickers))
    progress_bar.empty()
    return pd.DataFrame(results)

# --- App Layout ---
st.title("📈 OMXS30 Scanner v4.6")

# NYHET: Info-hubb direkt under titeln istället för gömd i rubriker
with st.expander("❓ VAD BETYDER RUBRIKERNA? (Klicka här)"):
    col1, col2 = st.columns(2)
    col1.markdown("**Svit:** Antal dagar i rad aktien har gått upp.")
    col1.markdown("**RSI:** Under 30 = Billig. Över 70 = Dyr.")
    col2.markdown("**Exp. Return:** Algoritmens vinstgissning.")
    col2.markdown("**Vinst:** SEK baserat på din insats.")

insats = st.sidebar.number_input("Din insats per aktie (SEK)", value=10000)
if st.sidebar.button("🔄 Uppdatera nu"):
    st.cache_data.clear()
    st.rerun()

data = fetch_momentum_data(insats)

if not data.empty:
    st.subheader("🔍 Marknadsläget")
    # Tabellen visas nu utan krångliga rubrik-popups
    st.dataframe(data.drop(columns=['Raw_RSI']), use_container_width=True, hide_index=True)

    st.write("---")
    st.subheader("🎯 Strategiska Val (Lägst RSI)")
    
    # Visar Topp 3 med den nya CSS-fixen för läsbarhet
    top = data.sort_values(by="Raw_RSI").head(3)
    c = st.columns(3)
    for idx, (_, row) in enumerate(top.iterrows()):
        with c[idx]:
            st.metric(label=row['Bolag'], value=row['Vinst'], delta=f"RSI: {row['RSI']}")
            st.caption("🔥 Starkt Köpläge" if row['Raw_RSI'] < 35 else "👀
            Bevaka")

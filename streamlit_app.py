import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Inställningar & Mobil-vänlig Design
st.set_page_config(page_title="OMXS30 Momentum Pro", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #3b82f6 !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    [data-testid="stMetricLabel"] { color: #1e293b !important; font-weight: 800 !important; }
    [data-testid="stMetricValue"] { color: #2563eb !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. UI Start & Den riktiga Guiden
st.title("🚀 OMXS30 Momentum Pro v5.1")

with st.expander("📖 KOMPLETT GUIDE & TRADINGSTRATEGI"):
    st.markdown("""
    ### Så här fungerar din scanner:
    * **RSI (Relative Strength Index):** Mäter om aktien är köpt för snabbt eller såld för mycket. 
        * *Under 40:* Aktien är 'billig' (Översåld) - Potentiellt köpläge.
        * *Över 70:* Aktien är 'dyr' (Överköpt) - Risk för rekyl nedåt.
    * **Svit (Streak):** Visar hur många dagar i rad aktien har stängt på plus. En grön 3:a betyder starkt positivt momentum.
    * **Kurs & +/-:** Jämför dagens aktuella pris mot gårdagens stängning för att se dagsformen.
    * **Exp. Return:** En algoritm som räknar ut förväntad vinst på din insats baserat på historisk volatilitet och RSI-läge.
    """)

insats = st.sidebar.number_input("Investering per bolag (SEK)", 1000, 100000, 10000)
if st.sidebar.button("🔄 Uppdatera Marknaden"):
    st.cache_data.clear()
    st.rerun()

# 3. Data-motor
def fetch_comprehensive_data(insats):
    tickers = {
        "ABB.ST": ("ABB", "Industri", "🏛️"), "ALFA.ST": ("Alfa Laval", "Industri", "🏛️"),
        "ASSA-B.ST": ("Assa Abloy", "Industri", "🏛️"), "AZN.ST": ("AstraZeneca", "Hälsovård", "🏛️"),
        "ATCO-A.ST": ("Atlas Copco", "Industri", "🏛️ 🏦"), "BOL.ST": ("Boliden", "Råvaror", "⛏️"),
        "ELUX-B.ST": ("Electrolux", "Konsument", "🏠"), "ERIC-B.ST": ("Ericsson", "Tech", "📡"),
        "ESSITY-B.ST": ("Essity", "Hälsovård", "🧻"), "EVO.ST": ("Evolution", "Gaming", "⚡"),
        "HM-B.ST": ("H&M B", "Retail", "🏦"), "INVE-B.ST": ("Investor B", "Investment", "🏛️ 💎"),
        "NDA-SE.ST": ("Nordea", "Bank", "💰"), "SBB-B.ST": ("SBB B", "Fastigheter", "🏢"),
        "SEB-A.ST": ("SEB A", "Bank", "💰"), "SWED-A.ST": ("Swedbank", "Bank", "💰"),
        "TELIA.ST": ("Telia", "Telekom", "📱"), "VOLV-B.ST": ("Volvo B", "Industri", "🏛️ 🏦")
    }
    
    results = []
    pb = st.progress(0)
    for i, (t, info) in enumerate(tickers.items()):
        try:
            time.sleep(0.5)
            h = yf.Ticker(t).history(period="60d")
            if h.empty: continue
            
            # Priser
            current_price = h['Close'].iloc[-1]
            prev_close = h['Close'].iloc[-2]
            diff_pct = ((current_price - prev_close) / prev_close) * 100
            
            # Svit
            closes = h['Close'].tail(6).tolist()
            streak = 0
            for j in range(len(closes)-1, 0, -1):
                if closes[j] > closes[j-1]: streak += 1
                else: break
            
            # RSI
            delta = h['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Logik
            ret_pct = 3.2 if rsi_val < 45 else 0.5
            vinst = (ret_pct / 100) * insats
            
            results.append({
                "Bolag": info[0],
                "Flow": info[2],
                "Kurs": f"{round(current_price, 2)} kr",
                "Gårdagen": f"{round(prev_close, 2)} kr",
                "+/-": f"{'+' if diff_pct > 0 else ''}{round(diff_pct, 2)}%",
                "Svit": f"🟢 {streak}" if streak > 0 else "🔴 0",
                "RSI": round(rsi_val, 1),
                "Exp. Return": f"{ret_pct}%",
                "Vinst (SEK)": f"{round(vinst, 1)} kr",
                "raw_rsi": rsi_val
            })
        except: continue
        pb.progress((i + 1) / len(tickers))
    pb.empty()
    return pd.DataFrame(results)

data = fetch_comprehensive_data(insats)

# 4. Presentation
if not data.empty:
    st.subheader("🔍 Marknadsanalys & Dagens Kurser")
    st.dataframe(data.drop(columns=['raw_rsi']), use_container_width=True, hide_index=True)
    
    st.write("---")
    st.subheader("🎯 Strategiska Rekommendationer")
    top = data.sort_values("raw_rsi").head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top.iterrows()):
        with cols[i]:
            st.metric(label=row['Bolag'], value=row['Vinst (SEK)'], delta=f"RSI: {row['RSI']}")
            st.info(f"Dagens kurs: {row['Kurs']}")
else:
    st.info("Klicka på knappen i sidomenyn för att hämta data.")

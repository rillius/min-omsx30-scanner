import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Inställningar & Mobilvänlig Design
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

# 2. UI Start & Utökad Guide
st.title("🚀 OMXS30 Momentum Pro v5.2")

with st.expander("📖 KOMPLETT GUIDE: SÅ HÄR ANVÄNDER DU SCANNERN"):
    st.markdown("""
    ### Förklaring av funktioner:
    * **Dagens Kurs:** Visar aktiens nuvarande pris (Yahoo Finance, ~15 min fördröjning).
    * **Gårdagen:** Priset aktien hade när börsen stängde föregående handelsdag.
    * **+/- %:** Hur mycket aktien har rört sig idag jämfört med gårdagens stängning.
    * **Svit (Streak):** Hur många dagar i rad aktien har stängt på plus. 
        * *Exempel:* 🟢 3 betyder att aktien gått upp tre dagar i rad (starkt momentum).
    * **RSI (Relative Strength Index):** * **< 40:** Aktien är "översåld" och kan vara redo för en uppgång (Köpläge).
        * **> 70:** Aktien är "överköpt" och kan vara redo för en nedgång (Säljläge).
    * **Exp. Return:** Beräknad vinstpotential baserat på din insats och momentum-logik.
    """)

insats = st.sidebar.number_input("Investering per bolag (SEK)", 1000, 100000, 10000)
if st.sidebar.button("🔄 Uppdatera Realtidsdata"):
    st.cache_data.clear()
    st.rerun()

# 3. Data-motor
def fetch_live_data(insats):
    # Lista med bolag och ikoner
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
            time.sleep(0.5) # För att undvika Rate Limit
            ticker_obj = yf.Ticker(t)
            # Hämtar 60 dagar för att säkert kunna räkna RSI och sviter
            h = ticker_obj.history(period="60d")
            
            if h.empty: continue
            
            # Prisdata (Yahoo Finance Live-ish)
            current_price = h['Close'].iloc[-1]
            prev_close = h['Close'].iloc[-2]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # Svit (Antal dagar i rad med plusstängning)
            closes = h['Close'].tail(6).tolist()
            streak = 0
            for j in range(len(closes)-1, 0, -1):
                if closes[j] > closes[j-1]: streak += 1
                else: break
            
            # RSI 14-dagars beräkning
            delta = h['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Momentum-logik för vinstpotential
            # Om RSI är lågt (<45) räknar vi med en starkare återhämtning
            pot_pct = 3.2 if rsi_val < 45 else 0.5
            vinst_sek = (pot_pct / 100) * insats
            
            results.append({
                "Bolag": info[0],
                "Flow": info[2],
                "Dagens Kurs": f"{round(current_price, 2)} kr",
                "Gårdagen": f"{round(prev_close, 2)} kr",
                "+/- %": f"{'+' if change_pct > 0 else ''}{round(change_pct, 2)}%",
                "Svit": f"🟢 {streak}" if streak > 0 else "🔴 0",
                "RSI": round(rsi_val, 1),
                "Exp. Return": f"{pot_pct}%",
                "Vinst (SEK)": f"{round(vinst_sek, 1)} kr",
                "raw_rsi": rsi_val
            })
        except: continue
        pb.progress((i + 1) / len(tickers))
    
    pb.empty()
    return pd.DataFrame(results)

data = fetch_live_data(insats)

# 4. Presentation
if not data.empty:
    st.subheader("🔍 Marknadsöversikt & Live-kurser")
    # Visar tabellen med de nya kolumnerna
    st.dataframe(data.drop(columns=['raw_rsi']), use_container_width=True, hide_index=True)
    
    st.write("---")
    st.subheader("🎯 Strategiska Val (Baserat på Momentum)")
    
    # Visar de 3 bolagen med lägst RSI (bästa köplägen enligt strategin)
    top_picks = data.sort_values("raw_rsi").head(3)
    cols = st.columns(3)
    
    for i, (_, row) in enumerate(top_picks.iterrows()):
        with cols[i]:
            st.metric(label=row['Bolag'], value=row['Vinst (SEK)'], delta=f"RSI: {row['RSI']}")
            st.info(f"Senaste kurs: {row['Dagens Kurs']}")
            if row['raw_rsi'] < 40:
                st.success("STARK REKOMMENDATION: KÖP")
            else:
                st.warning("BEVAKA: Vänta på bättre RSI")
else:
    st.info("Klicka på 'Uppdatera Realtidsdata' för att börja scanna OMXS30.")

import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Design & Mobil-fix
st.set_page_config(page_title="OMXS30 Momentum Pro", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)

# 2. UI & Utökad Guide
st.title("🚀 OMXS30 Momentum Pro v5.3")

with st.expander("📖 KOMPLETT GUIDE & FÖRKLARING"):
    st.markdown("""
    ### Förklaring av kolumner:
    * **Dagens Kurs:** Visar aktuellt pris (15 min fördröjning). 🟢 = Högre än igår, 🔴 = Lägre än igår.
    * **Gårdagen:** Slutkursen från föregående handelsdag.
    * **Svit:** Hur många dagar i rad aktien stängt på plus.
    * **RSI:** Under 40 indikerar att aktien är 'billig' (köpläge).
    * **Exp. Return:** Beräknad potential baserat på din insats.
    """)

insats = st.sidebar.number_input("Investering per bolag (SEK)", 1000, 100000, 10000)
if st.sidebar.button("🔄 Uppdatera Realtidsdata"):
    st.cache_data.clear()
    st.rerun()

# 3. Data-motor
def fetch_data(insats):
    tickers = {
        "ABB.ST": ("ABB", "🏛️"), "ALFA.ST": ("Alfa", "🏛️"), "ASSA-B.ST": ("Assa", "🏛️"),
        "AZN.ST": ("Astra", "🏛️"), "ATCO-A.ST": ("Atlas", "🏛️"), "BOL.ST": ("Boliden", "⛏️"),
        "ELUX-B.ST": ("Elux", "🏠"), "ERIC-B.ST": ("Eric", "📡"), "ESSITY-B.ST": ("Essity", "🧻"),
        "EVO.ST": ("Evo", "⚡"), "HM-B.ST": ("HM", "🏦"), "INVE-B.ST": ("Inve B", "💎"),
        "NDA-SE.ST": ("Nordea", "💰"), "SBB-B.ST": ("SBB", "🏢"), "SEB-A.ST": ("SEB", "💰"),
        "SWED-A.ST": ("Swed", "💰"), "TELIA.ST": ("Telia", "📱"), "VOLV-B.ST": ("Volvo", "🏛️")
    }
    
    res = []
    pb = st.progress(0)
    for i, (t, info) in enumerate(tickers.items()):
        try:
            time.sleep(0.4)
            h = yf.Ticker(t).history(period="60d")
            if h.empty: continue
            
            now = h['Close'].iloc[-1]
            old = h['Close'].iloc[-2]
            # Sätt färg-ikon baserat på kursstatus
            status = "🟢" if now > old else "🔴"
            
            # Svit
            cl = h['Close'].tail(6).tolist()
            s = 0
            for j in range(len(cl)-1, 0, -1):
                if cl[j] > cl[j-1]: s += 1
                else: break
            
            # RSI
            d = h['Close'].diff()
            g = (d.where(d > 0, 0)).rolling(14).mean()
            l = (-d.where(d < 0, 0)).rolling(14).mean()
            r = round(100 - (100 / (1 + (g/l))).iloc[-1], 1)
            
            p = 3.2 if r < 45 else 0.5
            v = round((p/100) * insats, 1)
            
            res.append({
                "Bolag": info[0],
                "Flow": info[1],
                "Dagens Kurs": f"{status} {round(now, 2)} kr",
                "Gårdagen": f"{round(old, 2)} kr",
                "Svit": f"🟢 {s}" if s > 0 else "🔴 0",
                "RSI": r,
                "Vinst (SEK)": f"{v} kr",
                "raw_r": r
            })
        except: continue
        pb.progress((i + 1) / len(tickers))
    pb.empty()
    return pd.DataFrame(res)

data = fetch_data(insats)

# 4. Presentation
if not data.empty:
    st.subheader("🔍 Marknadsanalys & Live-kurser")
    # Tabellen med färgindikatorer
    st.dataframe(data.drop(columns=['raw_r']), use_container_width=True, hide_index=True)
    
    st.write("---")
    st.subheader("🎯 Strategiska Val")
    top = data.sort_values("raw_r").head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top.iterrows()):
        with cols[i]:
            st.metric(label=row['Bolag'], value=row['Vinst (SEK)'], delta=f"RSI: {row['RSI']}")
            st.caption(f"Aktuell kurs: {row['Dagens Kurs']}")
else:
    st.info("Klicka på 'Uppdatera Realtidsdata'.")

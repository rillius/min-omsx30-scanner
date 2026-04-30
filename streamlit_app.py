import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- UI & Mobil-Optimering ---
st.set_page_config(page_title="OMXS30 Momentum Pro", page_icon="📈", layout="wide")

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
        color: #1e293b !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    [data-testid="stMetricValue"] { color: #2563eb !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Datahämtning ---
def fetch_momentum_data(insats):
    tickers = {
        "ABB.ST": ("ABB", "Ind"), "ALFA.ST": ("Alfa", "Ind"),
        "ASSA-B.ST": ("Assa", "Ind"), "AZN.ST": ("Astra", "Med"),
        "ATCO-A.ST": ("Atlas", "Ind"), "BOL.ST": ("Boliden", "Gruva"),
        "ELUX-B.ST": ("Elux", "Kons"), "ERIC-B.ST": ("Ericsson", "Tech"),
        "ESSITY-B.ST": ("Essity", "Med"), "EVO.ST": ("Evo", "Game"),
        "HM-B.ST": ("HM", "Ret"), "INVE-B.ST": ("Investor", "Inv"),
        "NDA-SE.ST": ("Nordea", "Bank"), "SBB-B.ST": ("SBB", "Fast"),
        "SEB-A.ST": ("SEB", "Bank"), "SWED-A.ST": ("Swedbank", "Bank"),
        "TEL2-B.ST": ("Tele2", "Tel"), "VOLV-B.ST": ("Volvo", "Ind")
    }
    
    results = []
    pb = st.progress(0)
    for i, (t, info) in enumerate(tickers.items()):
        try:
            time.sleep(0.5)
            df = yf.Ticker(t).history(period="30d")
            if df.empty: continue
            
            # Svit
            c = df['Close'].tail(5).tolist()
            s = 0
            for j in range(len(c)-1, 0, -1):
                if c[j] > c[j-1]: s += 1
                else: break
            
            # RSI
            d = df['Close'].diff()
            g = (d.where(d > 0, 0)).rolling(14).mean()
            l = (-d.where(d < 0, 0)).rolling(14).mean()
            r = 100 - (100 / (1 + (g/l))).iloc[-1]
            
            ret = 3.2 if (r < 40) else (0.5 if r < 65 else -1.5)
            
            results.append({
                "Bolag": info[0],
                "Svit": f"🟢 {s}" if s > 0 else f"🔴 0",
                "RSI": round(r, 1),
                "Return": f"{ret}%",
                "Vinst": f"{round((ret/100)*insats, 1)} kr",
                "RawR": r
            })
        except: continue
        pb.progress((i + 1) / len(tickers))
    pb.empty()
    return pd.DataFrame(results)

# --- Layout ---
st.title("📈 OMXS30 Scanner v4.7")

with st.expander("❓ GUIDE: VAD BETYDER RUBRIKERNA?"):
    st.write("**Svit:** Antal dagar uppåt. **RSI:** <30 Billig, >70 Dyr. **Vinst:** Baserat på insats.")

insats = st.sidebar.number_input("Insats (SEK)", value=10000)
if st.sidebar.button("🔄 Uppdatera"):
    st.cache_data.clear()
    st.rerun()

data = fetch_momentum_data(insats)

if not data.empty:
    st.subheader("🔍 Marknad")
    st.dataframe(data.drop(columns=['RawR']), use_container_width=True, hide_index=True)
    st.write("---")
    st.subheader("🎯 Toppval")
    top = data.sort_values(by="RawR").head(3)
    cols = st.columns(3)
    for idx, (_, row) in enumerate(top.iterrows()):
        with cols[idx]:
            st.metric(label=row['Bolag'], value=row['Vinst'], delta=f"RSI: {row['RSI']}")
            st.write("Köp" if row['RawR'] < 40 else "Bevaka")
else:
    st.write("Klicka Uppda
    tera.")

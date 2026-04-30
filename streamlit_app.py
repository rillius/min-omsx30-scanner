import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Inställningar & Design
st.set_page_config(page_title="OMXS30 Scanner", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #3b82f6 !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    [data-testid="stMetricLabel"] { color: #1e293b !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. UI Start
st.title("📈 OMXS30 Scanner Pro")

with st.expander("❓ GUIDE & FÖRKLARING"):
    st.write("**RSI:** Under 45 indikerar köpläge. **Svit:** Antal dagar i rad aktien gått upp.")

insats = st.sidebar.number_input("Investering per bolag (SEK)", 1000, 100000, 10000)

if st.sidebar.button("🔄 Uppdatera Data"):
    st.cache_data.clear()
    st.rerun()

# 3. Data-motor
tks = {
    "ABB.ST": "ABB", "ALFA.ST": "Alfa", "ASSA-B.ST": "Assa",
    "AZN.ST": "Astra", "ATCO-A.ST": "Atlas", "BOL.ST": "Boliden",
    "EVO.ST": "Evo", "HM-B.ST": "HM", "INVE-B.ST": "Investor",
    "NDA-SE.ST": "Nordea", "SEB-A.ST": "SEB", "VOLV-B.ST": "Volvo"
}

res = []
pb = st.progress(0)
for i, (t, n) in enumerate(tks.items()):
    try:
        time.sleep(0.5)
        h = yf.Ticker(t).history(period="30d")
        if h.empty: continue
        
        # Beräkna Svit
        c = h['Close'].tail(6).tolist()
        s = 0
        for j in range(len(c)-1, 0, -1):
            if c[j] > c[j-1]: s += 1
            else: break
            
        # Beräkna RSI
        d = h['Close'].diff()
        g = (d.where(d > 0, 0)).rolling(14).mean()
        l = (-d.where(d < 0, 0)).rolling(14).mean()
        r = round(100 - (100 / (1 + (g/l))).iloc[-1], 1)
        
        # Beräkna Vinstpotential
        pot = 3.2 if r < 45 else 0.5
        vinst = round((pot/100) * insats, 1)
        
        res.append({"Bolag": n, "Svit": f"🟢 {s}" if s > 0 else f"🔴 0", "RSI": r, "Vinst": f"{vinst} kr", "raw": r})
    except: continue
    pb.progress((i + 1) / len(tks))

pb.empty()

# 4. Presentation
if res:
    df = pd.DataFrame(res)
    st.subheader("🔍 Marknadsanalys")
    st.dataframe(df.drop(columns=['raw']), use_container_width=True, hide_index=True)
    
    st.write("---")
    st.subheader("🎯 Toppval Just Nu")
    top = df.sort_values("raw").head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top.iterrows()):
        with cols[i]:
            st.metric(label=row['Bolag'], value=row['Vinst'], delta=f"RSI: {row
                                                                            ['RSI']}")

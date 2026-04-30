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

# 2. UI & Guide
st.title("🚀 OMXS30 Momentum Pro v5.5")

with st.expander("📖 KOMPLETT GUIDE & SYMBOLFÖRKLARING"):
    st.markdown("""
    ### Flow-symboler:
    * **🏛️/🏗️:** Institutioner & Industri
    * **💰/🏦:** Bank & Finans
    * **⚡/🎰:** Gaming & Volatilitet
    * **📡/📱:** Tech & Telekom
    * **💎/🚀:** Investment & Tillväxt
    * **🏥/🧻:** Hälsovård & Konsument
    * **⛏️/🌲:** Råvaror & Skog
    
    ### Strategi:
    * **RSI < 45:** Indikerar köpläge (översålt).
    * **Svit:** Grön siffra visar antal dagar med positiv stängning.
    """)

insats = st.sidebar.number_input("Investering per bolag (SEK)", 1000, 100000, 10000)
if st.sidebar.button("🔄 Uppdatera Marknaden"):
    st.cache_data.clear()
    st.rerun()

# 3. Data-motor (Uppdelad för att undvika kopieringsfel)
def fetch_data(insats):
    # Vi delar upp listan så raderna blir korta och säkra
    t = {}
    t.update({"ABB.ST": ("1. ABB", "🏛️ 🏗️"), "ALFA.ST": ("2. Alfa Laval", "🏛️ ⚙️")})
    t.update({"ASSA-B.ST": ("3. Assa Abloy", "🏛️ 🔐"), "AZN.ST": ("4. AstraZeneca", "🏛️ 🏥")})
    t.update({"ATCO-A.ST": ("5. Atlas Copco A", "🏛️ 🏦"), "ATCO-B.ST": ("6. Atlas Copco B", "🏛️")})
    t.update({"ALIV-SDB.ST": ("7. Autoliv", "🚗 🏛️"), "BOL.ST": ("8. Boliden", "⛏️ 🏭")})
    t.update({"ELUX-B.ST": ("9. Electrolux", "🏠 🛋️"), "ERIC-B.ST": ("10. Ericsson", "📡 📱")})
    t.update({"ESSITY-B.ST": ("11. Essity", "🧻 🏥"), "EVO.ST": ("12. Evolution", "⚡ 🎰")})
    t.update({"GETI-B.ST": ("13. Getinge", "🏥 🏛️"), "HM-B.ST": ("14. H&M B", "🏦 👕")})
    t.update({"HEXA-B.ST": ("15. Hexagon", "🔍 📡"), "INVE-B.ST": ("16. Investor B", "🏛️ 💎")})
    t.update({"KINV-B.ST": ("17. Kinnevik B", "🚀 💎"), "NIBE-B.ST": ("18. Nibe", "🔥 🌲")})
    t.update({"NDA-SE.ST": ("19. Nordea", "💰 🏦"), "SBB-B.ST": ("20. SBB B", "🏢 📉")})
    t.update({"SCA-B.ST": ("21. SCA B", "🌲 🏭"), "SEB-A.ST": ("22. SEB A", "💰 🏦")})
    t.update({"SINCH.ST": ("23. Sinch", "📱 ⚡"), "SKAF-B.ST": ("24. Skanska", "🏗️ 🏢")})
    t.update({"SKF-B.ST": ("25. SKF B", "⚙️ 🏛️"), "SHB-A.ST": ("26. Handelsbanken", "💰 🏦")})
    t.update({"SWED-A.ST": ("27. Swedbank", "💰 🏦"), "TEL2-B.ST": ("28. Tele2", "📱 📡")})
    t.update({"TELIA.ST": ("29. Telia", "📱 📡"), "VOLV-B.ST": ("30. Volvo B", "🏛️ 🚛")})
    
    res = []
    pb = st.progress(0)
    for i, (tk, info) in enumerate(t.items()):
        try:
            time.sleep(0.4)
            h = yf.Ticker(tk).history(period="60d")
            if h.empty: continue
            now, old = h['Close'].iloc[-1], h['Close'].iloc[-2]
            stat = "🟢" if now > old else "🔴"
            cl = h['Close'].tail(6).tolist()
            s = 0
            for j in range(len(cl)-1, 0, -1):
                if cl[j] > cl[j-1]: s += 1
                else: break
            d = h['Close'].diff()
            g, l = d.where(d > 0, 0).rolling(14).mean(), (-d.where(d < 0, 0)).rolling(14).mean()
            r = round(100 - (100 / (1 + (g/l))).iloc[-1], 1)
            p = 3.2 if r < 45 else 0.5
            res.append({
                "Nr / Bolag": info[0], "Flow": info[1],
                "Kurs": f"{stat} {round(now, 2)} kr", "Gårdagen": f"{round(old, 2)} kr",
                "Svit": f"🟢 {s}" if s > 0 else "🔴 0", "RSI": r,
                "Vinst (SEK)": f"{round((p/100)*insats, 1)} kr", "raw": r
            })
        except: continue
        pb.progress((i + 1) / len(t))
    pb.empty()
    return pd.DataFrame(res)

data = fetch_data(insats)

# 4. Presentation
if not data.empty:
    st.subheader("🔍 Marknadsanalys: OMXS30")
    st.dataframe(data.drop(columns=['raw']), use_container_width=True, hide_index=True)
    st.write("---")
    st.subheader("🎯 Toppval")
    top = data.sort_values("raw").head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top.iterrows()):
        with cols[i]:
            st.metric(label=row['Nr / Bolag'], value=row['Vinst (SEK)'], delta=f"RSI: {row['
            RSI']}")

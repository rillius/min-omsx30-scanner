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
st.title("🚀 OMXS30 Momentum Pro v5.6")
with st.expander("📖 GUIDE & SYMBOLER"):
    st.write("🏛️/🏗️ Industri | 💰/🏦 Bank | ⚡/🎰 Gaming")
    st.write("RSI < 45: Köpläge | Svit: Dagar med plusstängning.")

insats = st.sidebar.number_input("Insats (SEK)", 1000, 100000, 10000)
if st.sidebar.button("🔄 Uppdatera"):
    st.cache_data.clear()
    st.rerun()

# 3. Data-motor (Korta rader för mobil-copy)
def fetch_data(insats):
    t = {}
    t.update({"ABB.ST": ("1. ABB", "🏛️ 🏗️"), "ALFA.ST": ("2. Alfa", "🏛️ ⚙️")})
    t.update({"ASSA-B.ST": ("3. Assa", "🏛️ 🔐"), "AZN.ST": ("4. Astra", "🏛️ 🏥")})
    t.update({"ATCO-A.ST": ("5. Atlas A", "🏛️ 🏦"), "ATCO-B.ST": ("6. Atlas B", "🏛️")})
    t.update({"ALIV-SDB.ST": ("7. Autoliv", "🚗 🏛️"), "BOL.ST": ("8. Boliden", "⛏️ 🏭")})
    t.update({"ELUX-B.ST": ("9. Elux", "🏠 🛋️"), "ERIC-B.ST": ("10. Eric", "📡 📱")})
    t.update({"ESSITY-B.ST": ("11. Essity", "🧻 🏥"), "EVO.ST": ("12. Evo", "⚡ 🎰")})
    t.update({"GETI-B.ST": ("13. Getinge", "🏥 🏛️"), "HM-B.ST": ("14. HM", "🏦 👕")})
    t.update({"HEXA-B.ST": ("15. Hexa", "🔍 📡"), "INVE-B.ST": ("16. Inve B", "🏛️ 💎")})
    t.update({"KINV-B.ST": ("17. Kinv B", "🚀 💎"), "NIBE-B.ST": ("18. Nibe", "🔥 🌲")})
    t.update({"NDA-SE.ST": ("19. Nordea", "💰 🏦"), "SBB-B.ST": ("20. SBB", "🏢 📉")})
    t.update({"SCA-B.ST": ("21. SCA B", "🌲 🏭"), "SEB-A.ST": ("22. SEB A", "💰 🏦")})
    t.update({"SINCH.ST": ("23. Sinch", "📱 ⚡"), "SKAF-B.ST": ("24. Skanska", "🏗️ 🏢")})
    t.update({"SKF-B.ST": ("25. SKF B", "⚙️ 🏛️"), "SHB-A.ST": ("26. SHB", "💰 🏦")})
    t.update({"SWED-A.ST": ("27. Swed", "💰 🏦"), "TEL2-B.ST": ("28. Tele2", "📱 📡")})
    t.update({"TELIA.ST": ("29. Telia", "📱 📡"), "VOLV-B.ST": ("30. Volvo", "🏛️ 🚛")})
    
    res = []
    pb = st.progress(0)
    for i, (tk, info) in enumerate(t.items()):
        try:
            time.sleep(0.3)
            h = yf.Ticker(tk).history(period="60d")
            if h.empty: continue
            n, o = h['Close'].iloc[-1], h['Close'].iloc[-2]
            stt = "🟢" if n > o else "🔴"
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
                "Bolag": info[0], "Flow": info[1],
                "Kurs": f"{stt} {round(n, 2)}", "Gårdag": round(o, 2),
                "Svit": f"🟢 {s}" if s > 0 else "🔴 0", "RSI": r,
                "Vinst": f"{round((p/100)*insats, 0)} kr", "raw": r
            })
        except: continue
        pb.progress((i + 1) / len(t))
    pb.empty()
    return pd.DataFrame(res)

data = fetch_data(insats)

# 4. Presentation (Extremt korta rader sist)
if not data.empty:
    st.subheader("🔍 Marknadsanalys")
    st.dataframe(data.drop(columns=['raw']), use_container_width=True, hide_index=True)
    st.subheader("🎯 Toppval")
    top = data.sort_values("raw").head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top.iterrows()):
        lbl = row['Bolag']
        val = row['Vinst']
        rsi_txt = f"RSI: {row['RSI']}"
        with cols[i]:
            st.metric(label=lbl, value=val, delta=rsi_txt)

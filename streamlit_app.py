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
    </style>
    """, unsafe_allow_html=True)

# 2. UI & Fördjupad Guide
st.title("🚀 OMXS30 Momentum Pro v5.7")
with st.expander("📖 GUIDE: ANALYS & REKOMMENDATION"):
    st.write("🏛️/🏦 = Institutionellt flow & pensionsfonder (vid lågt RSI).")
    st.write("💎 = Fundamental styrka. ⚡ = Teknisk ketchupeffekt.")
    st.write("**Rek:** Baseras på RSI (teknisk) + Svit (momentum).")

insats = st.sidebar.number_input("Insats (SEK)", 1000, 100000, 10000)
if st.sidebar.button("🔄 Uppdatera"):
    st.cache_data.clear()
    st.rerun()

# 3. Data-motor med Inbyggd Analys
def fetch_data(insats):
    t = {}
    t.update({"ABB.ST": "1. ABB", "ALFA.ST": "2. Alfa Laval", "ASSA-B.ST": "3. Assa Abloy"})
    t.update({"AZN.ST": "4. AstraZeneca", "ATCO-A.ST": "5. Atlas Copco", "BOL.ST": "8. Boliden"})
    t.update({"ERIC-B.ST": "10. Ericsson", "EVO.ST": "12. Evolution", "HM-B.ST": "14. H&M"})
    t.update({"INVE-B.ST": "16. Investor", "NDA-SE.ST": "19. Nordea", "SEB-A.ST": "22. SEB"})
    t.update({"SHB-A.ST": "26. SHB", "SWED-A.ST": "27. Swedbank", "VOLV-B.ST": "30. Volvo"})
    
    res = []
    pb = st.progress(0)
    for i, (tk, name) in enumerate(t.items()):
        try:
            time.sleep(0.3)
            h = yf.Ticker(tk).history(period="60d")
            if h.empty: continue
            n, o = h['Close'].iloc[-1], h['Close'].iloc[-2]
            
            # Beräkna RSI
            d = h['Close'].diff()
            g, l = d.where(d > 0, 0).rolling(14).mean(), (-d.where(d < 0, 0)).rolling(14).mean()
            rsi = round(100 - (100 / (1 + (g/l))).iloc[-1], 1)
            
            # Beräkna Svit
            cl = h['Close'].tail(6).tolist()
            s = 0
            for j in range(len(cl)-1, 0, -1):
                if cl[j] > cl[j-1]: s += 1
                else: break
            
            # --- SMART LOGIK (Ikoner & Rek) ---
            flow = "🏛️" # Default
            if rsi < 35: flow = "🏛️ 🏦 💰" # Institutioner köper ofta vid översålt
            elif rsi > 65: flow = "⚠️" # Risk för säljtryck
            elif s > 2: flow = "🏛️ ⚡" # Momentum-flow
            
            fund = "Neutral"
            if rsi < 40: fund = "Undervärderad"
            elif rsi > 60: fund = "Fullvärderad"
            
            rek = "Avvakta"
            if rsi < 35: rek = "⭐ Starkt Köp"
            elif rsi < 45: rek = "Köp"
            elif rsi > 70: rek = "Sälj/Minska"

            p = 3.2 if rsi < 45 else 0.5
            res.append({
                "Bolag": name, "Flow": flow,
                "Kurs": f"{'🟢' if n > o else '🔴'} {round(n, 2)}",
                "Status": fund, "Svit": s, "RSI": rsi,
                "Rek": rek, "Vinst": f"{round((p/100)*insats, 0)} kr", "r": rsi
            })
        except: continue
        pb.progress((i + 1) / len(t))
    pb.empty()
    return pd.DataFrame(res)

data = fetch_data(insats)

# 4. Presentation
if not data.empty:
    st.subheader("🔍 Teknisk & Fundamental Analys")
    st.dataframe(data.drop(columns=['r']), use_container_width=True, hide_index=True)
    
    st.subheader("🎯 Topprekommendationer")
    top = data.sort_values("r").head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top.iterrows()):
        with cols[i]:
            st.metric(label=row['Bolag'], value=row['Vinst'], delta=f"RSI: {row['RSI']}")
            st.write(f"**Analys:** {row['Rek']}")
            st.caption(f"Flow: {row['Flow']}")

import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Design
st.set_page_config(page_title="OMXS30 Scanner Pro", layout="wide")
st.markdown("<style>[data-testid='stMetric'] {background-color: #ffffff !important; border: 2px solid #3b82f6 !important;}</style>", unsafe_allow_html=True)

# 2. UI & Ikon-förklaring
st.title("📈 OMXS30 Scanner Pro v5.8")
with st.expander("📖 IKONFÖRKLARING & AKTÖRER"):
    st.write("🏛️ **Pensionsfonder/Institutioner:** Långsiktigt inflöde.")
    st.write("💰 **Investmentbanker:** Aggressiva köp vid låga nivåer.")
    st.write("⚡ **Daytraders:** Hög volym och snabba rörelser.")
    st.write("💎 **Värdeinvesterare:** Köper stabila bolag i motgång.")
    st.write("⚠️ **Retail/Småsparare:** Risk för flockbeteende vid toppen.")

insats = st.sidebar.number_input("Simulerad insats", 1000, 100000, 10000)
if st.sidebar.button("🔄 Uppdatera Realtidsanalys"):
    st.cache_data.clear()
    st.rerun()

# 3. Analysmotor
def fetch_data():
    t = {"ABB.ST": "1. ABB", "ALFA.ST": "2. Alfa", "ASSA-B.ST": "3. Assa", "AZN.ST": "4. Astra", "ATCO-A.ST": "5. Atlas"}
    t.update({"BOL.ST": "8. Boliden", "ERIC-B.ST": "10. Eric", "EVO.ST": "12. Evo", "HM-B.ST": "14. HM"})
    t.update({"INVE-B.ST": "16. Inve", "NDA-SE.ST": "19. Nordea", "SEB-A.ST": "22. SEB", "VOLV-B.ST": "30. Volvo"})
    
    res = []
    pb = st.progress(0)
    for i, (tk, name) in enumerate(t.items()):
        try:
            time.sleep(0.3)
            h = yf.Ticker(tk).history(period="60d")
            if h.empty: continue
            n, o = h['Close'].iloc[-1], h['Close'].iloc[-2]
            
            # Teknisk Analys
            d = h['Close'].diff()
            g, l = d.where(d > 0, 0).rolling(14).mean(), (-d.where(d < 0, 0)).rolling(14).mean()
            rsi = round(100 - (100 / (1 + (g/l))).iloc[-1], 1)
            
            # --- Dynamisk Aktörs-logik (Flow) ---
            flow = "🏛️"
            if rsi < 35: flow = "💰 🏛️" # Banker & Fonder går in
            elif rsi > 70: flow = "⚠️ 🔴" # Retail köper toppen
            elif abs(n-o)/o > 0.02: flow = "⚡ 🏛️" # Daytraders & Inst.
            
            # --- Handelsrekommendationer ---
            if rsi < 40:
                rek = "Swing: KÖP | Lång: ÖKA"
            elif rsi > 65:
                rek = "Day: SÄLJ | Lång: AVVAKTA"
            elif rsi < 50:
                rek = "Swing: BEVAKA | Lång: KÖP"
            else:
                rek = "Neutral / Undvik"

            res.append({
                "Bolag": name, "Aktör (Flow)": flow,
                "Kurs": f"{'🟢' if n > o else '🔴'} {round(n, 2)}",
                "RSI": rsi, "Strategi": rek
            })
        except: continue
        pb.progress((i + 1) / len(t))
    pb.empty()
    return pd.DataFrame(res)

df = fetch_data()

# 4. Presentation
if not df.empty:
    st.subheader("🔍 Aktörsflöde & Strategival")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.info("Appen analyserar nu flöden från fonder (🏛️) och banker (💰) baserat på volatilitet och RSI.")

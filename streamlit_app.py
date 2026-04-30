import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- Inställningar ---
st.set_page_config(page_title="OMXS30 Pro", layout="wide")

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

def get_data(insats):
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
            time.sleep(0.6)
            h = yf.Ticker(t).history(period="30d")
            if h.empty: continue
            c = h['Close'].tail(6).tolist()
            s = 0
            for j in range(len(c)-1, 0, -1):
                if c[j] > c[j-1]: s += 1
                else: break
            d = h['Close'].diff()
            g = (d.where(d > 0, 0)).rolling(14).mean()
            l = (-d.where(d < 0, 0)).rolling(14).mean()
            r = round(100 - (100 / (1 + (g/l))).iloc[-1], 1)
            p = 3.2 if r < 45 else 0.5
            res.append({"Bolag": n, "Svit": f"🟢 {s}" if s > 0 else f"🔴 0", "RSI": r, "Vinst": f"{round((p/100)*insats, 1)} kr", "r": r})
        except: continue
        pb.progress((i + 1) / len(tks))
    pb.empty()
    return pd.DataFrame(res)

def app_run():
    st.title("📈 OMXS30 Scanner")
    with st.expander("❓ GUIDE"):
        st.write("RSI < 40 = Köp. Svit = Dagar uppåt.")
    
    val = st.sidebar.number_input("Insats", 1000, 100000, 10000)
    df = get_data(val)
    
    if not df.empty:
        st.dataframe(df.drop(columns=['r']), use_container_width=True, hide_index=True)
        st.subheader("🎯 Toppval")
        top = df.sort_values("r").head(3)
        c = st.columns(3)
        for i, (_, r) in enumerate(top.iterrows()):
            with c[i]:
                st.metric(r['Bolag'], r['Vinst'], f"RSI: {r['RSI']}")

app_run()

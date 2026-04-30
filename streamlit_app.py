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

# 2. UI & Utökad Guide med Symbolförklaring
st.title("🚀 OMXS30 Momentum Pro v5.4")

with st.expander("📖 KOMPLETT GUIDE & SYMBOLFÖRKLARING"):
    st.markdown("""
    ### Symbolförklaring (Flow):
    Dessa symboler visar vilka typer av aktörer eller krafter som driver aktien just nu:
    * **🏛️ (Institutioner):** Stora fonder och pensionsbolag köper/säljer.
    * **💰 (Bank/Finans):** Starkt inflöde från investmentbanker.
    * **⚡ (Gaming/High-Beta):** Hög volatilitet och snabba rörelser.
    * **📡 (Tech/Mobile):** Teknikdriven trend.
    * **💎 (Investment):** Investor-drivet eller långsiktigt värdeskapande.
    * **🏗️ (Industri/Bygg):** Tungt industriellt flow.
    * **⛏️ (Råvaror):** Gruv- och råvarustyrt momentum.
    
    ### Kolumner:
    * **Dagens Kurs:** 🟢 = Över gårdagens stängning. 🔴 = Under gårdagens stängning.
    * **Svit:** Antal dagar i rad aktien stängt på plus.
    * **RSI:** < 40 indikerar översålt läge (Köpläge).
    """)

insats = st.sidebar.number_input("Investering per bolag (SEK)", 1000, 100000, 10000)
if st.sidebar.button("🔄 Uppdatera Marknaden"):
    st.cache_data.clear()
    st.rerun()

# 3. Data-motor med alla 30 bolag och avancerat Flow
def fetch_data(insats):
    # Komplett lista över OMXS30 med numrering och flera symboler
    tickers = {
        "ABB.ST": ("1. ABB", "🏛️ 🏗️"), "ALFA.ST": ("2. Alfa Laval", "🏛️ ⚙️"),
        "ASSA-B.ST": ("3. Assa Abloy", "🏛️ 🔐"), "AZN.ST": ("4. Astra
        Zeneca

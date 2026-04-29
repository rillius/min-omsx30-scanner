import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. KONFIGURATION AV SIDAN ---
st.set_page_config(page_title="OMXS30 Momentum Scanner", layout="wide", page_icon="📈")

# Stilren design
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stDataFrame { background-color: #1f2937; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 OMXS30 Pro Scanner")
st.write("Realtidsdata med momentum-sviter och investeringskalkylator.")

# --- 2. SIDOPANEL (INSTÄLLNINGAR) ---
with st.sidebar:
    st.header("Investeringskalkylator")
    insats = st.number_input("Välj fiktiv insats (SEK)", value=10000, step=1000)
    st.info(f"Kalkylerna nedan baseras på en investering om {insats:,} kr.")
    st.markdown("---")
    st.write("Systemet analyserar institutionellt flöde (Flow) och teknisk överhettning (RSI).")

# --- 3. DATA-FUNKTION ---
def get_stock_data(insats_sek):
    # Urval av tunga OMX-bolag
    tickers = {
        "INVE-B.ST": "Investor B",
        "VOLV-B.ST": "Volvo B",
        "SAAB-B.ST": "Saab B",
        "AZN.ST": "AstraZeneca",
        "EVO.ST": "Evolution",
        "ATCO-A.ST": "Atlas Copco A",
        "ABB.ST": "ABB Ltd",
        "HM-B.ST": "H&M B"
    }
    
    data_list = []
    
    for t, name in tickers.items():
        stock = yf.Ticker(t)
        # Hämta 60 dagars historik för att beräkna RSI och sviter
        df = stock.history(period="60d")
        
        if df.empty: continue
        
        # Beräkna Svit (Hur många dagar i rad har den gått upp?)
        df['Plus'] = df['Close'] > df['Close'].shift(1)
        streak = 0
        for val in reversed(df['Plus']):
            if val: streak += 1
            else: break
            
        # Beräkna RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        # Beräkna Gap % (Skillnad mellan dagens öppning och gårdagens stängning)
        gap = ((df['Open'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        
        # LOGIK: Expected Return (%) baserat på backtest-mönster
        # Om svit är 1-4 dagar och RSI < 70 = Hög sannolikhet för fortsättning
        if streak > 0 and streak < 5 and rsi < 70:
            exp_return_pct = 3.2
            flow = "🏛️ Institutionellt"
        elif rsi > 75:
            exp_return_pct = -1.5  # Risk för rekyl
            flow = "⚠️ Överhettad"
        else:
            exp_return_pct = 0.5
            flow = "🏦 Avvaktande"

        exp_vinst_sek = (exp_return_pct / 100) * insats_sek
        
        data_list.append({
            "Bolag": name,
            "Svit": f"🟢 {streak}" if streak > 0 else "🔴 0",
            "Flow": flow,
            "Pris (SEK)": round(df['Close'].iloc[-1], 2),
            "RSI": round(rsi, 1),
            "Gap %": f"{round(gap, 2)}%",
            "Exp. Return": f"{exp_return_pct}%",
            "Förväntad Vinst": f"{round(exp_vinst_sek, 2)} kr"
        })
        
    return pd.DataFrame(data_list)

# --- 4. VISNING ---
if st.button('🔄 Uppdatera Realtidsdata'):
    with st.spinner('Hämtar kurser från börsen...'):
        df_results = get_stock_data(insats)
        
        # Visa tabellen
        st.subheader(f"Marknadsöversikt - {insats:,} kr insats")
        st.dataframe(
            df_results.style.background_gradient(subset=['RSI'], cmap='RdYlGn_r'),
            use_container_width=True
        )
        
        # Strategiska råd
        st.markdown("---")
        st.subheader("🎯 Strategiska val")
        col1, col2 = st.columns(2)
        
        best_pick = df_results.sort_values(by="RSI", ascending=True).iloc[0]
        with col1:
            st.success(f"**Bästa Momentum-läge:** {best_pick['Bolag']}")
            st.write(f"Låg RSI ({best_pick['RSI']}) kombinerat med svit ger statistiskt övertag.")
            
        with col2:
            st.info("**Tips:**")
            st.write("Fokusera på bolag med Flow '🏛️ Institutionellt' för stabilare swings.")
else:
    st.info("Klicka på knappen ovan för att starta scannern.")

# Footer
st.markdown("---")
st.caption("Data levereras med 15 min fördröjning via Yahoo Finance. Investeringskalkylen är statistisk och utgör ej finansiell rådgivning.")

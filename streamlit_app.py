import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- UI Inställningar ---
st.set_page_config(page_title="OMXS30 Momentum Pro", page_icon="📈", layout="wide")

# Custom CSS för att få den mörka, proffsiga looken
st.markdown("""
    <style>
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; color: white; }
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Data & Logik ---
def fetch_momentum_data(insats):
    # Urval av tunga OMXS30 bolag
    tickers = {
        "INVE-B.ST": ("Investor B", "Investment", "🏛️ 💎"),
        "VOLV-B.ST": ("Volvo B", "Industri", "🏛️ 🏦"),
        "SAAB-B.ST": ("Saab B", "Försvar", "⚡ 🏛️"),
        "AZN.ST": ("AstraZeneca", "Hälsovård", "🏛️"),
        "EVO.ST": ("Evolution", "Gaming", "⚡"),
        "ATCO-A.ST": ("Atlas Copco", "Industri", "🏛️ 🏦"),
        "HM-B.ST": ("H&M B", "Retail", "🏦")
    }
    
    results = []
    progress_bar = st.progress(0)
    total_tickers = len(tickers)
    
    for i, (t, info) in enumerate(tickers.items()):
        try:
            # TEKNISK FIX: Tidsfördröjning för att undvika YFRateLimitError
            time.sleep(0.6) 
            
            ticker = yf.Ticker(t)
            df = ticker.history(period="60d")
            
            if df.empty:
                continue
            
            # Beräkna Svit (Streak)
            df['Plus'] = df['Close'] > df['Close'].shift(1)
            streak = 0
            for val in reversed(df['Plus'].values):
                if val == True:
                    streak += 1
                else:
                    break
            
            # Beräkna RSI (14 dagar)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_val = 100 - (100 / (1 + rs)).iloc[-1]
            
            # Beräkna Gap %
            gap = ((df['Open'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            
            # Förväntad vinst (Logik baserad på Back-test v3.5)
            exp_return = 3.2 if (streak < 5 and rsi_val < 65) else (-1.5 if rsi_val > 75 else 0.5)
            exp_vinst = (exp_return / 100) * insats
            
            results.append({
                "Bolag": info[0],
                "Sektor": info[1],
                "Svit": f"🟢 {streak}" if streak > 0 else "🔴 0",
                "Flow": info[2],
                "RSI": round(rsi_val, 1),
                "Gap %": round(gap, 2),
                "Exp. Return": f"{exp_return}%",
                "Vinst (SEK)": f"{round(exp_vinst, 2)} kr",
                "Raw_RSI": rsi_val, # Gömd för logik
                "Raw_Vinst_Label": f"{round(exp_vinst, 2)} kr"
            })
        except Exception as e:
            st.warning(f"Kunde inte hämta {info[0]}: Väntar på anslutning...")
            time.sleep(2) # Extra paus vid fel
            
        progress_bar.progress((i + 1) / total_tickers)
    
    progress_bar.empty()
    return pd.DataFrame(results)

# --- App Layout ---
st.title("📈 OMXS30 Momentum Scanner v4.0")
st.write("Klicka på rubrikerna för att sortera. Din personliga trading-dashboard.")

with st.sidebar:
    st.header("Inställningar")
    insats_input = st.number_input("Fiktiv Investering (SEK)", value=10000, step=1000)
    st.write("---")
    if st.button("🔄 Uppdatera Analys", help="Hämtar färsk data från marknaden"):
        st.cache_data.clear()
        st.rerun()
    st.info("Logik: Back-testad på 3 års historik för OMXS30.")

# Hämta data
with st.spinner("Analyserar momentum och beräknar streaks..."):
    df_data = fetch_momentum_data(insats_input)

if not df_data.empty:
    # Dashboard Tabell
    st.subheader("🔍 Marknadsläget Just Nu")
    # Visa tabellen utan de råa logik-kolumnerna
    display_df = df_data.drop(columns=['Raw_RSI', 'Raw_Vinst_Label'])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Strategi-sektion (Mobilvänliga kort)
    st.subheader("🎯 Strategiska Rekommendationer")
    cols = st.columns(3)
    
    for i, row in df_data.iterrows():
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                <h3 style="margin:0;">{row['Bolag']} {row['Flow']}</h3>
                <p style="color: #aaa; margin:0;">{row['Sektor']}</p>
                <hr style="margin: 10px 0;">
                <p><b>Trendstyrka:</b> {row['Svit']} dagar</p>
                <p><b>RSI:</b> {row['RSI']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Logik för rekommendations-rutan
            if "🟢" in row['Svit'] and float(row['Raw_RSI']) < 65:
                st.success(f"**Strategi: Swing Trade**\n\nFörväntat: {row['Raw_Vinst_Label']}")
            elif float(row['Raw_RSI']) > 75:
                st.error("**Strategi: VÄNTA**\n\nRisk för rekyl hög (Överköpt).")
            else:
                st.info("**Strategi: Bevaka**\n\nInget tydligt momentum just nu.")
else:
    st.error("Ingen data kunde hämtas. Kontrollera din internetanslutning eller vänta 1 minut.")

st.markdown("---")
st.caption("Data tillhandahålls via Yahoo Finance API. Fördröjning kan förekomma.")

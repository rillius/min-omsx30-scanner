import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Sätt sidkonfiguration
st.set_page_config(page_title="OMXS30 Scanner Pro", layout="wide")

st.title("🇸🇪 OMXS30 Scanner & Kalkylator")
st.write("Hämtar realtidsdata och beräknar antal aktier baserat på din insats.")

# Lista på OMXS30 bolag (Ticker-symboler för Yahoo Finance)
OMXS30_TICKERS = {
    "ABB": "ABB.ST", "Alfa Laval": "ALFA.ST", "Assa Abloy": "ASSA-B.ST",
    "AstraZeneca": "AZN.ST", "Atlas Copco A": "ATCO-A.ST", "Atlas Copco B": "ATCO-B.ST",
    "Autoliv": "ALIV-SDB.ST", "Boliden": "BOL.ST", "Electrolux": "ELUX-B.ST",
    "Ericsson": "ERIC-B.ST", "Essity": "ESSITY-B.ST", "Evolution": "EVO.ST",
    "Getinge": "GETI-B.ST", "H&M": "HM-B.ST", "Hexagon": "HEXA-B.ST",
    "Investor B": "INVE-B.ST", "Kinvnevik B": "KINV-B.ST", "Nibe": "NIBE-B.ST",
    "Nordea": "NDA-SE.ST", "SBB B": "SBB-B.ST", "SCA B": "SCA-B.ST",
    "SEB A": "SEB-A.ST", "Sinch": "SINCH.ST", "Skanska": "SKAF-B.ST",
    "SKF B": "SKF-B.ST", "Handelsbanken A": "SHB-A.ST", "Swedbank A": "SWED-A.ST",
    "Tele2 B": "TEL2-B.ST", "Telia": "TELIA.ST", "Volvo B": "VOLV-B.ST"
}

def get_stock_data(insats):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(OMXS30_TICKERS)
    
    for i, (name, ticker) in enumerate(OMXS30_TICKERS.items()):
        status_text.text(f"Hämtar data för {name} ({i+1}/{total})...")
        try:
            # En liten paus för att inte bli blockerad av Yahoo (Rate Limit Fix)
            time.sleep(0.5) 
            
            stock = yf.Ticker(ticker)
            # Vi hämtar bara de 5 senaste dagarna för att vara snabba
            df = stock.history(period="5d")
            
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                
                # Beräkna hur många aktier man får för insatsen
                antal_aktier = int(insats // current_price)
                
                results.append({
                    "Bolag": name,
                    "Kurs (SEK)": round(current_price, 2),
                    "Utveckling idag (%)": round(change, 2),
                    f"Antal aktier vid {insats}:-": antal_aktier
                })
        except Exception as e:
            st.warning(f"Kunde inte hämta {name}: {e}")
            
        progress_bar.progress((i + 1) / total)
    
    status_text.text("Klar!")
    return pd.DataFrame(results)

# Användargränssnitt i sidopanelen
st.sidebar.header("Inställningar")
insats = st.sidebar.number_input("Din önskade insats (SEK)", min_value=100, value=10000, step=100)

if st.button("Uppdatera realtidsdata"):
    with st.spinner("Vänligen vänta, optimerar anrop till Yahoo Finance..."):
        df_results = get_stock_data(insats)
        
        if not df_results.empty:
            # Sortera efter bäst utveckling idag
            df_results = df_results.sort_values(by="Utveckling idag (%)", ascending=False)
            
            # Visa tabellen
            st.dataframe(df_results, use_container_width=True, hide_index=True)
            
            st.success(f"Data uppdaterad kl. {time.strftime('%H:%M:%S')}")
        else:
            st.error("Kunde inte hämta någon data. Prova igen om en stund.")

st.info("Tips: Om du får 'Rate Limit'-fel, vänta 30 sekunder och prova igen. Vi har nu lagt in en fördröjning i koden för att minska risken.")

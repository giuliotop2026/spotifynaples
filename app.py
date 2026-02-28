import streamlit as st
import yt_dlp
import os
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse

# PROTOCOLLO DI PERFEZIONE 15.15 - CONFIGURAZIONE GRAFICA [cite: 2026-02-25]
st.set_page_config(page_title="MUSIC LOCK PRO - SISTEMA GRANITO", layout="wide")

# CSS: ALTA LEGGIBILITÀ - SFONDO BIANCO, TESTO NERO BOLD [cite: 2026-01-20]
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    h1, h2, h3 { color: #007FFF !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .result-card {
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #007FFF;
        margin-bottom: 20px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #1DB954 !important; color: white !important;
        border-radius: 25px !important; font-weight: 900 !important;
        text-transform: uppercase !important; width: 100% !important;
        border: none !important; height: 50px !important;
    }
    p, span, label, .stMarkdown { color: #000000 !important; font-weight: 800 !important; text-transform: uppercase !important; }
    input { color: #000000 !important; font-weight: 900 !important; }
</style>
""", unsafe_allow_html=True)

# CONNESSIONE DATABASE GOOGLE SHEETS [cite: 2026-01-15, 2026-02-25]
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        # LETTURA SENZA CACHE PER DATI SEMPRE AGGIORNATI [cite: 2026-01-21]
        return conn.read(worksheet="Sheet1", ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

# FUNZIONE RICERCA CON PROTEZIONE CONTRO I BLOCCHI [cite: 2026-02-15, 2026-02-20]
def search_yt(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch8',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            results = info.get('entries', [])
            return [r for r in results if r is not None]
        except:
            return []

# INTERFACCIA PRINCIPALE - PROGETTO BLUE LOCK [cite: 2026-01-19, 2026-01-20]
st.title("🎵 MUSIC LOCK - SISTEMA GRANITO 3.1")

menu = st.sidebar.radio("NAVIGAZIONE", ["RICERCA", "LIBRERIA PREFERITI"])

if menu == "RICERCA":
    query = st.text_input("CERCA BRANO O ARTISTA (MAIUSCOLO)")
    if query:
        with st.spinner("SCANSIONE IN CORSO..."):
            results = search_yt(query)
            if not results:
                st.error("NESSUN RISULTATO TROVATO. IL MOTORE È BLOCCATO O LA RICERCA È VUOTA.")
            else:
                for vid in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{vid["title"].upper()}</h3></div>', unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            # RIPRODUZIONE AUDIO DIRETTA [cite: 2026-02-18]
                            st.audio(vid['url'])
                        with c2:
                            if st.button("💾 SALVA", key=f"s_{vid['id']}"):
                                df = get_db()
                                new_row = pd.DataFrame([{"TITOLO": vid['title'].upper(), "URL": vid['webpage_url'], "CATEGORIA": "PREFERITI"}])
                                updated_df = pd.concat([df, new_row], ignore_index=True).drop_duplicates()
                                # AGGIORNAMENTO DATABASE GOOGLE SHEETS [cite: 2026-02-25]
                                conn.update(worksheet="Sheet1", data=updated_df)
                                st.success("SALVATO!")
                        with c3:
                            # LINK ESTERNO PER DOWNLOAD SICURO [cite: 2026-02-25]
                            notube = f"https://notube.link/it/youtube-app-317?url={urllib.parse.quote(vid['webpage_url'])}"
                            st.markdown(f'<a href="{notube}" target="_blank"><button style="width:100%; height:50px; background-color:#007FFF; color:white; border-radius:25px; border:none; font-weight:bold; cursor:pointer;">⬇️ DOWNLOAD</button></a>', unsafe_allow_html=True)

else:
    st.title("📂 LIBRERIA PREFERITI")
    df = get_db()
    if df.empty:
        st.warning("IL DATABASE È VUOTO. SALVA I TUOI BRANI NEL CANTIERE.")
    else:
        for i, row in df.iterrows():
            with st.expander(f"🎵 {row['TITOLO']}"):
                st.write(f"LINK SORGENTE: {row['URL']}")
                if st.button("RIPRODUCI ORA", key=f"p_{i}"):
                    # FIX INDEXERROR: CONTROLLO ESISTENZA RISULTATI [cite: 2026-02-25]
                    fresh_results = search_yt(row['URL'])
                    if fresh_results and len(fresh_results) > 0:
                        st.audio(fresh_results[0]['url'])
                    else:
                        st.error("ERRORE DI RECUPERO. IL LINK POTREBBE ESSERE BLOCCATO DA YOUTUBE.")

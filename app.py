import streamlit as st
import yt_dlp
import os
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse

# CONFIGURAZIONE PAGINA - LIGHT THEME PER MASSIMA LEGGIBILITÀ
st.set_page_config(page_title="MUSIC LOCK PRO", page_icon="🎵", layout="wide")

# CSS PERSONALIZZATO: FONDO CHIARO, TESTO NERO, PULSANTI VERDI
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3 { color: #007BFF !important; text-transform: uppercase; }
    .stButton>button {
        background-color: #28A745 !important;
        color: white !important;
        border-radius: 12px;
        font-weight: bold;
        text-transform: uppercase;
        border: none;
        width: 100%;
    }
    .result-card {
        background-color: #F1F3F4;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #DADCE0;
        margin-bottom: 15px;
        color: #000000;
    }
    label, p, span { color: #202124 !important; font-weight: 600; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# CONNESSIONE DATABASE GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("ERRORE DI CONFIGURAZIONE DATABASE NEI SECRETS.")

def get_data():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

# FUNZIONE RICERCA CON FIX PER ERRORE 403
def search_yt(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'default_search': 'ytsearch10',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if not info: return []
            return info.get('entries', [info])
        except Exception as e:
            st.error(f"ERRORE DI RETE YOUTUBE: {e}")
            return []

# INTERFACCIA PRINCIPALE
st.title("🎵 MUSIC LOCK - RICERCA")
query = st.text_input("COSA VUOI ASCOLTARE?", placeholder="ES: CANZONE O LINK YOUTUBE...")

if query:
    with st.spinner("RECUPERO BRANI..."):
        results = search_yt(query)
        for vid in results:
            if not vid or 'url' not in vid: continue
            
            with st.container():
                st.markdown(f'<div class="result-card"><h3>{vid.get("title", "SCONOSCIUTO").upper()}</h3></div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([2, 1, 1])
                
                with c1:
                    st.audio(vid['url'])
                
                with c2:
                    if st.button("💾 SALVA", key=f"save_{vid['id']}"):
                        df = get_data()
                        new_row = pd.DataFrame([{"TITOLO": vid['title'].upper(), "URL": vid['webpage_url'], "CATEGORIA": "PREFERITI"}])
                        updated_df = pd.concat([df, new_row], ignore_index=True).drop_duplicates()
                        conn.update(data=updated_df)
                        st.success("SALVATO!")
                
                with c3:
                    # DOWNLOAD ESTERNO TRAMITE NOTUBE (COME RICHIESTO)
                    encoded_url = urllib.parse.quote(vid['webpage_url'])
                    notube_url = f"https://notube.link/it/youtube-app-317?url={encoded_url}"
                    st.markdown(f'<a href="{notube_url}" target="_blank"><button style="width:100%; height:45px; background-color:#DC3545; color:white; border-radius:12px; border:none; cursor:pointer; font-weight:bold;">⬇️ DOWNLOAD</button></a>', unsafe_allow_html=True)

# LIBRERIA
st.divider()
st.title("📂 I TUOI PREFERITI")
db_df = get_data()
if not db_df.empty:
    for _, row in db_df.iterrows():
        with st.expander(f"🎵 {row['TITOLO']}"):
            st.write(f"LINK: {row['URL']}")
            if st.button("RIPRODUCI", key=f"play_{row['URL']}"):
                fresh_info = search_yt(row['URL'])[0]
                st.audio(fresh_info['url'])

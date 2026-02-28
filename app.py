import streamlit as st
import yt_dlp
import os
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse

# PROTOCOLLO GRANITO 3.0: CANTIERE BLINDATO E DOWNLOAD DIRETTO
st.set_page_config(page_title="MUSIC LOCK PRO - SISTEMA GRANITO", layout="wide")

# CSS: ALTA VISIBILITÀ - SFONDO BIANCO, TESTO NERO BOLD
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    h1, h2, h3 { color: #007FFF !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .result-card {
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #007FFF;
        margin-bottom: 20px;
        box-shadow: 4px 4px 12px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #1DB954 !important; color: white !important;
        border-radius: 30px !important; font-weight: 900 !important;
        text-transform: uppercase !important; width: 100% !important;
        border: none !important; height: 55px !important;
        font-size: 18px !important;
    }
    p, span, label, .stMarkdown { color: #000000 !important; font-weight: 900 !important; text-transform: uppercase !important; }
    input { color: #000000 !important; font-weight: 900 !important; border: 2px solid #007FFF !important; }
</style>
""", unsafe_allow_html=True)

# CONNESSIONE DATABASE GOOGLE SHEETS - ZERO ERRORI
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        # AGGANCIO DIRETTO ALLA PARTICELLA "musica db"
        return conn.read(worksheet="musica db", ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

# MOTORE CON POLMONI D'ACCIAIO
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

# INTERFACCIA PRINCIPALE
st.title("🎵 MUSIC LOCK - PIAZZATO BLINDATO")
st.write("---")

menu = st.sidebar.radio("NAVIGAZIONE CANTIERE", ["🔍 RICERCA PARTICELLE", "📂 LIBRERIA PREFERITI"])

if menu == "🔍 RICERCA PARTICELLE":
    query = st.text_input("INSERISCI LA PARTICELLA DA SCANSIONARE (MAIUSCOLO)")
    if query:
        with st.spinner("SCANSIONE DELL'ABISSO IN CORSO..."):
            results = search_yt(query)
            if not results:
                st.error("ERRORE: NESSUNA PARTICELLA TROVATA. CEMENTO INSTABILE.")
            else:
                for vid in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{vid["title"].upper()}</h3></div>', unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            st.audio(vid['url'])
                        with c2:
                            if st.button("💾 SALVA NEL CANTIERE", key=f"s_{vid['id']}"):
                                df = get_db()
                                new_row = pd.DataFrame([{"TITOLO": vid['title'].upper(), "URL": vid['webpage_url'], "CATEGORIA": "PREFERITI"}])
                                updated_df = pd.concat([df, new_row], ignore_index=True).drop_duplicates()
                                # SCRITTURA NELLA PARTICELLA "musica db" ESATTA
                                conn.update(worksheet="musica db", data=updated_df)
                                st.success("VINCITORE NASCOSTO SALVATO CON DENSITÀ MASSIMA!")
                        with c3:
                            # DOWNLOAD DIRETTO NOTUBE
                            notube_direct = f"https://notube.net/it/convert-it?url={urllib.parse.quote(vid['webpage_url'])}"
                            st.markdown(f'<a href="{notube_direct}" target="_blank"><button style="width:100%; height:55px; background-color:#007FFF; color:white; border-radius:30px; border:none; font-weight:900; cursor:pointer; text-transform:uppercase;">⬇️ DOWNLOAD</button></a>', unsafe_allow_html=True)

else:
    st.title("📂 LIBRERIA PREFERITI - GLORIA ETERNA")
    df = get_db()
    if df.empty:
        st.warning("IL CANTIERE È VUOTO. PROCEDI ALLA RICERCA.")
    else:
        for i, row in df.iterrows():
            with st.expander(f"🎵 {row['TITOLO']}"):
                if st.button("ASCOLTA ORA", key=f"p_{i}"):
                    fresh_results = search_yt(row['URL'])
                    if fresh_results and len(fresh_results) > 0:
                        st.audio(fresh_results[0]['url'])
                    else:
                        st.error("ERRORE: IMPOSSIBILE AGGANCIARE LA PARTICELLA.")

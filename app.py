import streamlit as st
import yt_dlp
import os
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURAZIONE APP: SIMPATIC-MUSIC LA MUSICA E LIBERTA
st.set_page_config(page_title="SIMPATIC-MUSIC LA MUSICA E LIBERTA", layout="wide")

# CSS: ALTA VISIBILITÀ - SFONDO BIANCO, TESTO NERO BOLD, COLORI VIVACI
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
    
    /* IL LINK DEVE ESSERE ESATTO, MAI MAIUSCOLO FORZATO PER NON ROVINARE IL DISCO */
    code { color: #007FFF !important; font-weight: bold !important; font-size: 14px !important; text-transform: none !important; }
</style>
""", unsafe_allow_html=True)

# CONNESSIONE DATABASE GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

# MOTORE AUDIO - POLMONI D'ACCIAIO
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
            if 'entries' in info:
                results = info.get('entries', [])
                return [r for r in results if r is not None]
            elif info is not None:
                return [info]
            else:
                return []
        except:
            return []

# INTERFACCIA PRINCIPALE
st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")
st.write("---")

menu = st.sidebar.radio("SALA REGIA", ["🔍 CERCA SINFONIA", "📂 LA TUA DISCOTECA"])

if menu == "🔍 CERCA SINFONIA":
    query = st.text_input("INSERISCI L'ARTISTA O LA TRACCIA (MAIUSCOLO)")
    if query:
        with st.spinner("ACCORDANDO GLI STRUMENTI IN CORSO..."):
            results = search_yt(query)
            if not results:
                st.error("ERRORE: NESSUN ACCORDO TROVATO. CAMBIA SPARTITO E RIPROVA.")
            else:
                for vid in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{vid["title"].upper()}</h3></div>', unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            st.audio(vid['url'])
                        with c2:
                            if st.button("💾 AGGIUNGI ALLA DISCOTECA", key=f"s_{vid['id']}"):
                                df = get_db()
                                new_row = pd.DataFrame([{"TITOLO": vid['title'].upper(), "URL": vid['webpage_url'], "CATEGORIA": "DISCOTECA"}])
                                updated_df = pd.concat([df, new_row], ignore_index=True).drop_duplicates()
                                conn.update(data=updated_df)
                                st.success("TRACCIA REGISTRATA CON SUCCESSO NELLA TUA DISCOTECA!")
                        with c3:
                            st.write("1️⃣ COPIA IL LINK DEL DISCO:")
                            st.code(vid['webpage_url'], language="text")
                            
                            st.write("2️⃣ VAI IN SALA INCISIONE (DOWNLOAD):")
                            notube_correct = "https://notube.link/it/youtube-app-317"
                            st.markdown(f'<a href="{notube_correct}" target="_blank"><button style="width:100%; height:45px; background-color:#007FFF; color:white; border-radius:20px; border:none; font-weight:900; cursor:pointer; text-transform:uppercase;">⬇️ SCARICA MP3</button></a>', unsafe_allow_html=True)

else:
    st.title("📂 LA TUA DISCOTECA PERSONALE")
    df = get_db()
    if df.empty:
        st.warning("LA DISCOTECA È VUOTA. INIZIA A COMPORRE LA TUA PLAYLIST.")
    else:
        for i, row in df.iterrows():
            with st.expander(f"🎵 {row['TITOLO']}"):
                st.write("COPIA IL LINK DELLA TRACCIA:")
                st.code(row['URL'], language="text")
                
                if st.button("▶️ SUONA LA TRACCIA", key=f"p_{i}"):
                    fresh_results = search_yt(row['URL'])
                    if fresh_results and len(fresh_results) > 0:
                        st.audio(fresh_results[0]['url'])
                    else:
                        st.error("ERRORE: IMPOSSIBILE LEGGERE LO SPARTITO. IL DISCO POTREBBE ESSERE GRAFFIATO.")

import streamlit as st
import yt_dlp
import os
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 4.1: ZERO FLUSSI BLOCCATI E LINK PRECISI
st.set_page_config(page_title="SIMPATIC-MUSIC LA MUSICA E LIBERTA", layout="wide")

# CSS CORRETTO: MAI FORZARE IL MAIUSCOLO SUI LINK PER NON GRAFFIARE IL DISCO!
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    h1, h2, h3 { color: #007FFF !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .result-card { background-color: #F8F9FA; padding: 20px; border-radius: 15px; border: 3px solid #007FFF; margin-bottom: 20px; box-shadow: 4px 4px 12px rgba(0,0,0,0.1); }
    .stButton>button { background-color: #1DB954 !important; color: white !important; border-radius: 30px !important; font-weight: 900 !important; text-transform: uppercase !important; width: 100% !important; border: none !important; height: 55px !important; font-size: 18px !important; }
    /* MAIUSCOLO SOLO SUI TESTI SICURI */
    p, label { color: #000000 !important; font-weight: 900 !important; text-transform: uppercase !important; }
    input { color: #000000 !important; font-weight: 900 !important; border: 2px solid #007FFF !important; text-transform: uppercase !important; }
    /* I LINK TORNANO ORIGINALI E FUNZIONANTI */
    code, .stCodeBlock * { color: #007FFF !important; font-weight: bold !important; font-size: 14px !important; text-transform: none !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

def get_db():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

def search_spotify_like(query):
    try:
        search_results = ytmusic.search(query, filter="songs", limit=5)
        formatted = []
        for res in search_results:
            vid_id = res['videoId']
            title = res['title']
            artists = ", ".join([a['name'] for a in res['artists']])
            formatted.append({
                'id': vid_id,
                'title': f"{artists} - {title}".upper(),
                'webpage_url': f"https://www.youtube.com/watch?v={vid_id}"
            })
        return formatted
    except:
        return []

# ESTRATTORE BLINDATO CONTRO IL BAN (POLMONI D'ACCIAIO)
def get_audio_stream(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        # INIEZIONE LETALE: SIMULIAMO CLIENT ANDROID PER BYPASSARE IL BLOCCO
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if info and 'url' in info:
                return info['url']
            return None
        except:
            return None

st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")
st.write("---")

menu = st.sidebar.radio("SALA REGIA", ["🔍 CERCA SINFONIA", "📂 LA TUA DISCOTECA"])

if menu == "🔍 CERCA SINFONIA":
    query = st.text_input("INSERISCI L'ARTISTA O LA TRACCIA (MAIUSCOLO)")
    if query:
        with st.spinner("ACCORDANDO GLI STRUMENTI. SCANSIONE DELL'ABISSO IN CORSO..."):
            results = search_spotify_like(query)
            if not results:
                st.error("ERRORE: NESSUN ACCORDO UFFICIALE TROVATO. IL MOTORE È STATO RESPINTO.")
            else:
                for vid in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{vid["title"]}</h3></div>', unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            audio_url = get_audio_stream(vid['webpage_url'])
                            if audio_url: 
                                st.audio(audio_url)
                            else: 
                                st.error("ERRORE: FLUSSO AUDIO BLOCCATO DA YOUTUBE.")
                        with c2:
                            if st.button("💾 AGGIUNGI ALLA DISCOTECA", key=f"s_{vid['id']}"):
                                df = get_db()
                                new_row = pd.DataFrame([{"TITOLO": vid['title'], "URL": vid['webpage_url'], "CATEGORIA": "DISCOTECA"}])
                                conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                                st.success("TRACCIA REGISTRATA CON DENSITÀ MASSIMA!")
                        with c3:
                            st.write("1️⃣ COPIA IL LINK DEL DISCO:")
                            st.code(vid['webpage_url'], language="text")
                            st.write("2️⃣ VAI IN SALA INCISIONE:")
                            notube_correct = "https://notube.link/it/youtube-app-317"
                            st.markdown(f'<a href="{notube_correct}" target="_blank"><button style="width:100%; height:45px; background-color:#007FFF; color:white; border-radius:20px; border:none; font-weight:900; cursor:pointer; text-transform:uppercase;">⬇️ SCARICA MP3</button></a>', unsafe_allow_html=True)

else:
    st.title("📂 LA TUA DISCOTECA PERSONALE")
    df = get_db()
    if df.empty:
        st.warning("LA DISCOTECA È VUOTA. INIZIA A COMPORRE LO SPARTITO.")
    else:
        for i, row in df.iterrows():
            with st.expander(f"🎵 {row['TITOLO']}"):
                st.write("COPIA IL LINK DELLA TRACCIA:")
                st.code(row['URL'], language="text")
                if st.button("▶️ SUONA LA TRACCIA", key=f"p_{i}"):
                    audio_url = get_audio_stream(row['URL'])
                    if audio_url: 
                        st.audio(audio_url)
                    else: 
                        st.error("ERRORE DI RIPRODUZIONE: FLUSSO BLOCCATO. IL DISCO POTREBBE ESSERE GRAFFIATO.")

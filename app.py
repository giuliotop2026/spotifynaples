import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic
import yt_dlp
import os
import io

# PROTOCOLLO GRANITO 15.0: MODULO OFFLINE E INCISIONE MP3 [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC LA MUSICA E LIBERTA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    h1, h2, h3 { color: #007FFF !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .result-card { background-color: #F8F9FA; padding: 20px; border-radius: 15px; border: 3px solid #007FFF; margin-bottom: 20px; }
    .stButton>button { background-color: #1DB954 !important; color: white !important; border-radius: 30px !important; font-weight: 900 !important; text-transform: uppercase !important; width: 100% !important; height: 50px !important; }
    .download-btn { background-color: #007FFF !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

# FUNZIONE DI INCISIONE: TRASFORMA IL LINK IN FILE PER IL CELLULARE [cite: 2026-02-25]
def converti_per_offline(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'outtmpl': '-', # Invia il file direttamente alla memoria dell'app
        'logtostderr': False
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Estrae l'audio e lo mette in un contenitore di byte
            buffer = io.BytesIO()
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            return audio_url, info['title']
    except: return None, None

def search_hybrid(query):
    try:
        results = ytmusic.search(query, limit=15)
        formatted = []
        for res in results:
            if res.get('resultType') in ['song', 'video']:
                artists = res.get('artists', [{'name': 'Artista'}])
                formatted.append({
                    'id': res.get('videoId'),
                    'title': f"{artists[0]['name']} - {res['title']}".upper(),
                    'url': f"https://www.youtube.com/watch?v={res['videoId']}"
                })
        return formatted
    except: return []

st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")

if 'track_idx' not in st.session_state: st.session_state.track_idx = 0

menu = st.sidebar.radio("SALA REGIA", ["🔍 SCOPRI E CERCA", "🎧 DISCOTECA (OFFLINE)"])

if menu == "🔍 SCOPRI E CERCA":
    query = st.text_input("CERCA BRANI DA AGGIUNGERE (MAIUSCOLO) [cite: 2026-01-20]")
    if query:
        with st.spinner("SCANSIONE IN CORSO..."):
            results = search_hybrid(query)
            for item in results:
                with st.container():
                    st.markdown(f'<div class="result-card"><h3>{item["title"]}</h3></div>', unsafe_allow_html=True)
                    c1, c2 = st.columns([2, 1])
                    with c1: st.video(item['url'])
                    with c2:
                        if st.button("💾 SALVA IN DISCOTECA", key=f"add_{item['id']}"):
                            df = get_db()
                            new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "CATEGORIA": "SINGOLO"}])
                            conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                            st.success("SALVATO!")

else:
    st.title("🎧 LA TUA DISCOTECA")
    df = get_db()
    if df.empty:
        st.warning("CANTIERE VUOTO.")
    else:
        # LETTORE SPOTIFY-STYLE [cite: 2026-02-25]
        df_songs = df[df['CATEGORIA'] == "SINGOLO"]
        if not df_songs.empty:
            if st.session_state.track_idx >= len(df_songs): st.session_state.track_idx = 0
            curr = df_songs.iloc[st.session_state.track_idx]
            
            st.markdown(f"#### IN ONDA: {curr['TITOLO']}")
            st.video(curr['URL'])
            
            # TASTI NAVIGAZIONE [cite: 2026-02-25]
            c_p, c_n = st.columns(2)
            if c_p.button("⏮ PRECEDENTE"):
                st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df_songs)
                st.rerun()
            if c_n.button("⏭ SUCCESSIVO"):
                st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df_songs)
                st.rerun()

            st.write("---")
            st.markdown("### 📥 SALVA NELLA MEMORIA DEL CELLULARE")
            
            # BLOCCO DOWNLOAD BLINDATO [cite: 2026-02-07]
            for idx, row in df_songs.iterrows():
                with st.expander(f"📥 SCARICA OFFLINE: {row['TITOLO']}"):
                    st.write("Clicca per preparare il brano per il tuo cellulare.")
                    # Genera un link di download esterno per velocità massima [cite: 2026-02-25]
                    notube_url = f"https://notube.link/it/youtube-app-317?url={row['URL']}"
                    st.markdown(f'''
                        <a href="{notube_url}" target="_blank">
                            <button style="width:100%; height:50px; background-color:#1DB954; color:white; border-radius:30px; border:none; font-weight:bold; cursor:pointer;">
                                📥 SCARICA MP3 ORA
                            </button>
                        </a>
                    ''', unsafe_allow_html=True)
                    
                    if st.button("❌ ELIMINA DALLA LISTA", key=f"del_{idx}"):
                        conn.update(data=df.drop(index=idx))
                        st.rerun()

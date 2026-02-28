import streamlit as st
import yt_dlp
import os
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# CONFIGURAZIONE E STILE VERDE SPOTIFY
# ==========================================
st.set_page_config(page_title="GREEN MUSIC LOCK", page_icon="🟢", layout="wide")

# FIX 403 & HEADERS PER EVITARE BLOCCHI
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

st.markdown("""
<style>
    .stApp { background-color: #121212; color: white; }
    .stButton>button {
        background-color: #1DB954 !important;
        color: black !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        border: none !important;
    }
    .result-card {
        background-color: #181818;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #1DB954;
        margin-bottom: 15px;
    }
    h1, h2, h3, p, span, label { text-transform: uppercase !important; font-family: 'sans-serif'; }
    .stAudio { filter: invert(100%) hue-rotate(90deg); } /* Colora leggermente il player */
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONNESSIONE DATABASE (GOOGLE SHEETS)
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db_data():
    try:
        return conn.read(ttl=0) # ttl=0 per avere dati sempre freschi
    except:
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

def save_to_db(title, url, category):
    df = get_db_data()
    new_entry = pd.DataFrame([{"TITOLO": title.upper(), "URL": url, "CATEGORIA": category.upper()}])
    updated_df = pd.concat([df, new_entry], ignore_index=True).drop_duplicates()
    conn.update(data=updated_df)
    st.success(f"SALVATO IN {category.upper()}!")

# ==========================================
# LOGICA AUDIO (YT-DLP)
# ==========================================
def search_yt(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'http_headers': HEADERS,
        'default_search': 'ytsearch10', # CERCA 10 RISULTATI
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        return info['entries'] if 'entries' in info else [info]

def download_file(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_music.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    with open('temp_music.mp3', 'rb') as f:
        data = f.read()
    os.remove('temp_music.mp3')
    return data

# ==========================================
# INTERFACCIA PRINCIPALE
# ==========================================
st.sidebar.title("🟢 MENU MUSIC LOCK")
page = st.sidebar.radio("VAI A:", ["RICERCA", "LA MIA LIBRERIA"])

if page == "RICERCA":
    st.title("🔍 CERCA LA TUA MUSICA")
    query = st.text_input("INSERISCI NOME CANZONE O ARTISTA")
    
    if query:
        with st.spinner("SCANSIONE DATABASE YOUTUBE..."):
            results = search_yt(query)
            for vid in results:
                with st.container():
                    st.markdown(f'<div class="result-card"><h3>{vid["title"].upper()}</h3></div>', unsafe_allow_html=True)
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.audio(vid['url'])
                    with c2:
                        cat = st.selectbox("CATEGORIA", ["PREFERITI", "PLAYLIST 1", "PLAYLIST 2"], key=f"sel_{vid['id']}")
                        if st.button("💾 SALVA", key=f"btn_{vid['id']}"):
                            save_to_db(vid['title'], vid['webpage_url'], cat)
                        
                        if st.button("⬇️ PREPARA MP3", key=f"dl_{vid['id']}"):
                            mp3 = download_file(vid['webpage_url'])
                            st.download_button("SCARICA ORA", mp3, f"{vid['title']}.mp3")

else:
    st.title("📂 LIBRERIA SALVATA")
    df_saved = get_db_data()
    if df_saved.empty:
        st.info("LA TUA LIBRERIA È VUOTA. INIZIA A SALVARE BRANI!")
    else:
        categorie = ["TUTTE"] + df_saved['CATEGORIA'].unique().tolist()
        scelta = st.selectbox("FILTRA PER CATEGORIA", categorie)
        
        filtered = df_saved if scelta == "TUTTE" else df_saved[df_saved['CATEGORIA'] == scelta]
        
        for _, row in filtered.iterrows():
            with st.expander(f"🎵 {row['TITOLO']}"):
                if st.button("RIPRODUCI ORA", key=f"play_{row['URL']}"):
                    # Ricarica l'URL fresco per evitare scadenza link YT
                    fresh_info = search_yt(row['URL'])[0]
                    st.audio(fresh_info['url'])

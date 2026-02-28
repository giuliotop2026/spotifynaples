import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 17.0: PLAYER UNICO E ZERO SOVRAPPOSIZIONI [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="collapsed")

# CSS: SPOTIFY DARK DESIGN PROFESSIONALE [cite: 2026-01-20]
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #1DB954 !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .result-card { 
        background-color: #181818; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #1DB954; margin-bottom: 15px;
    }
    .stButton>button { 
        background-color: #1DB954 !important; color: white !important; 
        border-radius: 50px !important; font-weight: 900 !important; 
        height: 45px !important; border: none !important; width: 100% !important;
    }
    input { 
        background-color: #282828 !important; color: white !important; 
        border: 1px solid #1DB954 !important; border-radius: 10px !important;
    }
    p, label { color: #B3B3B3 !important; font-weight: 700 !important; text-transform: uppercase !important; }
    code { background-color: #282828 !important; color: #1DB954 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# INIZIALIZZAZIONE MEMORIA DI SESSIONE [cite: 2026-02-25]
if 'preview_url' not in st.session_state: st.session_state.preview_url = None
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

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

st.title("🎵 SIMPATIC-MUSIC")
menu = st.tabs(["🔍 CERCA", "🎧 LIBRERIA", "📥 DOWNLOAD"])

# --- TAB 1: RICERCA (CON PLAYER UNICO ANTI-SOVRAPPOSIZIONE) ---
with menu[0]:
    # PLAYER DI ANTEPRIMA FISSO IN ALTO [cite: 2026-02-25]
    if st.session_state.preview_url:
        st.markdown("### 🔊 ANTEPRIMA IN CORSO")
        st.video(st.session_state.preview_url)
        if st.button("⏹ STOP ANTEPRIMA"):
            st.session_state.preview_url = None
            st.rerun()
    
    query = st.text_input("COSA VUOI ASCOLTARE?", placeholder="ARTISTA O BRANO...")
    if query:
        results = search_hybrid(query)
        for item in results:
            with st.container():
                st.markdown(f'<div class="result-card"><h4>{item["title"]}</h4></div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    # CLICCANDO QUI, IL PLAYER IN ALTO SI AGGIORNA E QUELLO VECCHIO SI FERMA [cite: 2026-02-25]
                    if st.button(f"▶️ ASCOLTA", key=f"play_{item['id']}"):
                        st.session_state.preview_url = item['url']
                        st.rerun()
                with c2:
                    if st.button(f"➕ SALVA", key=f"add_{item['id']}"):
                        df = get_db()
                        new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "CATEGORIA": "SINGOLO"}])
                        conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                        st.success("AGGIUNTO!")

# --- TAB 2: LIBRERIA (PLAYER SINGOLO - IMPOSSIBILE SOVRAPPORRE) ---
with menu[1]:
    df = get_db()
    if df.empty: st.warning("LA TUA LIBRERIA È VUOTA.")
    else:
        df_songs = df[df['CATEGORIA'] == "SINGOLO"]
        if not df_songs.empty:
            if st.session_state.track_idx >= len(df_songs): st.session_state.track_idx = 0
            curr = df_songs.iloc[st.session_state.track_idx]
            
            st.markdown(f"### 🎼 {curr['TITOLO']}")
            # NELLA LIBRERIA C'È SOLO UN PLAYER: SE CAMBI CANZONE, QUESTA SI SOSTITUISCE [cite: 2026-02-25]
            st.video(curr['URL'])
            
            c_p, c_n = st.columns(2)
            if c_p.button("⏮ INDIETRO"):
                st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df_songs)
                st.rerun()
            if c_n.button("⏭ AVANTI"):
                st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df_songs)
                st.rerun()

# --- TAB 3: DOWNLOAD ---
with menu[2]:
    st.markdown("### 📥 COPIA E SCARICA OFFLINE")
    df = get_db()
    for idx, row in df.iterrows():
        with st.expander(f"🎵 {row['TITOLO']}"):
            st.code(row['URL'], language="text")
            st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:45px; background-color:#007FFF; color:white; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">🚀 SCARICA MP3</button></a>', unsafe_allow_html=True)
            if st.button("❌ ELIMINA", key=f"del_{idx}"):
                conn.update(data=df.drop(index=idx))
                st.rerun()

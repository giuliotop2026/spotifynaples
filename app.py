import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 16.0: INTERFACCIA NATIVA DARK MODE [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="collapsed")

# CSS: SPOTIFY DARK DESIGN - NERO PROFONDO E VERDE [cite: 2026-01-20]
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #1DB954 !important; font-weight: 900 !important; text-transform: uppercase !important; }
    
    /* CARTE DEI BRANI TIPO SPOTIFY */
    .result-card { 
        background-color: #181818; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #1DB954; margin-bottom: 15px;
    }
    
    /* BOTTONI ROTONDI NATIVI */
    .stButton>button { 
        background-color: #1DB954 !important; color: white !important; 
        border-radius: 50px !important; font-weight: 900 !important; 
        height: 50px !important; border: none !important;
    }
    
    /* INPUT DARK */
    input { 
        background-color: #282828 !important; color: white !important; 
        border: 1px solid #1DB954 !important; border-radius: 10px !important;
    }
    
    /* TESTI E CODICE */
    p, label { color: #B3B3B3 !important; font-weight: 700 !important; text-transform: uppercase !important; }
    code { background-color: #282828 !important; color: #1DB954 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

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

# NAVIGAZIONE TIPO APP (BARRA LATERALE NASCOSTA)
st.title("🎵 SIMPATIC-MUSIC")
menu = st.tabs(["🔍 CERCA", "🎧 LIBRERIA", "📥 DOWNLOAD"])

# --- TAB 1: RICERCA ---
with menu[0]:
    query = st.text_input("COSA VUOI ASCOLTARE?", placeholder="ARTISTA O BRANO...")
    if query:
        results = search_hybrid(query)
        for item in results:
            with st.container():
                st.markdown(f'<div class="result-card"><h3>{item["title"]}</h3></div>', unsafe_allow_html=True)
                st.video(item['url'])
                if st.button("➕ AGGIUNGI AI PREFERITI", key=f"add_{item['id']}"):
                    df = get_db()
                    new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "CATEGORIA": "SINGOLO"}])
                    conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                    st.success("AGGIUNTO!")

# --- TAB 2: LIBRERIA (PLAYER SPOTIFY STYLE) ---
with menu[1]:
    df = get_db()
    if df.empty: st.warning("LA TUA LIBRERIA È VUOTA.")
    else:
        if 'track_idx' not in st.session_state: st.session_state.track_idx = 0
        df_songs = df[df['CATEGORIA'] == "SINGOLO"]
        
        if not df_songs.empty:
            curr = df_songs.iloc[st.session_state.track_idx]
            st.markdown(f"### 🎼 {curr['TITOLO']}")
            st.video(curr['URL'])
            
            c_p, c_n = st.columns(2)
            if c_p.button("⏮ INDIETRO"):
                st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df_songs)
                st.rerun()
            if c_n.button("⏭ AVANTI"):
                st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df_songs)
                st.rerun()

# --- TAB 3: DOWNLOAD (OFFLINE) ---
with menu[2]:
    st.markdown("### 📥 COPIA E SCARICA OFFLINE")
    df = get_db()
    for idx, row in df.iterrows():
        with st.expander(f"🎵 {row['TITOLO']}"):
            st.code(row['URL'], language="text")
            st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:45px; background-color:#007FFF; color:white; border-radius:10px; border:none; font-weight:bold;">🚀 SCARICA MP3</button></a>', unsafe_allow_html=True)
            if st.button("❌ ELIMINA", key=f"del_{idx}"):
                conn.update(data=df.drop(index=idx))
                st.rerun()

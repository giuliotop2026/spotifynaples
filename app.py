import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# Configurazione dell'interfaccia dark ottimizzata per smartphone
st.set_page_config(page_title="Simpatic-Music", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #1DB954 !important; font-weight: 900 !important; }
    .result-card { 
        background-color: #181818; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #1DB954; margin-bottom: 15px;
    }
    .stButton>button { 
        background-color: #1DB954 !important; color: white !important; 
        border-radius: 50px !important; font-weight: 700 !important; 
        height: 45px !important; border: none !important; width: 100% !important;
    }
    .btn-download>button { background-color: #007FFF !important; }
    input { 
        background-color: #282828 !important; color: white !important; 
        border: 1px solid #1DB954 !important; border-radius: 10px !important;
    }
    p, label { color: #B3B3B3 !important; font-weight: 700; }
    code { background-color: #282828 !important; color: #1DB954 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# Gestione della sessione per evitare sovrapposizioni audio
if 'preview_url' not in st.session_state: st.session_state.preview_url = None
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0

def get_db():
    try: 
        return conn.read(ttl=0)
    except: 
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

def search_music(query):
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

st.title("🎵 Simpatic-Music")
tabs = st.tabs(["🔍 Cerca", "🎧 Libreria", "📥 Download"])

# --- SCHEDA RICERCA ---
with tabs[0]:
    if st.session_state.preview_url:
        st.video(st.session_state.preview_url)
        if st.button("⏹ Stop Anteprima"):
            st.session_state.preview_url = None
            st.rerun()
    
    query = st.text_input("Cerca brani o artisti", placeholder="Esempio: Pino Daniele...")
    if query:
        results = search_music(query)
        for item in results:
            with st.container():
                st.markdown(f'<div class="result-card"><h4>{item["title"]}</h4></div>', unsafe_allow_html=True)
                col_play, col_lib, col_dl = st.columns([1, 1, 1])
                
                with col_play:
                    if st.button(f"▶️ Ascolta", key=f"p_{item['id']}"):
                        st.session_state.preview_url = item['url']
                        st.rerun()
                
                with col_lib:
                    if st.button(f"🎧 Libreria", key=f"lib_{item['id']}"):
                        df = get_db()
                        new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "CATEGORIA": "LIBRERIA"}])
                        conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                        st.success("Aggiunto alla Libreria!")
                
                with col_dl:
                    st.markdown('<div class="btn-download">', unsafe_allow_html=True)
                    if st.button(f"📥 Download", key=f"dl_{item['id']}"):
                        df = get_db()
                        new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "CATEGORIA": "DOWNLOAD"}])
                        conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                        st.success("Aggiunto ai Download!")
                    st.markdown('</div>', unsafe_allow_html=True)

# --- SCHEDA LIBRERIA (SOLO ASCOLTO) ---
with tabs[1]:
    df = get_db()
    if df.empty or "LIBRERIA" not in df['CATEGORIA'].values:
        st.info("La tua Libreria è vuota. Aggiungi brani dalla ricerca.")
    else:
        df_lib = df[df['CATEGORIA'] == "LIBRERIA"].reset_index(drop=True)
        if st.session_state.track_idx >= len(df_lib): st.session_state.track_idx = 0
        
        curr = df_lib.iloc[st.session_state.track_idx]
        st.markdown(f"### 🎼 {curr['TITOLO']}")
        st.video(curr['URL'])
        
        c_p, c_n = st.columns(2)
        if c_p.button("⏮ Precedente"):
            st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df_lib)
            st.rerun()
        if c_n.button("⏭ Successivo"):
            st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df_lib)
            st.rerun()

# --- SCHEDA DOWNLOAD (LINK E CANCELLAZIONE) ---
with tabs[2]:
    df = get_db()
    df_dl = df[df['CATEGORIA'] == "DOWNLOAD"]
    if df_dl.empty:
        st.info("Nessun brano pronto per il download.")
    else:
        for idx, row in df_dl.iterrows():
            with st.expander(f"📥 Scarica: {row['TITOLO']}"):
                st.write("Copia il link e incollalo nel convertitore:")
                st.code(row['URL'], language="text")
                st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:45px; background-color:#007FFF; color:white; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">Apri Download</button></a>', unsafe_allow_html=True)
                if st.button("Rimuovi dai Download", key=f"rm_{idx}"):
                    conn.update(data=df.drop(index=idx))
                    st.rerun()

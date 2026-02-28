import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 18.1: ZERO ERRORI DI SINTASSI E LIBRERIA UNIFICATA [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="collapsed")

# CSS: DESIGN DARK CON ILLUMINAZIONE ATTIVA (GLOW) [cite: 2026-01-20]
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #1DB954 !important; font-weight: 900; }
    
    .result-card { 
        background-color: #181818; padding: 15px; border-radius: 10px; 
        border: 2px solid #282828; margin-bottom: 15px; transition: 0.3s;
    }
    
    .active-card { 
        background-color: #282828 !important; 
        border: 2px solid #1DB954 !important; 
        box-shadow: 0px 0px 15px rgba(29, 185, 84, 0.4);
    }
    
    .stButton>button { 
        background-color: #1DB954 !important; color: white !important; 
        border-radius: 50px !important; font-weight: 700 !important; 
        height: 45px !important; border: none !important; width: 100% !important;
    }
    
    .btn-delete>button { background-color: #E91E63 !important; }
    
    input { 
        background-color: #282828 !important; color: white !important; 
        border: 1px solid #1DB954 !important; border-radius: 10px !important;
    }
    
    p, label { color: #B3B3B3 !important; font-weight: 700; text-transform: uppercase !important; }
    code { background-color: #282828 !important; color: #1DB954 !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# INIZIALIZZAZIONE SESSIONE [cite: 2026-02-25]
if 'preview_url' not in st.session_state: st.session_state.preview_url = None
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL"])

def search_music(query):
    try:
        results = ytmusic.search(query, limit=15)
        formatted = []
        # CORREZIONE SINTASSI: CICLO FOR PULITO SENZA WALRUS OPERATOR [cite: 2026-02-25]
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
tabs = st.tabs(["🔍 CERCA", "📚 LIBRERIA"])

# --- TAB 1: CERCA ---
with tabs[0]:
    if st.session_state.preview_url:
        st.video(st.session_state.preview_url)
        if st.button("⏹ STOP ASCOLTO"):
            st.session_state.preview_url = None
            st.rerun()
    
    query = st.text_input("COSA VUOI ASCOLTARE? (MAIUSCOLO) [cite: 2026-01-20]", placeholder="ESEMPIO: PINO DANIELE...")
    if query:
        results = search_music(query)
        for item in results:
            is_active = "active-card" if st.session_state.preview_url == item['url'] else ""
            with st.container():
                st.markdown(f'''<div class="result-card {is_active}"><h4>{'▶️ ' if is_active else ''}{item["title"]}</h4></div>''', unsafe_allow_html=True)
                col_p, col_s = st.columns(2)
                with col_p:
                    if st.button(f"▶️ ASCOLTA", key=f"p_{item['id']}"):
                        st.session_state.preview_url = item['url']
                        st.rerun()
                with col_s:
                    if st.button(f"💾 SALVA IN LIBRERIA", key=f"s_{item['id']}"):
                        df = get_db()
                        new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url']}])
                        conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                        st.success("AGGIUNTO!")

# --- TAB 2: LIBRERIA ---
with tabs[1]:
    df = get_db()
    if df.empty:
        st.info("LA TUA LIBRERIA È VUOTA. AGGIUNGI BRANI DALLA SEZIONE CERCA [cite: 2026-02-20].")
    else:
        if st.session_state.track_idx >= len(df): st.session_state.track_idx = 0
        curr = df.iloc[st.session_state.track_idx]
        st.markdown(f"### 🎼 {curr['TITOLO']}")
        st.video(curr['URL'])
        
        c_p, c_n = st.columns(2)
        if c_p.button("⏮ PRECEDENTE"):
            st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df)
            st.rerun()
        if c_n.button("⏭ SUCCESSIVO"):
            st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df)
            st.rerun()

        st.write("---")
        for idx, row in df.iterrows():
            with st.expander(f"⚙️ GESTISCI: {row['TITOLO']}"):
                st.code(row['URL'], language="text")
                notube_url = f"https://notube.link/it/youtube-app-317?url={row['URL']}"
                st.markdown(f'<a href="{notube_url}" target="_blank"><button style="width:100%; height:45px; background-color:#007FFF; color:white; border-radius:10px; border:none; font-weight:bold;">VAI AL DOWNLOAD</button></a>', unsafe_allow_html=True)
                st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
                if st.button("❌ ELIMINA DALLA LIBRERIA", key=f"rm_{idx}"):
                    conn.update(data=df.drop(index=idx))
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

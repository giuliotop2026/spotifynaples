import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 19.0: CONTROLLO TOTALE E ZERO SOVRAPPOSIZIONI
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="collapsed")

# CSS: DESIGN DARK SPOTIFY CON ILLUMINAZIONE ATTIVA
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #1DB954 !important; font-weight: 900; }
    
    .result-card { 
        background-color: #181818; padding: 15px; border-radius: 10px; 
        border: 2px solid #282828; margin-bottom: 10px; transition: 0.3s;
    }
    
    .active-card { 
        background-color: #282828 !important; border: 2px solid #1DB954 !important; 
        box-shadow: 0px 0px 15px rgba(29, 185, 84, 0.4);
    }
    
    .stButton>button { 
        background-color: #1DB954 !important; color: white !important; 
        border-radius: 50px !important; font-weight: 700 !important; 
        height: 45px !important; border: none !important; width: 100% !important;
    }
    
    .btn-delete>button { background-color: #E91E63 !important; }
    .btn-control>button { background-color: #007FFF !important; height: 60px !important; font-size: 20px !important; }
    
    .already-saved { color: #1DB954 !important; font-weight: 900; text-align: center; }
    input { background-color: #282828 !important; color: white !important; border: 1px solid #1DB954 !important; border-radius: 10px !important; }
    p, label { color: #B3B3B3 !important; font-weight: 700; text-transform: uppercase !important; }
    code { background-color: #282828 !important; color: #1DB954 !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# INIZIALIZZAZIONE SESSIONE PER CONTROLLO GLOBALE
if 'preview_url' not in st.session_state: st.session_state.preview_url = None
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0
if 'lib_playing' not in st.session_state: st.session_state.lib_playing = False

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL"])

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

st.title("🎵 SIMPATIC-MUSIC")
tabs = st.tabs(["🔍 CERCA", "📚 LIBRERIA"])

# --- TAB 1: CERCA ---
with tabs[0]:
    if st.session_state.preview_url:
        st.markdown("### 🔊 ANTEPRIMA IN CORSO")
        st.video(st.session_state.preview_url)
        if st.button("⏹ STOP ASCOLTO"):
            st.session_state.preview_url = None
            st.rerun()
    
    query = st.text_input("COSA VUOI ASCOLTARE?", placeholder="ESEMPIO: PINO DANIELE...")
    if query:
        results = search_music(query)
        df_current = get_db()
        for item in results:
            is_active = "active-card" if st.session_state.preview_url == item['url'] else ""
            is_saved = item['url'] in df_current['URL'].values
            with st.container():
                st.markdown(f'''<div class="result-card {is_active}"><h4>{'▶️ ' if is_active else ''}{item["title"]}</h4></div>''', unsafe_allow_html=True)
                col_p, col_s = st.columns(2)
                with col_p:
                    if st.button(f"▶️ ASCOLTA", key=f"p_{item['id']}"):
                        st.session_state.preview_url = item['url']
                        st.session_state.lib_playing = False
                        st.rerun()
                with col_s:
                    if is_saved:
                        st.markdown('<div class="already-saved">✅ BRANO GIÀ SALVATO</div>', unsafe_allow_html=True)
                    else:
                        if st.button(f"💾 SALVA IN LIBRERIA", key=f"s_{item['id']}"):
                            df = get_db()
                            new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url']}])
                            conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                            st.success("AGGIUNTO!")
                            st.rerun()

# --- TAB 2: LIBRERIA (CONTROLLO TOTALE) ---
with tabs[1]:
    df = get_db()
    if df.empty:
        st.info("LA TUA LIBRERIA È VUOTA.")
    else:
        if st.session_state.track_idx >= len(df): st.session_state.track_idx = 0
        curr = df.iloc[st.session_state.track_idx]
        
        st.markdown(f"### 🎼 ORA IN ONDA: {curr['TITOLO']}")
        
        # CONTROLLI MUSICA SOPRA IL VIDEO
        col_prev, col_play, col_next = st.columns([1, 1, 1])
        with col_prev:
            if st.button("⏮ INDIETRO", key="lib_prev"):
                st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df)
                st.session_state.lib_playing = True
                st.session_state.preview_url = None
                st.rerun()
        with col_play:
            if not st.session_state.lib_playing:
                if st.button("▶️ PLAY", key="lib_start"):
                    st.session_state.lib_playing = True
                    st.session_state.preview_url = None
                    st.rerun()
            else:
                if st.button("⏸ STOP", key="lib_stop"):
                    st.session_state.lib_playing = False
                    st.rerun()
        with col_next:
            if st.button("⏭ AVANTI", key="lib_next"):
                st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df)
                st.session_state.lib_playing = True
                st.session_state.preview_url = None
                st.rerun()

        # PLAYER VIDEO SOTTO I CONTROLLI
        if st.session_state.lib_playing:
            st.video(curr['URL'])
        else:
            st.markdown('<div style="background-color:#181818; height:200px; border-radius:10px; display:flex; align-items:center; justify-content:center; border:2px dashed #282828;"><h4>SISTEMA IN STANDBY</h4></div>', unsafe_allow_html=True)

        st.write("---")
        st.markdown("### 📋 CODA DI RIPRODUZIONE (TOCCA PER ASCOLTARE)")
        
        # LISTA BRANI CON SELEZIONE DIRETTA
        for idx, row in df.iterrows():
            is_playing_now = (idx == st.session_state.track_idx and st.session_state.lib_playing)
            card_class = "active-card" if is_playing_now else ""
            
            with st.container():
                st.markdown(f'''<div class="result-card {card_class}"><strong>{idx + 1}. {row['TITOLO']}</strong></div>''', unsafe_allow_html=True)
                c_play, c_gest, c_del = st.columns([1, 2, 1])
                
                with c_play:
                    if st.button(f"▶️", key=f"play_direct_{idx}"):
                        st.session_state.track_idx = idx
                        st.session_state.lib_playing = True
                        st.session_state.preview_url = None
                        st.rerun()
                
                with c_gest:
                    with st.expander("SCARICA"):
                        st.code(row['URL'], language="text")
                        st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:35px; background-color:#007FFF; color:white; border-radius:5px; border:none; font-weight:bold; cursor:pointer;">DOWNLOAD</button></a>', unsafe_allow_html=True)
                
                with c_del:
                    st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
                    if st.button("❌", key=f"rm_lib_{idx}"):
                        conn.update(data=df.drop(index=idx))
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

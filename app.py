import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 21.0: VISUAL ENGINE & MOBILE HYBRID LAYOUT [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="collapsed")

# CSS: SPOTIFY DARK DESIGN CON COPERTINE ARROTONDATE E LISTA MOBILE [cite: 2026-01-20]
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #1DB954 !important; font-weight: 900; }
    
    /* PLAYER PRINCIPALE */
    .main-player {
        background-color: #121212; padding: 20px; border-radius: 20px;
        border: 1px solid #282828; text-align: center; margin-bottom: 25px;
    }
    
    /* COPERTINA BRANO */
    .album-cover {
        width: 250px; height: 250px; border-radius: 15px;
        object-fit: cover; box-shadow: 0px 10px 30px rgba(0,0,0,0.8);
        margin: 0 auto 20px auto; border: 2px solid #1DB954;
    }
    
    /* LISTA BRANI SOTTO IL PLAYER */
    .track-row {
        background-color: #181818; padding: 12px; border-radius: 10px;
        margin-bottom: 10px; display: flex; align-items: center;
        border: 1px solid #282828; transition: 0.3s;
    }
    .active-row { border-color: #1DB954 !important; background-color: #282828 !important; }
    
    .stButton>button { 
        background-color: #1DB954 !important; color: white !important; 
        border-radius: 50px !important; font-weight: 700 !important; border: none !important;
    }
    .btn-delete>button { background-color: #E91E63 !important; }
    input { background-color: #181818 !important; color: white !important; border: 1px solid #1DB954 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# SESSIONE PER IL CONTROLLO [cite: 2026-02-25]
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0
if 'is_playing' not in st.session_state: st.session_state.is_playing = False

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

def search_music(query):
    try:
        results = ytmusic.search(query, limit=15)
        formatted = []
        for res in results:
            if res.get('resultType') in ['song', 'video']:
                artists = res.get('artists', [{'name': 'Artista'}])
                # CATTURA LA COPERTINA (THUMBNAIL) [cite: 2026-02-25]
                thumb = res.get('thumbnails', [{'url': ''}])[-1]['url']
                formatted.append({
                    'id': res.get('videoId'),
                    'title': f"{artists[0]['name']} - {res['title']}".upper(),
                    'url': f"https://www.youtube.com/watch?v={res['videoId']}",
                    'thumb': thumb
                })
        return formatted
    except: return []

st.title("🎵 SIMPATIC-MUSIC")
tabs = st.tabs(["🎧 LIBRERIA", "🔍 SCOPRI", "📥 SCARICA"])

# --- TAB 1: LIBRERIA (PLAYER + LISTA SOTTO) ---
with tabs[0]:
    df = get_db()
    if df.empty:
        st.info("IL CANTIERE È VUOTO. AGGIUNGI MUSICA [cite: 2026-02-20].")
    else:
        # PLAYER SUPREMO IN ALTO [cite: 2026-02-25]
        if st.session_state.track_idx >= len(df): st.session_state.track_idx = 0
        curr = df.iloc[st.session_state.track_idx]
        
        with st.container():
            st.markdown(f'<div class="main-player">', unsafe_allow_html=True)
            # MOSTRA LA COPERTINA ORIGINALE [cite: 2026-02-25]
            if 'COPERTINA' in curr and pd.notnull(curr['COPERTINA']):
                st.image(curr['COPERTINA'], width=250)
            else:
                st.markdown('<div class="album-cover"><h1>🎵</h1></div>', unsafe_allow_html=True)
            
            st.markdown(f"### {curr['TITOLO']}")
            
            c1, c2, c3 = st.columns([1,1,1])
            if c1.button("⏮", key="l_prev"):
                st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df)
                st.session_state.is_playing = True
                st.rerun()
            with c2:
                if st.button("▶️/⏸", key="l_play"):
                    st.session_state.is_playing = not st.session_state.is_playing
                    st.rerun()
            if c3.button("⏭", key="l_next"):
                st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df)
                st.session_state.is_playing = True
                st.rerun()
            
            if st.session_state.is_playing:
                st.video(curr['URL'])
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        st.markdown("### 📋 LA TUA DISCOTECA")
        
        # LISTA SCORREVILE SOTTO IL PLAYER [cite: 2026-02-25]
        for idx, row in df.iterrows():
            is_active = "active-row" if idx == st.session_state.track_idx else ""
            with st.container():
                col_img, col_txt, col_btn = st.columns([1, 4, 1])
                with col_img:
                    if 'COPERTINA' in row and pd.notnull(row['COPERTINA']):
                        st.image(row['COPERTINA'], width=50)
                with col_txt:
                    st.markdown(f"**{row['TITOLO']}**")
                with col_btn:
                    if st.button("▶️", key=f"list_p_{idx}"):
                        st.session_state.track_idx = idx
                        st.session_state.is_playing = True
                        st.rerun()

# --- TAB 2: SCOPRI (CON ANTEPRIMA COPERTINE) ---
with tabs[1]:
    query = st.text_input("CERCA BRANO O ARTISTA")
    if query:
        results = search_music(query)
        df_current = get_db()
        for item in results:
            is_saved = item['url'] in df_current['URL'].values
            with st.container():
                c_img, c_info = st.columns([1, 3])
                with c_img: st.image(item['thumb'], width=80)
                with c_info:
                    st.markdown(f"**{item['title']}**")
                    if is_saved:
                        st.write("✅ GIÀ IN LIBRERIA")
                    else:
                        if st.button("💾 AGGIUNGI", key=f"add_{item['id']}"):
                            new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "COPERTINA": item['thumb']}])
                            conn.update(data=pd.concat([df_current, new_row], ignore_index=True).drop_duplicates())
                            st.success("SALVATO!")
                            st.rerun()

# --- TAB 3: GESTISCI & DOWNLOAD ---
with tabs[2]:
    for idx, row in df.iterrows():
        with st.expander(f"⚙️ {row['TITOLO']}"):
            st.code(row['URL'])
            st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:40px; background-color:#007FFF; color:white; border:none; border-radius:10px; font-weight:bold;">SCARICA MP3</button></a>', unsafe_allow_html=True)
            st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
            if st.button("❌ ELIMINA", key=f"del_{idx}"):
                conn.update(data=df.drop(index=idx))
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

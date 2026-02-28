import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 24.0: PLAYER SUPREMO E ZERO ERRORI [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS: SPOTIFY CLONE TOTALE - DARK MODE NATIVO [cite: 2026-01-20, 2026-02-25]
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #282828; }
    
    h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 900 !important; }
    .spotify-green { color: #1DB954 !important; }
    
    .track-card {
        background-color: #181818; padding: 12px; border-radius: 12px;
        transition: 0.3s; border: 1px solid transparent; margin-bottom: 10px;
    }
    .active-card { background-color: #282828 !important; border: 1px solid #1DB954 !important; }

    .stButton>button { 
        background-color: #1DB954 !important; color: white !important; 
        border-radius: 50px !important; font-weight: 700 !important; 
        height: 40px !important; border: none !important; width: 100% !important;
    }
    .btn-play>button { background-color: #FFFFFF !important; color: #000000 !important; }
    .btn-delete>button { background-color: #E91E63 !important; }
    
    input { background-color: #282828 !important; color: white !important; border: 1px solid #1DB954 !important; border-radius: 8px !important; }
    
    /* FIX PER IMMAGINI PULITE */
    .stImage > img { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# SESSION STATE PER RIPRODUZIONE GLOBALE [cite: 2026-02-25]
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0
if 'current_url' not in st.session_state: st.session_state.current_url = None
if 'current_view' not in st.session_state: st.session_state.current_view = "🔍 SCOPRI"

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.markdown("# <span class='spotify-green'>SIMPATIC</span>-MUSIC", unsafe_allow_html=True)
    st.write("---")
    if st.button("🔍 SCOPRI NUOVA MUSICA"): st.session_state.current_view = "🔍 SCOPRI"; st.rerun()
    if st.button("🎧 LA TUA LIBRERIA"): st.session_state.current_view = "🎧 LIBRERIA"; st.rerun()
    if st.button("📥 GESTISCI & DOWNLOAD"): st.session_state.current_view = "📥 DOWNLOAD"; st.rerun()

df = get_db()

# --- LOGICA VISUALIZZAZIONE ---
if st.session_state.current_view == "🔍 SCOPRI":
    st.title("CERCA SINFONIE ")
    
    # PLAYER MASTER PER SCOPRI [cite: 2026-02-25]
    if st.session_state.current_url:
        st.video(st.session_state.current_url)
        if st.button("⏹ STOP ASCOLTO"): st.session_state.current_url = None; st.rerun()

    query = st.text_input("", placeholder="Cosa vuoi ascoltare? (Pino Daniele, Rocky...)")
    if query:
        with st.spinner("Scansione dell'abisso..."):
            results = ytmusic.search(query, limit=12)
            for res in results:
                if res.get('resultType') in ['song', 'video']:
                    title = f"{res.get('artists', [{'name': 'Artista'}])[0]['name']} - {res['title']}".upper()
                    url = f"https://www.youtube.com/watch?v={res['videoId']}"
                    thumb = res.get('thumbnails', [{'url': ''}])[-1]['url']
                    
                    is_saved = url in df['URL'].values
                    is_playing = st.session_state.current_url == url
                    
                    st.markdown(f'<div class="track-card {"active-card" if is_playing else ""}">', unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1, 4, 1, 1])
                    with c1: st.image(thumb, width=60)
                    with c2: st.markdown(f"**{title}**")
                    with c3:
                        st.markdown('<div class="btn-play">', unsafe_allow_html=True)
                        if st.button("▶️", key=f"p_{res['videoId']}"):
                            st.session_state.current_url = url
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with c4:
                        if is_saved: st.write("✅")
                        else:
                            if st.button("💾", key=f"add_{res['videoId']}"):
                                df_now = get_db()
                                new_row = pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": thumb}])
                                conn.update(data=pd.concat([df_now, new_row], ignore_index=True).drop_duplicates())
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_view == "🎧 LIBRERIA":
    if df.empty:
        st.info("LIBRERIA VUOTA [cite: 2026-02-20].")
    else:
        # PLAYER LIBRERIA SEMPRE PRONTO [cite: 2026-02-25]
        if st.session_state.track_idx >= len(df): st.session_state.track_idx = 0
        curr = df.iloc[st.session_state.track_idx]
        
        st.title("LIBRERIA")
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
            is_active = idx == st.session_state.track_idx
            st.markdown(f'<div class="track-card {"active-card" if is_active else ""}">', unsafe_allow_html=True)
            cl1, cl2, cl3 = st.columns([1, 5, 1])
            with cl1: 
                if 'COPERTINA' in row and pd.notnull(row['COPERTINA']): st.image(row['COPERTINA'], width=40)
            with cl2: st.markdown(f"**{row['TITOLO']}**")
            with cl3:
                if st.button("▶️", key=f"lib_p_{idx}"):
                    st.session_state.track_idx = idx
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

else: # DOWNLOAD
    st.title("SALA INCISIONE")
    for idx, row in df.iterrows():
        with st.expander(f"⚙️ {row['TITOLO']}"):
            st.code(row['URL'])
            st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:40px; background-color:#007FFF; color:white; border:none; border-radius:10px; font-weight:bold;">SCARICA MP3</button></a>', unsafe_allow_html=True)
            st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
            if st.button("❌ ELIMINA", key=f"del_{idx}"):
                conn.update(data=df.drop(index=idx))
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

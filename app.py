import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 27.0: CLONE TOTALE E MOTORE DI EMERGENZA [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS: L'ANIMA VISIVA DI SPOTIFY - ZERO ERRORI, SOLO CEMENTO [cite: 2026-01-20, 2026-02-25]
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #121212; }
    
    /* SIDEBAR: PULSANTI TIPO APP NATIVA */
    .stSidebar [data-testid="stVerticalBlock"] button {
        background-color: transparent !important; color: #b3b3b3 !important;
        border: none !important; text-align: left !important; justify-content: flex-start !important;
        font-size: 16px !important; font-weight: 700 !important; padding: 10px 0px !important;
    }
    .stSidebar [data-testid="stVerticalBlock"] button:hover { color: #FFFFFF !important; }
    
    /* TITOLI SEZIONI */
    .section-title { font-size: 24px; font-weight: 800; color: white; margin: 25px 0 15px 0; }
    .spotify-green { color: #1DB954 !important; }

    /* GRID CARDS (HOME PAGE) */
    .grid-card {
        background-color: #181818; padding: 15px; border-radius: 8px;
        transition: 0.3s; height: 100%; cursor: pointer;
    }
    .grid-card:hover { background-color: #282828; }
    .img-square { border-radius: 6px; width: 100%; aspect-ratio: 1; object-fit: cover; margin-bottom: 12px; }
    .img-circle { border-radius: 50%; width: 100%; aspect-ratio: 1; object-fit: cover; margin-bottom: 12px; }
    .card-title { color: white; font-weight: 700; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .card-artist { color: #A7A7A7; font-size: 13px; margin-top: 4px; }

    /* LISTA BRANI (LIBRERIA E CERCA) */
    .track-row { padding: 8px 12px; border-radius: 4px; display: flex; align-items: center; transition: 0.2s; }
    .track-row:hover { background-color: rgba(255,255,255,0.1); }
    
    /* PULSANTI AZIONE (PLAY/SALVA) */
    .btn-pill button {
        background-color: #1DB954 !important; color: black !important;
        border-radius: 50px !important; border: none !important;
        font-weight: 700 !important; height: 35px !important;
    }
    .btn-pill button:hover { transform: scale(1.04); background-color: #1ed760 !important; }
    
    /* SEARCH BAR NATIVA */
    input { background-color: #242424 !important; color: white !important; border-radius: 500px !important; border: 1px solid transparent !important; }
    input:focus { border-color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# SESSIONE [cite: 2026-02-25]
if 'current_view' not in st.session_state: st.session_state.current_view = "🏠 HOME"
if 'current_url' not in st.session_state: st.session_state.current_url = None
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

def get_home_content():
    # MOTORE DI EMERGENZA: SE CHARTS FALLISCE, CERCA HIT GENERICHE [cite: 2026-02-25]
    try:
        charts = ytmusic.get_charts(country='IT')
        if charts and 'trending' in charts: return charts
    except: pass
    
    # FALLBACK: SCANSIONE ABISSO PER HIT 2026 [cite: 2026-02-20]
    try:
        emergency_search = ytmusic.search("Top Hits 2026 Italy", filter="songs", limit=10)
        return {'trending': {'items': emergency_search}, 'videos': {'items': []}}
    except: return None

# --- SIDEBAR (PULITA COME SPOTIFY) ---
with st.sidebar:
    st.markdown("## <span class='spotify-green'>SIMPATIC</span> MUSIC", unsafe_allow_html=True)
    st.write("")
    if st.button("🏠 Home"): st.session_state.current_view = "🏠 HOME"; st.rerun()
    if st.button("🔍 Cerca"): st.session_state.current_view = "🔍 CERCA"; st.rerun()
    if st.button("🎧 La tua libreria"): st.session_state.current_view = "🎧 LIBRERIA"; st.rerun()

df = get_db()

# --- PLAYER SUPREMO (SEMPRE IN ALTO SE ATTIVO) ---
if st.session_state.current_url:
    st.video(st.session_state.current_url)
    if st.button("⏹ STOP"): st.session_state.current_url = None; st.rerun()
    st.write("---")

# === VISTA: HOME (L'ANIMA DI SPOTIFY) ===
if st.session_state.current_view == "🏠 HOME":
    st.markdown('<div class="section-title">Brani di tendenza</div>', unsafe_allow_html=True)
    content = get_home_content()
    
    if content and 'trending' in content:
        cols = st.columns(5)
        items = content['trending'].get('items', [])
        for i, item in enumerate(items[:5]):
            with cols[i]:
                thumb = item['thumbnails'][-1]['url']
                title = item['title']
                artist = item['artists'][0]['name'] if item.get('artists') else "Artista"
                
                st.markdown(f'''
                <div class="grid-card">
                    <img src="{thumb}" class="img-square">
                    <div class="card-title">{title}</div>
                    <div class="card-artist">{artist}</div>
                </div>
                ''', unsafe_allow_html=True)
                
                st.markdown('<div class="btn-pill">', unsafe_allow_html=True)
                if st.button("▶", key=f"h_p_{i}_{item.get('videoId','id')}"):
                    v_id = item.get('videoId') if item.get('videoId') else item.get('id')
                    st.session_state.current_url = f"https://www.youtube.com/watch?v={v_id}"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("ERRORE: IL MURO DI YOUTUBE È TROPPO ALTO. RIPROVA TRA 2 MINUTI [cite: 2026-02-20].")

# === VISTA: CERCA ===
elif st.session_state.current_view == "🔍 CERCA":
    st.markdown('<div class="section-title">Cerca</div>', unsafe_allow_html=True)
    query = st.text_input("", placeholder="Cosa vuoi ascoltare?")
    if query:
        results = ytmusic.search(query, limit=12)
        for res in results:
            if res.get('resultType') in ['song', 'video']:
                title = f"{res.get('artists', [{'name': ''}])[0]['name']} - {res['title']}".upper()
                url = f"https://www.youtube.com/watch?v={res['videoId']}"
                thumb = res.get('thumbnails', [{'url': ''}])[-1]['url']
                
                st.markdown('<div class="track-row">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1, 6, 1, 1])
                with c1: st.image(thumb, width=50)
                with c2: st.markdown(f"**{title}**")
                with c3:
                    st.markdown('<div class="btn-pill">', unsafe_allow_html=True)
                    if st.button("▶", key=f"s_p_{res['videoId']}"):
                        st.session_state.current_url = url; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with c4:
                    if url not in df['URL'].values:
                        if st.button("💾", key=f"s_s_{res['videoId']}"):
                            df_new = pd.concat([get_db(), pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": thumb}])], ignore_index=True)
                            conn.update(data=df_new.drop_duplicates())
                            st.rerun()
                    else: st.write("✅")

# === VISTA: LIBRERIA ===
elif st.session_state.current_view == "🎧 LIBRERIA":
    st.markdown('<div class="section-title">La tua libreria</div>', unsafe_allow_html=True)
    if df.empty: st.info("Cantiere vuoto.")
    else:
        for idx, row in df.iterrows():
            st.markdown('<div class="track-row">', unsafe_allow_html=True)
            cl1, cl2, cl3, cl4 = st.columns([1, 6, 1, 1])
            with cl1: st.image(row['COPERTINA'], width=45)
            with cl2: st.markdown(f"**{row['TITOLO']}**")
            with cl3:
                st.markdown('<div class="btn-pill">', unsafe_allow_html=True)
                if st.button("▶", key=f"l_p_{idx}"):
                    st.session_state.current_url = row['URL']; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with cl4:
                if st.button("❌", key=f"l_d_{idx}"):
                    conn.update(data=df.drop(index=idx)); st.rerun()

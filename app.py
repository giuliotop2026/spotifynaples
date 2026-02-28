import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 29.0: RIPRISTINO MENU E MOTORE INFINITO
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS: SPOTIFY CLONE - SIDEBAR PULITA E BOTTONI CARD MIRATI
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #282828; }
    
    /* TITOLI SEZIONI */
    .section-title { font-size: 24px; font-weight: 800; color: white; margin-bottom: 20px; border-left: 5px solid #1DB954; padding-left: 15px; }
    
    /* MENU A SINISTRA (SIDEBAR) - RIPRISTINATO */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important; color: #b3b3b3 !important;
        border: none !important; text-align: left !important; justify-content: flex-start !important;
        font-size: 16px !important; font-weight: 700 !important; width: 100% !important;
        height: auto !important; border-radius: 4px !important; padding: 10px !important;
    }
    [data-testid="stSidebar"] .stButton button:hover { color: #FFFFFF !important; background-color: #282828 !important; }

    /* CARD HOME PAGE */
    .grid-card { background-color: #181818; padding: 15px; border-radius: 8px; transition: 0.3s; height: 100%; }
    .grid-card:hover { background-color: #282828; }
    .img-square { border-radius: 6px; width: 100%; aspect-ratio: 1; object-fit: cover; margin-bottom: 10px; }
    .card-title { color: white; font-weight: 700; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    
    /* BOTTONE PLAY VERDE (SOLO PER LE CARD) */
    .play-btn-container .stButton button {
        background-color: #1DB954 !important; color: black !important;
        border-radius: 50% !important; width: 45px !important; height: 45px !important;
        border: none !important; font-size: 20px !important; font-weight: 900 !important;
        margin-top: -50px !important; margin-left: auto !important; display: flex !important;
        align-items: center !important; justify-content: center !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.5) !important;
    }

    /* TRACK LIST (CERCA/LIBRERIA) */
    .track-row { padding: 10px; border-radius: 6px; display: flex; align-items: center; transition: 0.2s; }
    .track-row:hover { background-color: #282828; }
    
    input { background-color: #242424 !important; color: white !important; border-radius: 500px !important; border: 1px solid #1DB954 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

if 'current_view' not in st.session_state: st.session_state.current_view = "🏠 HOME"
if 'current_url' not in st.session_state: st.session_state.current_url = None
if 'genre' not in st.session_state: st.session_state.genre = "HIT DEL MOMENTO"

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

# MOTORE DI EMERGENZA POTENZIATO
@st.cache_data(ttl=3600)
def fetch_home_content(category):
    try:
        if category == "HIT DEL MOMENTO":
            charts = ytmusic.get_charts(country='IT')
            if charts and 'trending' in charts: return charts['trending']['items']
        return ytmusic.search(f"Top {category} 2026", filter="songs", limit=15)
    except:
        return ytmusic.search("Musica 2026", filter="songs", limit=15)

# --- SIDEBAR (RIPRISTINATA) ---
with st.sidebar:
    st.markdown("### <span style='color:#1DB954'>SIMPATIC</span>-MUSIC", unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 Home"): st.session_state.current_view = "🏠 HOME"; st.rerun()
    if st.button("🔍 Cerca"): st.session_state.current_view = "🔍 CERCA"; st.rerun()
    if st.button("🎧 La tua libreria"): st.session_state.current_view = "🎧 LIBRERIA"; st.rerun()
    st.write("---")
    st.markdown("#### GENERE")
    for g in ["ROCK", "JAZZ", "WESTERN", "NAPOLI", "ANNI 80"]:
        if st.button(f"🎵 {g}"):
            st.session_state.genre = g
            st.session_state.current_view = "🏠 HOME"
            st.rerun()

df = get_db()

# --- PLAYER SUPREMO ---
if st.session_state.current_url:
    st.video(st.session_state.current_url)
    if st.button("⏹ STOP ASCOLTO", key="stop_master"): st.session_state.current_url = None; st.rerun()
    st.write("---")

# === VISTA: HOME ===
if st.session_state.current_view == "🏠 HOME":
    st.markdown(f'<div class="section-title">{st.session_state.genre}</div>', unsafe_allow_html=True)
    items = fetch_home_content(st.session_state.genre)
    
    if items:
        for start in range(0, len(items), 5):
            cols = st.columns(5)
            for i, item in enumerate(items[start:start+5]):
                with cols[i]:
                    v_id = item.get('videoId') or item.get('id')
                    thumb = item['thumbnails'][-1]['url']
                    st.markdown(f'''
                    <div class="grid-card">
                        <img src="{thumb}" class="img-square">
                        <div class="card-title">{item['title']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    # BOTTONE VERDE SOLO QUI
                    st.markdown('<div class="play-btn-container">', unsafe_allow_html=True)
                    if st.button("▶", key=f"h_{v_id}"):
                        st.session_state.current_url = f"https://www.youtube.com/watch?v={v_id}"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("SCANSIONE FALLITA. IL CANTIERE È IN MANUTENZIONE.")

# === VISTA: CERCA ===
elif st.session_state.current_view == "🔍 CERCA":
    st.markdown('<div class="section-title">Cerca</div>', unsafe_allow_html=True)
    q = st.text_input("", placeholder="Artisti o canzoni...")
    if q:
        res = ytmusic.search(q, limit=12)
        for r in res:
            if r.get('resultType') in ['song', 'video']:
                title = f"{r['artists'][0]['name']} - {r['title']}".upper()
                url = f"https://www.youtube.com/watch?v={r['videoId']}"
                st.markdown('<div class="track-row">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1, 7, 1])
                with c1: st.image(r['thumbnails'][-1]['url'], width=50)
                with c2: st.markdown(f"**{title}**")
                with c3:
                    if st.button("💾", key=f"s_{r['videoId']}"):
                        new_row = pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": r['thumbnails'][-1]['url']}])
                        conn.update(data=pd.concat([get_db(), new_row], ignore_index=True).drop_duplicates())
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# === VISTA: LIBRERIA ===
elif st.session_state.current_view == "🎧 LIBRERIA":
    st.markdown('<div class="section-title">Libreria</div>', unsafe_allow_html=True)
    if df.empty: st.info("Cantiere vuoto.")
    else:
        for idx, row in df.iterrows():
            st.markdown('<div class="track-row">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 6, 1, 1])
            with c1: st.image(row['COPERTINA'], width=50)
            with c2: st.markdown(f"**{row['TITOLO']}**")
            with c3:
                if st.button("▶", key=f"l_p_{idx}"): st.session_state.current_url = row['URL']; st.rerun()
            with c4:
                if st.button("❌", key=f"l_d_{idx}"): conn.update(data=df.drop(index=idx)); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

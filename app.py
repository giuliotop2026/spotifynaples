import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 33.0: BRANDING RESTORED & PLAY BUTTON FIX [cite: 2026-02-28]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS: DESIGN MINIMALE, ZERO BIANCO, PULSANTI NATIVI [cite: 2026-01-20, 2026-02-25]
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #121212; }
    
    /* TITOLO SUPREMO */
    .app-title { color: #1DB954 !important; font-weight: 900 !important; font-size: 32px !important; text-transform: uppercase; margin-bottom: 20px; }

    /* MENU SIDEBAR - RIPRISTINATO CON TESTO [cite: 2026-02-25] */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important; color: #b3b3b3 !important;
        border: none !important; text-align: left !important; justify-content: flex-start !important;
        font-size: 16px !important; font-weight: 700 !important; width: 100% !important;
        padding: 10px !important; border-radius: 4px !important;
    }
    [data-testid="stSidebar"] .stButton button:hover { color: #FFFFFF !important; background-color: #282828 !important; }

    /* BOTTONI PLAY E SALVA (ZERO BIANCO) [cite: 2026-02-25] */
    .stButton>button { 
        background-color: #1DB954 !important; color: #000000 !important; 
        border-radius: 50px !important; font-weight: 900 !important; 
        border: none !important; height: 40px !important; text-transform: uppercase; font-size: 14px !important;
    }
    .stButton>button:hover { transform: scale(1.03); background-color: #1ed760 !important; }
    
    /* CARD BRANO */
    .track-card { background-color: #121212; padding: 15px; border-radius: 12px; border: 1px solid #181818; margin-bottom: 15px; text-align: center; }
    
    /* LISTA RICERCA */
    .search-row { padding: 10px; border-bottom: 1px solid #181818; transition: 0.2s; }
    .search-row:hover { background-color: #181818; }
    
    input { background-color: #181818 !important; color: white !important; border: 1px solid #1DB954 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# SESSIONE [cite: 2026-02-25]
if 'view' not in st.session_state: st.session_state.view = "HOME"
if 'url' not in st.session_state: st.session_state.url = None

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

@st.cache_data(ttl=3600)
def fetch_real_hits():
    try:
        charts = ytmusic.get_charts(country='IT')
        return charts['trending']['items']
    except:
        return ytmusic.search("Top Global Hits 2026", filter="songs", limit=16)

# --- BRANDING E NAVIGAZIONE ---
st.markdown('<h1 class="app-title">🎵 SIMPATIC-MUSIC</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### NAVIGAZIONE")
    if st.button("🏠 HOME"): st.session_state.view = "HOME"; st.rerun()
    if st.button("🔍 CERCA"): st.session_state.view = "CERCA"; st.rerun()
    if st.button("🎧 LIBRERIA"): st.session_state.view = "LIBRERIA"; st.rerun()
    st.write("---")
    st.markdown("### GENERI")
    for g in ["ROCK", "NAPOLI", "ANNI 80", "JAZZ", "WESTERN"]:
        if st.button(f"🎵 {g}"): 
            st.session_state.genre = g
            st.session_state.view = "GENERE"
            st.rerun()

# --- PLAYER FISSO ---
if st.session_state.url:
    st.video(st.session_state.url)
    if st.button("⏹ CHIUDI PLAYER"): st.session_state.url = None; st.rerun()
    st.write("---")

# === VISTA HOME (TOP HITS) ===
if st.session_state.view == "HOME":
    st.subheader("🔥 BRANI PIÙ ASCOLTATI DEL MOMENTO")
    items = fetch_real_hits()
    
    for start in range(0, len(items), 4):
        cols = st.columns(4)
        for i, item in enumerate(items[start:start+4]):
            with cols[i]:
                v_id = item.get('videoId') or item.get('id')
                thumb = item['thumbnails'][-1]['url']
                st.markdown(f'<div class="track-card">', unsafe_allow_html=True)
                st.image(thumb, use_container_width=True)
                st.write(f"**{item['title'].upper()}**")
                if st.button("▶️ PLAY", key=f"h_{v_id}"):
                    st.session_state.url = f"https://www.youtube.com/watch?v={v_id}"; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# === VISTA CERCA (RIPRISTINATA CON PLAY) ===
elif st.session_state.view == "CERCA":
    st.subheader("🔍 CERCA SINFONIE NEL MONDO")
    q = st.text_input("NOME ARTISTA O CANZONE:")
    if q:
        res = ytmusic.search(q, limit=12)
        for r in res:
            if r.get('resultType') in ['song', 'video']:
                title = f"{r['artists'][0]['name']} - {r['title']}".upper()
                url = f"https://www.youtube.com/watch?v={r['videoId']}"
                with st.container():
                    st.markdown('<div class="search-row">', unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1, 4, 1, 1])
                    c1.image(r['thumbnails'][-1]['url'], width=60)
                    c2.write(f"**{title}**")
                    if c3.button("▶️", key=f"p_s_{r['videoId']}"):
                        st.session_state.url = url; st.rerun()
                    if c4.button("💾", key=f"s_s_{r['videoId']}"):
                        df = get_db()
                        new = pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": r['thumbnails'][-1]['url']}])
                        conn.update(data=pd.concat([df, new], ignore_index=True).drop_duplicates())
                        st.success("SALVATO!")
                    st.markdown('</div>', unsafe_allow_html=True)

# === VISTA LIBRERIA ===
elif st.session_state.view == "LIBRERIA":
    st.subheader("🎧 LA TUA LIBRERIA BLINDATA")
    df = get_db()
    if df.empty: st.info("CANTIERE VUOTO.")
    else:
        for idx, row in df.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([1, 4, 1, 1])
                c1.image(row['COPERTINA'], width=50)
                c2.write(f"**{row['TITOLO']}**")
                if c3.button("▶️", key=f"l_p_{idx}"):
                    st.session_state.url = row['URL']; st.rerun()
                if c4.button("❌", key=f"l_d_{idx}"):
                    conn.update(data=df.drop(index=idx)); st.rerun()

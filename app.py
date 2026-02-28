import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 28.0: CATEGORIE DINAMICHE E DESIGN ZERO-DISTURBO
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS: L'EVOLUZIONE DEFINITIVA - PULIZIA TOTALE
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #121212; }
    
    .section-title { font-size: 26px; font-weight: 800; color: white; margin: 30px 0 15px 0; border-left: 5px solid #1DB954; padding-left: 15px; }
    .spotify-green { color: #1DB954 !important; }

    /* CARD DELLA HOME PAGE - INTEGRATA */
    .grid-card {
        background-color: #181818; padding: 15px; border-radius: 8px;
        transition: 0.3s; height: 100%; border: 1px solid transparent;
    }
    .grid-card:hover { background-color: #282828; }
    .img-square { border-radius: 6px; width: 100%; aspect-ratio: 1; object-fit: cover; box-shadow: 0 8px 24px rgba(0,0,0,.5); }
    .card-title { color: white; font-weight: 700; font-size: 15px; margin-top: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .card-artist { color: #A7A7A7; font-size: 13px; margin-top: 4px; }

    /* RIMOZIONE "COSI BIANCHI" - PULSANTI INVISIBILI O VERDI NATIVI */
    .stButton>button { 
        background-color: #1DB954 !important; color: black !important; 
        border-radius: 50px !important; font-weight: 800 !important; 
        border: none !important; width: 45px !important; height: 45px !important;
        margin-top: -50px !important; margin-left: auto !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
        font-size: 18px !important;
    }
    .stButton>button:hover { transform: scale(1.1) !important; background-color: #1ed760 !important; }
    
    /* FIX PER LIBRERIA E CERCA */
    .track-row { padding: 10px; border-radius: 8px; transition: 0.2s; border: 1px solid transparent; }
    .track-row:hover { background-color: #282828; border-color: #1DB954; }
    
    input { background-color: #242424 !important; color: white !important; border-radius: 500px !important; border: 1px solid #1DB954 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

if 'current_view' not in st.session_state: st.session_state.current_view = "🏠 HOME"
if 'current_url' not in st.session_state: st.session_state.current_url = None
if 'home_genre' not in st.session_state: st.session_state.home_genre = "HIT DEL MOMENTO"

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

# MOTORE DI RICERCA CATEGORIE
@st.cache_data(ttl=3600)
def get_genre_hits(genre):
    try:
        if genre == "HIT DEL MOMENTO":
            charts = ytmusic.get_charts(country='IT')
            return charts['trending']['items'] if charts else []
        else:
            return ytmusic.search(f"Top {genre} 2026", filter="songs", limit=10)
    except: return []

# --- SIDEBAR (PULITA E PROFESSIONALE) ---
with st.sidebar:
    st.markdown("## <span class='spotify-green'>SIMPATIC</span> MUSIC", unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 Home"): st.session_state.current_view = "🏠 HOME"; st.rerun()
    if st.button("🔍 Cerca"): st.session_state.current_view = "🔍 CERCA"; st.rerun()
    if st.button("🎧 La tua libreria"): st.session_state.current_view = "🎧 LIBRERIA"; st.rerun()
    st.write("---")
    st.markdown("### 🏷️ GENERI")
    for g in ["ROCK", "JAZZ", "WESTERN", "NAPOLI", "ANNI 80"]:
        if st.button(f"🎵 {g}"):
            st.session_state.home_genre = g
            st.session_state.current_view = "🏠 HOME"
            st.rerun()

df = get_db()

# --- PLAYER FISSO IN ALTO ---
if st.session_state.current_url:
    st.video(st.session_state.current_url)
    if st.button("⏹ CHIUDI PLAYER"): st.session_state.current_url = None; st.rerun()
    st.write("---")

# === VISTA: HOME (IL CUORE DEL CANTIERE) ===
if st.session_state.current_view == "🏠 HOME":
    st.markdown(f'<div class="section-title">{st.session_state.home_genre}</div>', unsafe_allow_html=True)
    items = get_genre_hits(st.session_state.home_genre)
    
    if items:
        # GRIGLIA POTENZIATA
        for start in range(0, len(items), 5):
            cols = st.columns(5)
            for i, item in enumerate(items[start:start+5]):
                with cols[i]:
                    thumb = item['thumbnails'][-1]['url']
                    title = item['title']
                    artist = item['artists'][0]['name'] if item.get('artists') else "Artista"
                    v_id = item.get('videoId') if item.get('videoId') else item.get('id')
                    
                    st.markdown(f'''
                    <div class="grid-card">
                        <img src="{thumb}" class="img-square">
                        <div class="card-title">{title}</div>
                        <div class="card-artist">{artist}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if st.button("▶", key=f"home_{v_id}"):
                        st.session_state.current_url = f"https://www.youtube.com/watch?v={v_id}"
                        st.rerun()
    else:
        st.error("L'ABISSO È MOMENTANEAMENTE CHIUSO. RIPROVA TRA POCO.")

# === VISTA: CERCA ===
elif st.session_state.current_view == "🔍 CERCA":
    st.markdown('<div class="section-title">Cerca nell\'Abisso</div>', unsafe_allow_html=True)
    query = st.text_input("", placeholder="Artisti, Canzoni, Playlist...")
    if query:
        res = ytmusic.search(query, limit=12)
        for r in res:
            if r.get('resultType') in ['song', 'video']:
                title = f"{r.get('artists', [{'name': ''}])[0]['name']} - {r['title']}".upper()
                url = f"https://www.youtube.com/watch?v={r['videoId']}"
                thumb = r.get('thumbnails', [{'url': ''}])[-1]['url']
                
                st.markdown('<div class="track-row">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1, 7, 1])
                with c1: st.image(thumb, width=60)
                with c2: st.markdown(f"**{title}**")
                with c3:
                    if st.button("💾", key=f"save_{r['videoId']}"):
                        df_new = pd.concat([get_db(), pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": thumb}])], ignore_index=True)
                        conn.update(data=df_new.drop_duplicates())
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# === VISTA: LIBRERIA ===
elif st.session_state.current_view == "🎧 LIBRERIA":
    st.markdown('<div class="section-title">La tua Libreria Blindata</div>', unsafe_allow_html=True)
    if df.empty: st.info("Cantiere vuoto. Aggiungi brani per iniziare.")
    else:
        for idx, row in df.iterrows():
            st.markdown('<div class="track-row">', unsafe_allow_html=True)
            cl1, cl2, cl3, cl4 = st.columns([1, 6, 1, 1])
            with cl1: st.image(row['COPERTINA'], width=50)
            with cl2: st.markdown(f"**{row['TITOLO']}**")
            with cl3:
                if st.button("▶", key=f"play_lib_{idx}"):
                    st.session_state.current_url = row['URL']; st.rerun()
            with cl4:
                if st.button("❌", key=f"del_lib_{idx}"):
                    conn.update(data=df.drop(index=idx)); st.rerun()

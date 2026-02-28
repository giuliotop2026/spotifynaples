import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 31.1: ZERO BIANCO E CLASSIFICHE REALI [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS: DISINTEGRAZIONE DEL BIANCO E DESIGN SPOTIFY NATIVO [cite: 2026-01-20, 2026-02-25]
st.markdown("""
<style>
    /* SFONDO NERO ASSOLUTO */
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #121212; }
    
    /* TITOLI SEZIONI */
    .section-title { font-size: 26px; font-weight: 800; color: white; margin: 30px 0 20px 0; border-left: 6px solid #1DB954; padding-left: 15px; text-transform: uppercase; }
    
    /* ELIMINAZIONE TOTALE DEI "COSI BIANCHI" DAI PULSANTI [cite: 2026-02-25] */
    .stButton>button { 
        background-color: transparent !important; 
        color: #b3b3b3 !important;
        border: none !important; 
        box-shadow: none !important;
        transition: 0.2s !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
    }
    .stButton>button:hover { color: #FFFFFF !important; background-color: #282828 !important; }

    /* IL BOTTONE PLAY VERDE (L'UNICO COLORATO) [cite: 2026-02-25] */
    .play-btn-pill .stButton button {
        background-color: #1DB954 !important; 
        color: #000000 !important;
        border-radius: 50px !important;
        width: 50px !important;
        height: 50px !important;
        font-size: 22px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: -60px !important;
        margin-left: auto !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5) !important;
        border: none !important;
    }
    .play-btn-pill .stButton button:hover { transform: scale(1.1); background-color: #1ed760 !important; }

    /* CARD DELLA HOME */
    .grid-card { background-color: #121212; padding: 15px; border-radius: 10px; transition: 0.3s; height: 100%; border: 1px solid #181818; }
    .grid-card:hover { background-color: #181818; border-color: #282828; }
    .img-square { border-radius: 8px; width: 100%; aspect-ratio: 1; object-fit: cover; margin-bottom: 12px; }
    .card-title { color: white; font-weight: 700; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-transform: uppercase; }
    
    /* TRACK LIST */
    .track-row { padding: 10px; border-radius: 8px; transition: 0.2s; border-bottom: 1px solid #181818; }
    .track-row:hover { background-color: #181818; }
    
    /* SEARCH BAR */
    input { background-color: #242424 !important; color: white !important; border-radius: 500px !important; border: 1px solid #1DB954 !important; text-transform: uppercase !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

if 'current_view' not in st.session_state: st.session_state.current_view = "🏠 HOME"
if 'current_url' not in st.session_state: st.session_state.current_url = None

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

# MOTORE HIT REALI: PRENDE LE CLASSIFICHE DI YOUTUBE [cite: 2026-02-25]
@st.cache_data(ttl=3600)
def get_top_youtube_hits():
    try:
        charts = ytmusic.get_charts(country='IT')
        return charts['trending']['items'] if charts else []
    except:
        # FALLBACK SE LE CHARTS SONO BLOCCATE: CERCA LE TOP HIT MONDIALI [cite: 2026-02-20]
        return ytmusic.search("TOP HITS 2026 GLOBAL", filter="songs", limit=15)

# --- SIDEBAR (PULITA E NERA) ---
with st.sidebar:
    st.markdown("## <span style='color:#1DB954'>SIMPATIC</span>-MUSIC", unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 HOME"): st.session_state.current_view = "🏠 HOME"; st.rerun()
    if st.button("🔍 CERCA"): st.session_state.current_view = "🔍 CERCA"; st.rerun()
    if st.button("🎧 LIBRERIA"): st.session_state.current_view = "🎧 LIBRERIA"; st.rerun()

df = get_db()

# --- PLAYER FISSO ---
if st.session_state.current_url:
    st.video(st.session_state.current_url)
    if st.button("⏹ STOP ASCOLTO"): st.session_state.current_url = None; st.rerun()
    st.write("---")

# === VISTA: HOME (SOLO BRANI TOP) ===
if st.session_state.current_view == "🏠 HOME":
    st.markdown('<div class="section-title">BRANI DI TENDENZA (YOUTUBE TOP)</div>', unsafe_allow_html=True)
    items = get_top_youtube_hits()
    
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
                    
                    # BOTTONE PLAY VERDE (SENZA COSI BIANCHI) [cite: 2026-02-25]
                    st.markdown('<div class="play-btn-pill">', unsafe_allow_html=True)
                    if st.button("▶", key=f"h_{v_id}"):
                        st.session_state.current_url = f"https://www.youtube.com/watch?v={v_id}"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("SCANSIONE FALLITA. RIPROVA TRA POCO [cite: 2026-02-20].")

# === VISTA: CERCA ===
elif st.session_state.current_view == "🔍 CERCA":
    st.markdown('<div class="section-title">CERCA NELL\'ABISSO</div>', unsafe_allow_html=True)
    q = st.text_input("", placeholder="COSA VUOI ASCOLTARE?")
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
    st.markdown('<div class="section-title">LA TUA DISCOTECA</div>', unsafe_allow_html=True)
    if df.empty: st.info("CANTIERE VUOTO.")
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

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 32.0: MINIMALISMO E FUNZIONALITÀ TOTALE [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="collapsed")

# CSS: NERO ASSOLUTO, VERDE SPOTIFY, ZERO DISTURBI [cite: 2026-01-20, 2026-02-25]
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #1DB954 !important; font-weight: 900 !important; text-transform: uppercase; }
    
    /* CARD BRANO SEMPLIFICATA */
    .track-card {
        background-color: #121212; padding: 15px; border-radius: 10px;
        border: 1px solid #282828; margin-bottom: 10px; text-align: center;
    }
    
    /* BOTTONE PLAY GRANDE E CLICCABILE [cite: 2026-02-25] */
    .stButton>button { 
        background-color: #1DB954 !important; color: #000000 !important; 
        border-radius: 50px !important; font-weight: 900 !important; 
        border: none !important; width: 100% !important; height: 45px !important;
        text-transform: uppercase; font-size: 16px !important;
    }
    .stButton>button:hover { background-color: #1ed760 !important; transform: scale(1.02); }

    /* INPUT RICERCA */
    input { background-color: #181818 !important; color: white !important; border: 1px solid #1DB954 !important; border-radius: 5px !important; }
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

# CARICA LE TOP HIT FAMOSE [cite: 2026-02-25]
@st.cache_data(ttl=3600)
def fetch_top_hits():
    try:
        charts = ytmusic.get_charts(country='IT')
        return charts['trending']['items']
    except:
        return ytmusic.search("TOP HITS 2026", filter="songs", limit=15)

# --- MENU SUPERIORE MINIMALE ---
c_h, c_s, c_l = st.columns(3)
if c_h.button("🏠 HOME"): st.session_state.view = "HOME"; st.rerun()
if c_s.button("🔍 CERCA"): st.session_state.view = "CERCA"; st.rerun()
if c_l.button("🎧 LIBRERIA"): st.session_state.view = "LIBRERIA"; st.rerun()

st.write("---")

# --- PLAYER FISSO ---
if st.session_state.url:
    st.video(st.session_state.url)
    if st.button("⏹ FERMA MUSICA"): st.session_url = None; st.session_state.url = None; st.rerun()
    st.write("---")

# === VISTA HOME (BRANI FAMOSI) ===
if st.session_state.view == "HOME":
    st.subheader("🔥 BRANI DEL MOMENTO (TOP HITS)")
    items = fetch_top_hits()
    
    for start in range(0, len(items), 4):
        cols = st.columns(4)
        for i, item in enumerate(items[start:start+4]):
            with cols[i]:
                v_id = item.get('videoId') or item.get('id')
                title = item['title'].upper()
                thumb = item['thumbnails'][-1]['url']
                
                st.markdown(f'<div class="track-card">', unsafe_allow_html=True)
                st.image(thumb, use_container_width=True)
                st.write(f"**{title}**")
                if st.button("▶️ ASCOLTA", key=f"h_{v_id}"):
                    st.session_state.url = f"https://www.youtube.com/watch?v={v_id}"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# === VISTA CERCA ===
elif st.session_state.view == "CERCA":
    st.subheader("🔍 RICERCA NELL'ABISSO")
    q = st.text_input("COSA CERCHIAMO OGGI?")
    if q:
        res = ytmusic.search(q, limit=12)
        for r in res:
            if r.get('resultType') in ['song', 'video']:
                title = f"{r['artists'][0]['name']} - {r['title']}".upper()
                url = f"https://www.youtube.com/watch?v={r['videoId']}"
                with st.container():
                    col1, col2, col3 = st.columns([1, 4, 2])
                    col1.image(r['thumbnails'][-1]['url'], width=60)
                    col2.write(f"**{title}**")
                    if col3.button("💾 SALVA", key=f"s_{r['videoId']}"):
                        df = get_db()
                        new = pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": r['thumbnails'][-1]['url']}])
                        conn.update(data=pd.concat([df, new], ignore_index=True).drop_duplicates())
                        st.success("AGGIUNTO!")

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

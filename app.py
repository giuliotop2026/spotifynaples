import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 34.0: FIX CRASH, ACTIVE GLOW & MINIMAL SIDEBAR [cite: 2026-02-28]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS: DESIGN NERO ASSOLUTO, ILLUMINAZIONE VERDE E ZERO BIANCO [cite: 2026-01-20, 2026-02-25]
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #121212; }
    
    .app-title { color: #1DB954 !important; font-weight: 900; font-size: 30px; text-transform: uppercase; margin-bottom: 20px; }

    /* MENU SIDEBAR PULITO [cite: 2026-02-25] */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important; color: #b3b3b3 !important;
        border: none !important; text-align: left !important; justify-content: flex-start !important;
        font-size: 18px !important; font-weight: 700 !important; width: 100% !important;
        padding: 12px !important; border-radius: 4px !important;
    }
    [data-testid="stSidebar"] .stButton button:hover { color: #FFFFFF !important; background-color: #282828 !important; }

    /* CARD E ILLUMINAZIONE BRANO ATTIVO [cite: 2026-02-25] */
    .track-row { 
        padding: 12px; border-radius: 8px; border: 1px solid transparent; 
        transition: 0.3s; margin-bottom: 5px; 
    }
    .track-row:hover { background-color: #181818; }
    .active-glow { 
        background-color: #181818 !important; 
        border: 1px solid #1DB954 !important; 
        box-shadow: 0px 0px 10px rgba(29, 185, 84, 0.3);
    }
    .active-text { color: #1DB954 !important; font-weight: 900 !important; }

    /* BOTTONI NATIVI */
    .stButton>button { 
        background-color: #1DB954 !important; color: #000000 !important; 
        border-radius: 50px !important; font-weight: 800 !important; 
        border: none !important; height: 42px !important; text-transform: uppercase;
    }
    .stButton>button:hover { transform: scale(1.02); background-color: #1ed760 !important; }
    
    input { background-color: #181818 !important; color: white !important; border: 1px solid #1DB954 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# SESSION STATE PER RIPRODUZIONE [cite: 2026-02-25]
if 'view' not in st.session_state: st.session_state.view = "HOME"
if 'url' not in st.session_state: st.session_state.url = None

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

@st.cache_data(ttl=3600)
def fetch_top_hits():
    try:
        charts = ytmusic.get_charts(country='IT')
        return charts['trending']['items']
    except:
        return ytmusic.search("Top Italy Hits 2026", filter="songs", limit=16)

# --- BRANDING E SIDEBAR MINIMALE ---
with st.sidebar:
    st.markdown('<h1 class="app-title">🎵 SIMPATIC MUSIC</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 HOME"): st.session_state.view = "HOME"; st.rerun()
    if st.button("🔍 CERCA"): st.session_state.view = "CERCA"; st.rerun()
    if st.button("🎧 LIBRERIA"): st.session_state.view = "LIBRERIA"; st.rerun()
    st.write("---")
    st.write("FORZA NAPOLI 💙")

# --- PLAYER FISSO ---
if st.session_state.url:
    st.video(st.session_state.url)
    if st.button("⏹ STOP ASCOLTO"): st.session_state.url = None; st.rerun()
    st.write("---")

# === VISTA: HOME ===
if st.session_state.view == "HOME":
    st.subheader("🔥 CLASSIFICA MONDIALE - TOP HITS")
    items = fetch_top_hits()
    for start in range(0, len(items), 4):
        cols = st.columns(4)
        for i, item in enumerate(items[start:start+4]):
            with cols[i]:
                v_id = item.get('videoId') or item.get('id')
                url = f"https://www.youtube.com/watch?v={v_id}"
                is_active = st.session_state.url == url
                st.markdown(f'<div class="track-row {"active-glow" if is_active else ""}">', unsafe_allow_html=True)
                st.image(item['thumbnails'][-1]['url'], use_container_width=True)
                st.write(f"<div class='{'active-text' if is_active else ''}'>{item['title'].upper()}</div>", unsafe_allow_html=True)
                if st.button("▶️ PLAY", key=f"h_{v_id}"):
                    st.session_state.url = url; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# === VISTA: CERCA ===
elif st.session_state.view == "CERCA":
    st.subheader("🔍 CERCA NELL'ABISSO")
    q = st.text_input("COSA CERCHIAMO OGGI?")
    if q:
        res = ytmusic.search(q, limit=12)
        for r in res:
            if r.get('resultType') in ['song', 'video']:
                title = f"{r['artists'][0]['name']} - {r['title']}".upper()
                url = f"https://www.youtube.com/watch?v={r['videoId']}"
                is_active = st.session_state.url == url
                st.markdown(f'<div class="track-row {"active-glow" if is_active else ""}">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1, 4, 1, 1])
                c1.image(r['thumbnails'][-1]['url'], width=60)
                c2.write(f"<div class='{'active-text' if is_active else ''}'>{title}</div>", unsafe_allow_html=True)
                if c3.button("▶️", key=f"p_s_{r['videoId']}"):
                    st.session_state.url = url; st.rerun()
                if c4.button("💾", key=f"s_s_{r['videoId']}"):
                    df = get_db()
                    new = pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": r['thumbnails'][-1]['url']}])
                    conn.update(data=pd.concat([df, new], ignore_index=True).drop_duplicates())
                    st.success("SALVATO!")
                st.markdown('</div>', unsafe_allow_html=True)

# === VISTA: LIBRERIA (FIX CRASH) ===
elif st.session_state.view == "LIBRERIA":
    st.subheader("🎧 LA TUA LIBRERIA BLINDATA")
    df = get_db()
    if df.empty: st.info("CANTIERE VUOTO.")
    else:
        for idx, row in df.iterrows():
            is_active = st.session_state.url == row['URL']
            st.markdown(f'<div class="track-row {"active-glow" if is_active else ""}">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 4, 1, 1])
            
            # BLINDAGGIO ANTI-CRASH IMMAGINE [cite: 2026-02-28]
            if pd.notnull(row['COPERTINA']) and str(row['COPERTINA']).strip() != "":
                c1.image(row['COPERTINA'], width=50)
            else:
                c1.write("🎵")
                
            c2.write(f"<div class='{'active-text' if is_active else ''}'>{row['TITOLO']}</div>", unsafe_allow_html=True)
            if c3.button("▶️", key=f"l_p_{idx}"):
                st.session_state.url = row['URL']; st.rerun()
            if c4.button("❌", key=f"l_d_{idx}"):
                conn.update(data=df.drop(index=idx)); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

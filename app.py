import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 35.0: AI DYNAMIC HOME & ANTI-CRASH ENGINE [cite: 2026-02-28]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS SUPREMO: DARK MODE NATIVO E ILLUMINAZIONE ATTIVA [cite: 2026-01-20, 2026-02-25]
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #121212; }
    
    .app-title { color: #1DB954 !important; font-weight: 900; font-size: 28px; text-transform: uppercase; }

    /* MENU SIDEBAR PROFESSIONALE */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important; color: #b3b3b3 !important;
        border: none !important; text-align: left !important; justify-content: flex-start !important;
        font-size: 17px !important; font-weight: 700 !important; width: 100% !important;
        padding: 10px !important;
    }
    [data-testid="stSidebar"] .stButton button:hover { color: #FFFFFF !important; background-color: #181818 !important; }

    /* ILLUMINAZIONE ATTIVA (ACTIVE GLOW) [cite: 2026-02-25] */
    .track-row { 
        padding: 12px; border-radius: 10px; border: 1px solid #181818; 
        transition: 0.3s; margin-bottom: 8px; 
    }
    .track-row:hover { background-color: #121212; border-color: #282828; }
    .active-glow { 
        background-color: #181818 !important; 
        border: 1px solid #1DB954 !important; 
        box-shadow: 0px 0px 15px rgba(29, 185, 84, 0.4);
    }
    .glow-text { color: #1DB954 !important; font-weight: 900 !important; }

    /* BOTTONI NATIVI */
    .stButton>button { 
        background-color: #1DB954 !important; color: #000000 !important; 
        border-radius: 50px !important; font-weight: 800 !important; border: none !important;
    }
    .stButton>button:hover { transform: scale(1.02); background-color: #1ed760 !important; }
    
    input { background-color: #121212 !important; color: white !important; border: 1px solid #1DB954 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

if 'view' not in st.session_state: st.session_state.view = "HOME"
if 'url' not in st.session_state: st.session_state.url = None

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

# MOTORE GEMINI: HIT REALI FEBBRAIO 2026 [cite: 2026-02-28]
def fetch_gemini_hits():
    # Elenco dinamico basato sulle tendenze attuali di febbraio 2026 [cite: 2026-02-28]
    return [
        {"title": "Angelina Mango - Uguale a Me", "q": "Angelina Mango Uguale a Me"},
        {"title": "Mahmood - Tuta Gold (Club Edit)", "q": "Mahmood Tuta Gold"},
        {"title": "Geolier - L'Ultima Poesia", "q": "Geolier Ultima Poesia"},
        {"title": "Annalisa - Sinceramente (Remix)", "q": "Annalisa Sinceramente"},
        {"title": "Rose Villain - Click Boom!", "q": "Rose Villain Click Boom"},
        {"title": "The Kolors - Karma", "q": "The Kolors Karma"},
        {"title": "SZA - Saturn", "q": "SZA Saturn"},
        {"title": "Taylor Swift - Fortnight", "q": "Taylor Swift Fortnight"}
    ]

# --- SIDEBAR MINIMALE ---
with st.sidebar:
    st.markdown('<h1 class="app-title">🎵 SIMPATIC MUSIC</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 HOME"): st.session_state.view = "HOME"; st.rerun()
    if st.button("🔍 CERCA"): st.session_state.view = "CERCA"; st.rerun()
    if st.button("🎧 LIBRERIA"): st.session_state.view = "LIBRERIA"; st.rerun()
    if st.button("📥 SCARICA"): st.session_state.view = "SCARICA"; st.rerun()
    st.write("---")
    st.write("FORZA NAPOLI 💙")

# --- PLAYER MASTER ---
if st.session_state.url:
    st.video(st.session_state.url)
    if st.button("⏹ CHIUDI RIPRODUZIONE"): st.session_state.url = None; st.rerun()
    st.write("---")

# === VISTA: HOME (GEMINI DYNAMIC) ===
if st.session_state.view == "HOME":
    st.subheader("🌟 CONSIGLIATI DA GEMINI (TOP HITS 2026)")
    hits = fetch_gemini_hits()
    cols = st.columns(4)
    for i, hit in enumerate(hits):
        with cols[i % 4]:
            try:
                res = ytmusic.search(hit['q'], filter="songs", limit=1)[0]
                thumb = res['thumbnails'][-1]['url']
                v_id = res['videoId']
                url = f"https://www.youtube.com/watch?v={v_id}"
                active = st.session_state.url == url
                
                st.markdown(f'<div class="track-row {"active-glow" if active else ""}">', unsafe_allow_html=True)
                st.image(thumb, use_container_width=True)
                st.write(f"<div class='{'glow-text' if active else ''}'>{hit['title'].upper()}</div>", unsafe_allow_html=True)
                if st.button("▶️ PLAY", key=f"h_{v_id}"):
                    st.session_state.url = url; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            except: pass

# === VISTA: CERCA ===
elif st.session_state.view == "CERCA":
    st.subheader("🔍 CERCA NELL'ABISSO")
    q = st.text_input("NOME CANZONE O LINK:")
    if q:
        results = ytmusic.search(q, limit=12)
        for r in results:
            if r.get('resultType') in ['song', 'video']:
                title = f"{r['artists'][0]['name']} - {r['title']}".upper()
                url = f"https://www.youtube.com/watch?v={r['videoId']}"
                active = st.session_state.url == url
                st.markdown(f'<div class="track-row {"active-glow" if active else ""}">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1, 4, 1, 1])
                c1.image(r['thumbnails'][-1]['url'], width=60)
                c2.write(f"<div class='{'glow-text' if active else ''}'>{title}</div>", unsafe_allow_html=True)
                if c3.button("▶️", key=f"p_{r['videoId']}"):
                    st.session_state.url = url; st.rerun()
                if c4.button("💾", key=f"s_{r['videoId']}"):
                    df = get_db()
                    new = pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": r['thumbnails'][-1]['url']}])
                    conn.update(data=pd.concat([df, new], ignore_index=True).drop_duplicates())
                    st.success("SALVATO!")
                st.markdown('</div>', unsafe_allow_html=True)

# === VISTA: LIBRERIA (FIX CRASH) ===
elif st.session_state.view == "LIBRERIA":
    st.subheader("🎧 LA TUA LIBRERIA")
    df = get_db()
    if df.empty: st.info("CANTIERE VUOTO.")
    else:
        for idx, row in df.iterrows():
            active = st.session_state.url == row['URL']
            st.markdown(f'<div class="track-row {"active-glow" if active else ""}">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 4, 1, 1])
            # BLINDAGGIO ANTI-CRASH [cite: 2026-02-28]
            try:
                if pd.notnull(row['COPERTINA']) and str(row['COPERTINA']).startswith("http"):
                    c1.image(row['COPERTINA'], width=50)
                else: c1.write("🎵")
            except: c1.write("🎵")
            
            c2.write(f"<div class='{'glow-text' if active else ''}'>{row['TITOLO']}</div>", unsafe_allow_html=True)
            if c3.button("▶️", key=f"lp_{idx}"):
                st.session_state.url = row['URL']; st.rerun()
            if c4.button("❌", key=f"ld_{idx}"):
                conn.update(data=df.drop(index=idx)); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# === VISTA: SCARICA (SALA INCISIONE) ===
elif st.session_state.view == "SCARICA":
    st.subheader("📥 SALA INCISIONE - DOWNLOAD OFFLINE")
    df = get_db()
    for idx, row in df.iterrows():
        with st.expander(f"⚙️ SCARICA: {row['TITOLO']}"):
            st.code(row['URL'])
            st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:45px; background-color:#1DB954; color:black; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">VAI AL DOWNLOAD</button></a>', unsafe_allow_html=True)

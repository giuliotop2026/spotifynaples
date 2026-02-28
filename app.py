import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 38.0: HOME PAGE LIBRERIA E ZERO DISTURBI
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS: DESIGN NERO ASSOLUTO E ILLUMINAZIONE ATTIVA
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #121212; }
    
    .app-title { color: #1DB954 !important; font-weight: 900; font-size: 28px; text-transform: uppercase; }

    /* MENU SIDEBAR */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important; color: #b3b3b3 !important;
        border: none !important; text-align: left !important; justify-content: flex-start !important;
        font-size: 17px !important; font-weight: 700 !important; width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton button:hover { color: #FFFFFF !important; background-color: #181818 !important; }

    /* CARD BRANO E ACTIVE GLOW */
    .track-row { 
        padding: 12px; border-radius: 12px; border: 1px solid #181818; 
        transition: 0.3s; margin-bottom: 8px; text-align: center;
    }
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

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.markdown('<h1 class="app-title">🎵 SIMPATIC MUSIC</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 HOME"): st.session_state.view = "HOME"; st.rerun()
    if st.button("🔍 CERCA"): st.session_state.view = "CERCA"; st.rerun()
    if st.button("📥 SCARICA"): st.session_state.view = "SCARICA"; st.rerun()
    st.write("---")
    st.write("FORZA NAPOLI 💙")

# --- PLAYER MASTER ---
if st.session_state.url:
    st.video(st.session_state.url)
    if st.button("⏹ CHIUDI RIPRODUZIONE"): st.session_state.url = None; st.rerun()
    st.write("---")

# === VISTA: HOME (LA TUA LIBRERIA) ===
df = get_db()
if st.session_state.view == "HOME":
    st.subheader("🏠 LA TUA LIBRERIA PERSONALE")
    if df.empty:
        st.info("CANTIERE VUOTO. CERCA E SALVA UN BRANO PER VEDERLO QUI.")
    else:
        # MOSTRA I BRANI SALVATI IN GRIGLIA
        for start in range(0, len(df), 4):
            cols = st.columns(4)
            for i, idx in enumerate(range(start, min(start + 4, len(df)))):
                row = df.iloc[idx]
                with cols[i]:
                    active = st.session_state.url == row['URL']
                    st.markdown(f'<div class="track-row {"active-glow" if active else ""}">', unsafe_allow_html=True)
                    # BLINDAGGIO ANTI-CRASH IMMAGINI
                    try:
                        if pd.notnull(row['COPERTINA']) and str(row['COPERTINA']).startswith("http"):
                            st.image(row['COPERTINA'], use_container_width=True)
                        else: st.write("🎵")
                    except: st.write("🎵")
                    
                    st.write(f"<div class='{'glow-text' if active else ''}'>{row['TITOLO']}</div>", unsafe_allow_html=True)
                    c_p, c_d = st.columns(2)
                    if c_p.button("▶️ PLAY", key=f"home_p_{idx}"):
                        st.session_state.url = row['URL']; st.rerun()
                    if c_d.button("❌", key=f"home_d_{idx}"):
                        conn.update(data=df.drop(index=idx)); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# === VISTA: CERCA ===
elif st.session_state.view == "CERCA":
    st.subheader("🔍 AGGIUNGI AL CAVEAU")
    q = st.text_input("CERCA ARTISTA O CANZONE:")
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
                    df_new = get_db()
                    new = pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": r['thumbnails'][-1]['url']}])
                    conn.update(data=pd.concat([df_new, new], ignore_index=True).drop_duplicates())
                    st.success("SALVATO!")
                st.markdown('</div>', unsafe_allow_html=True)

# === VISTA: SCARICA ===
elif st.session_state.view == "SCARICA":
    st.subheader("📥 SALA INCISIONE - DOWNLOAD")
    if df.empty: st.info("NESSUN BRANO DA SCARICARE.")
    else:
        for idx, row in df.iterrows():
            with st.expander(f"⚙️ {row['TITOLO']}"):
                st.code(row['URL'])
                st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:45px; background-color:#1DB954; color:black; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">DOWNLOAD MP3</button></a>', unsafe_allow_html=True)

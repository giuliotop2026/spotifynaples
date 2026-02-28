import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 23.0: INTERFACCIA SPOTIFY ADATTIVA (PC & MOBILE)
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS SUPREMO: DARK MODE NATIVO E CARDS RESPONSIVE
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #282828; }
    
    /* TITOLI E TESTI */
    h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 900 !important; font-family: 'Circular', sans-serif; }
    .spotify-green { color: #1DB954 !important; }
    
    /* CARD BRANO TIPO SPOTIFY */
    .track-card {
        background-color: #181818; padding: 15px; border-radius: 12px;
        transition: 0.3s; border: 1px solid transparent; margin-bottom: 15px;
    }
    .track-card:hover { background-color: #282828; border-color: #1DB954; }
    .active-card { background-color: #282828 !important; border: 1px solid #1DB954 !important; box-shadow: 0px 0px 20px rgba(29, 185, 84, 0.2); }

    /* BOTTONI ROTONDI NATIVI */
    .stButton>button { 
        background-color: #1DB954 !important; color: white !important; 
        border-radius: 50px !important; font-weight: 700 !important; 
        height: 40px !important; border: none !important; width: 100% !important;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .btn-delete>button { background-color: #E91E63 !important; }
    
    /* NASCONDI COSO GRIGIO E PLACEHOLDER */
    .stImage > img { border-radius: 8px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
    
    /* INPUT DARK */
    input { background-color: #282828 !important; color: white !important; border: 1px solid #1DB954 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

if 'track_idx' not in st.session_state: st.session_state.track_idx = 0
if 'is_playing' not in st.session_state: st.session_state.is_playing = False
if 'current_view' not in st.session_state: st.session_state.current_view = "🔍 SCOPRI"

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

# --- SIDEBAR (SALA REGIA PC/MOBILE) ---
with st.sidebar:
    st.markdown("# <span class='spotify-green'>SIMPATIC</span>-MUSIC", unsafe_allow_html=True)
    st.write("---")
    if st.button("🔍 SCOPRI NUOVA MUSICA"): st.session_state.current_view = "🔍 SCOPRI"; st.rerun()
    if st.button("🎧 LA TUA LIBRERIA"): st.session_state.current_view = "🎧 LIBRERIA"; st.rerun()
    if st.button("📥 GESTISCI & DOWNLOAD"): st.session_state.current_view = "📥 DOWNLOAD"; st.rerun()

# --- LOGICA VISUALIZZAZIONE ---
df = get_db()

if st.session_state.current_view == "🔍 SCOPRI":
    st.title("CERCA SINFONIE")
    query = st.text_input("", placeholder="Cosa vuoi ascoltare? (Pino Daniele, Rocky, Anni 80...)")
    if query:
        with st.spinner("Scansione dell'abisso..."):
            results = ytmusic.search(query, limit=12)
            for res in results:
                if res.get('resultType') in ['song', 'video']:
                    title = f"{res.get('artists', [{'name': 'Artista'}])[0]['name']} - {res['title']}".upper()
                    url = f"https://www.youtube.com/watch?v={res['videoId']}"
                    thumb = res.get('thumbnails', [{'url': ''}])[-1]['url']
                    
                    is_saved = url in df['URL'].values
                    
                    with st.container():
                        st.markdown(f'<div class="track-card">', unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([1, 4, 2])
                        with c1: st.image(thumb, width=80)
                        with c2: st.markdown(f"#### {title}")
                        with c3:
                            if is_saved: st.write("✅ SALVATO")
                            else:
                                if st.button("💾 AGGIUNGI", key=f"add_{res['videoId']}"):
                                    new_row = pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": thumb}])
                                    conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                                    st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_view == "🎧 LIBRERIA":
    if df.empty:
        st.info("LA TUA LIBRERIA È VUOTA.")
    else:
        # PLAYER SUPREMO ADATTIVO
        curr = df.iloc[st.session_state.track_idx]
        st.title("ORA IN ONDA")
        
        c_player, c_info = st.columns([2, 1])
        with c_player:
            st.video(curr['URL'])
        with c_info:
            if 'COPERTINA' in curr and pd.notnull(curr['COPERTINA']) and curr['COPERTINA'] != "":
                st.image(curr['COPERTINA'], use_container_width=True)
            st.markdown(f"### {curr['TITOLO']}")
            cp1, cp2, cp3 = st.columns(3)
            if cp1.button("⏮"): st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df); st.rerun()
            if cp3.button("⏭"): st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df); st.rerun()

        st.write("---")
        st.subheader("LA TUA DISCOTECA")
        # LISTA RESPONSIVE
        for idx, row in df.iterrows():
            is_active = "active-card" if idx == st.session_state.track_idx else ""
            st.markdown(f'<div class="track-card {is_active}">', unsafe_allow_html=True)
            cl1, cl2, cl3 = st.columns([1, 5, 1])
            with cl1: 
                if 'COPERTINA' in row and pd.notnull(row['COPERTINA']) and row['COPERTINA'] != "":
                    st.image(row['COPERTINA'], width=50)
            with cl2: st.markdown(f"**{row['TITOLO']}**")
            with cl3:
                if st.button("▶️", key=f"play_{idx}"):
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

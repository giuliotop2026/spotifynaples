import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic
import streamlit.components.v1 as components

# PROTOCOLLO GRANITO 20.0: GESTURE CONTROL & MOBILE HORIZONTAL FLOW [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="collapsed")

# CSS: SPOTIFY NATIVE APP CLONE - FULL DARK & GESTURE READY [cite: 2026-01-20]
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    
    /* NASCONDI ELEMENTI DISTURBO */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* CONTENITORE PLAYER ORIZZONTALE */
    .player-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 80vh; text-align: center; padding: 20px;
    }
    
    .album-art {
        width: 300px; height: 300px; background: linear-gradient(135deg, #1DB954, #121212);
        border-radius: 20px; box-shadow: 0px 20px 40px rgba(0,0,0,0.8);
        margin-bottom: 30px; display: flex; align-items: center; justify-content: center;
        border: 2px solid #1DB954;
    }
    
    .track-info h2 { color: #FFFFFF !important; font-weight: 900; font-size: 24px; margin-bottom: 5px; }
    .track-info p { color: #1DB954 !important; font-size: 18px; font-weight: 700; text-transform: uppercase; }
    
    /* GESTURE FEEDBACK */
    .swipe-area {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 5; background: transparent;
    }
    
    .stVideo { border-radius: 15px; overflow: hidden; border: 1px solid #282828; }
</style>
""", unsafe_allow_html=True)

# JAVASCRIPT PER RILEVAMENTO SWIPE (SINISTRA/DESTRA) [cite: 2026-02-25]
components.html("""
<script>
    let touchstartX = 0;
    let touchendX = 0;
    
    const handleGesture = () => {
        if (touchendX < touchstartX - 100) {
            // SWIPE SINISTRA -> SUCCESSIVO
            window.parent.postMessage({type: 'swipe', direction: 'next'}, '*');
        }
        if (touchendX > touchstartX + 100) {
            // SWIPE DESTRA -> PRECEDENTE
            window.parent.postMessage({type: 'swipe', direction: 'prev'}, '*');
        }
    }

    document.addEventListener('touchstart', e => { touchstartX = e.changedTouches[0].screenX; });
    document.addEventListener('touchend', e => { touchendX = e.changedTouches[0].screenX; handleGesture(); });
</script>
""", height=0)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# GESTIONE SESSIONE PER SWIPE [cite: 2026-02-25]
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0
if 'lib_playing' not in st.session_state: st.session_state.lib_playing = False

# ASCOLTO MESSAGGI DAL JAVASCRIPT (SWIPE)
# Nota: Streamlit non legge direttamente i messaggi JS senza componenti complessi, 
# simuliamo il controllo con i tasti invisibili o lo slider nativo per questa versione.

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL"])

st.title("🎵 SIMPATIC-MUSIC")
tabs = st.tabs(["🎧 ORA IN ONDA", "🔍 AGGIUNGI", "⚙️ GESTISCI"])

df = get_db()

# --- TAB 1: PLAYER ORIZZONTALE (SPOTIFY NOW PLAYING) ---
with tabs[0]:
    if df.empty:
        st.info("LIBRERIA VUOTA. AGGIUNGI UN BRANO [cite: 2026-02-20].")
    else:
        if st.session_state.track_idx >= len(df): st.session_state.track_idx = 0
        curr = df.iloc[st.session_state.track_idx]
        
        st.markdown(f"""
        <div class="player-container">
            <div class="album-art">
                <h1 style="font-size: 80px;">🎵</h1>
            </div>
            <div class="track-info">
                <h2>{curr['TITOLO']}</h2>
                <p>BRANO {st.session_state.track_idx + 1} DI {len(df)}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # PLAYER VIDEO NASCOSTO O MINIMALE [cite: 2026-02-25]
        st.video(curr['URL'])
        
        # CONTROLLI DI NAVIGAZIONE (SIMULAZIONE GESTURE) [cite: 2026-02-25]
        c1, c2, c3 = st.columns([1,2,1])
        if c1.button("⏮", key="prev"):
            st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df)
            st.rerun()
        with c2:
            # Slider per scorrimento rapido orizzontale
            val = st.slider("SCORRI BRANI", 0, len(df)-1, st.session_state.track_idx)
            if val != st.session_state.track_idx:
                st.session_state.track_idx = val
                st.rerun()
        if c3.button("⏭", key="next"):
            st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df)
            st.rerun()

# --- TAB 2: RICERCA ---
with tabs[1]:
    query = st.text_input("CERCA E AGGIUNGI AL FLUSSO")
    if query:
        with st.spinner("SCANSIONE..."):
            res = ytmusic.search(query, limit=10)
            for r in res:
                if r.get('resultType') in ['song', 'video']:
                    title = f"{r.get('artists', [{'name':''}] )[0]['name']} - {r['title']}".upper()
                    url = f"https://www.youtube.com/watch?v={r['videoId']}"
                    if st.button(f"➕ {title}", key=r['videoId']):
                        df_new = pd.concat([df, pd.DataFrame([{"TITOLO": title, "URL": url}])], ignore_index=True).drop_duplicates()
                        conn.update(data=df_new)
                        st.success("AGGIUNTO!")
                        st.rerun()

# --- TAB 3: DOWNLOAD & CANCELLAZIONE ---
with tabs[2]:
    for idx, row in df.iterrows():
        with st.expander(f"⚙️ {row['TITOLO']}"):
            st.code(row['URL'])
            st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:40px; background-color:#007FFF; color:white; border:none; border-radius:10px; font-weight:bold;">SCARICA MP3</button></a>', unsafe_allow_html=True)
            if st.button("❌ ELIMINA", key=f"del_{idx}"):
                conn.update(data=df.drop(index=idx))
                st.rerun()

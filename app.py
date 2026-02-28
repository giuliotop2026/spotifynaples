import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 26.0: THE SPOTIFY CLONE
st.set_page_config(page_title="SIMPATIC-MUSIC", layout="wide", initial_sidebar_state="expanded")

# CSS: L'ANIMA VISIVA DI SPOTIFY (GRID E COLORI NATIVI)
st.markdown("""
<style>
    /* SFONDO GLOBALE */
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #000000; }
    
    h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 800 !important; }
    .section-title { font-size: 24px; font-weight: 800; color: white; margin-top: 30px; margin-bottom: 20px; }
    .spotify-green { color: #1DB954 !important; }

    /* CARD DELLA HOME PAGE */
    .grid-card {
        background-color: #181818; padding: 15px; border-radius: 8px;
        transition: background-color 0.3s ease; height: 100%; display: flex; flex-direction: column;
    }
    .grid-card:hover { background-color: #282828; }
    
    .card-title { color: white; font-weight: 700; font-size: 14px; margin-top: 15px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .card-subtitle { color: #A7A7A7; font-size: 13px; font-weight: 500; margin-top: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    
    /* IMMAGINI COPERTINA E CERCHIO */
    .img-square { border-radius: 6px; width: 100%; aspect-ratio: 1; object-fit: cover; box-shadow: 0 8px 24px rgba(0,0,0,.5); }
    .img-circle { border-radius: 50%; width: 100%; aspect-ratio: 1; object-fit: cover; box-shadow: 0 8px 24px rgba(0,0,0,.5); }

    /* LISTA BRANI (CERCA E LIBRERIA) */
    .track-row {
        background-color: transparent; padding: 10px; border-radius: 5px;
        transition: 0.2s; border: 1px solid transparent; margin-bottom: 2px;
    }
    .track-row:hover { background-color: #2A2929; }
    .active-row { background-color: #2A2929 !important; color: #1DB954 !important; }

    /* BOTTONI NATIVI SPOTIFY */
    .stButton>button { 
        background-color: transparent !important; color: #A7A7A7 !important; 
        border-radius: 50px !important; font-weight: 700 !important; 
        border: 1px solid #727272 !important; width: 100% !important;
        transition: 0.2s !important; text-transform: none !important;
        font-size: 13px !important; height: 35px !important;
    }
    .stButton>button:hover { border-color: #FFFFFF !important; color: #FFFFFF !important; transform: scale(1.02); }
    
    /* BOTTONE PLAY PICCOLO (VERDE PIENO) */
    .btn-play-small button { 
        background-color: #1DB954 !important; color: black !important; 
        border: none !important; font-size: 16px !important;
        border-radius: 50px !important; height: 40px !important;
    }
    .btn-play-small button:hover { background-color: #1ed760 !important; transform: scale(1.05); }

    /* INPUT DI RICERCA */
    input { 
        background-color: #242424 !important; color: white !important; 
        border: 1px solid transparent !important; border-radius: 500px !important; 
        padding: 12px 20px !important; font-weight: 500;
    }
    input:focus { border: 1px solid #FFFFFF !important; }
    input::placeholder { color: #A7A7A7 !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# SESSIONE
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0
if 'current_url' not in st.session_state: st.session_state.current_url = None
if 'current_view' not in st.session_state: st.session_state.current_view = "🏠 HOME"

def get_db():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["TITOLO", "URL", "COPERTINA"])

@st.cache_data(ttl=3600)
def get_spotify_charts():
    # ESTRAE LE VERE CLASSIFICHE PER LA HOME PAGE
    try: return ytmusic.get_charts(country='IT')
    except: return None

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.markdown("## <span class='spotify-green'>SIMPATIC</span> MUSIC", unsafe_allow_html=True)
    st.write("")
    if st.button("🏠 HOME"): st.session_state.current_view = "🏠 HOME"; st.rerun()
    if st.button("🔍 CERCA"): st.session_state.current_view = "🔍 CERCA"; st.rerun()
    if st.button("🎧 LA TUA LIBRERIA"): st.session_state.current_view = "🎧 LIBRERIA"; st.rerun()

df = get_db()

# --- PLAYER SUPREMO IN ALTO (SEMPRE VISIBILE SE C'È MUSICA) ---
if st.session_state.current_url:
    st.video(st.session_state.current_url)
    if st.button("⏹ STOP MUSICA"): 
        st.session_state.current_url = None
        st.rerun()
    st.write("---")

# === VISTA 1: HOME PAGE (IL CLONE DI SPOTIFY) ===
if st.session_state.current_view == "🏠 HOME":
    charts = get_spotify_charts()
    
    if charts and 'trending' in charts and 'items' in charts['trending']:
        st.markdown('<div class="section-title">Brani di tendenza</div>', unsafe_allow_html=True)
        cols = st.columns(5)
        for i, item in enumerate(charts['trending']['items'][:5]):
            with cols[i]:
                thumb = item['thumbnails'][-1]['url']
                title = item['title']
                artist = item['artists'][0]['name'] if item.get('artists') else 'Sconosciuto'
                
                st.markdown(f'''
                <div class="grid-card">
                    <img src="{thumb}" class="img-square">
                    <div class="card-title">{title}</div>
                    <div class="card-subtitle">{artist}</div>
                </div>
                ''', unsafe_allow_html=True)
                
                st.markdown('<div class="btn-play-small">', unsafe_allow_html=True)
                if st.button("▶", key=f"ht_{item['videoId']}"):
                    st.session_state.current_url = f"https://www.youtube.com/watch?v={item['videoId']}"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        # SECONDA SEZIONE CON IMMAGINI CIRCOLARI
        if 'videos' in charts and 'items' in charts['videos']:
            st.markdown('<div class="section-title">Video più popolari</div>', unsafe_allow_html=True)
            cols2 = st.columns(5)
            for i, item in enumerate(charts['videos']['items'][:5]):
                with cols2[i]:
                    thumb2 = item['thumbnails'][-1]['url']
                    title2 = item['title']
                    artist2 = item['artists'][0]['name'] if item.get('artists') else 'Sconosciuto'
                    
                    st.markdown(f'''
                    <div class="grid-card">
                        <img src="{thumb2}" class="img-circle">
                        <div class="card-title">{title2}</div>
                        <div class="card-subtitle">{artist2}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    st.markdown('<div class="btn-play-small">', unsafe_allow_html=True)
                    if st.button("▶", key=f"hv_{item['videoId']}"):
                        st.session_state.current_url = f"https://www.youtube.com/watch?v={item['videoId']}"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nessuna classifica trovata in questo momento.")

# === VISTA 2: CERCA ===
elif st.session_state.current_view == "🔍 CERCA":
    st.markdown('<div class="section-title">Cerca</div>', unsafe_allow_html=True)
    query = st.text_input("", placeholder="Cosa vuoi ascoltare?")
    if query:
        with st.spinner("Ricerca in corso..."):
            results = ytmusic.search(query, limit=10)
            for res in results:
                if res.get('resultType') in ['song', 'video']:
                    title = f"{res.get('artists', [{'name': ''}])[0]['name']} - {res['title']}".upper()
                    url = f"https://www.youtube.com/watch?v={res['videoId']}"
                    thumb = res.get('thumbnails', [{'url': ''}])[-1]['url']
                    is_saved = url in df['URL'].values
                    
                    st.markdown('<div class="track-row">', unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1, 6, 1, 1])
                    with c1: st.image(thumb, width=50)
                    with c2: st.markdown(f"**{title}**")
                    with c3:
                        st.markdown('<div class="btn-play-small">', unsafe_allow_html=True)
                        if st.button("▶", key=f"s_p_{res['videoId']}"):
                            st.session_state.current_url = url; st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with c4:
                        if is_saved: st.write("✅")
                        else:
                            if st.button("Salva", key=f"add_{res['videoId']}"):
                                df_now = get_db()
                                new_row = pd.DataFrame([{"TITOLO": title, "URL": url, "COPERTINA": thumb}])
                                conn.update(data=pd.concat([df_now, new_row], ignore_index=True).drop_duplicates())
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# === VISTA 3: LIBRERIA & DOWNLOAD ===
elif st.session_state.current_view == "🎧 LIBRERIA":
    st.markdown('<div class="section-title">La tua libreria</div>', unsafe_allow_html=True)
    if df.empty:
        st.info("La tua libreria è vuota.")
    else:
        for idx, row in df.iterrows():
            is_active = "active-row" if st.session_state.current_url == row['URL'] else ""
            st.markdown(f'<div class="track-row {is_active}">', unsafe_allow_html=True)
            cl1, cl2, cl3, cl4 = st.columns([1, 5, 2, 1])
            with cl1: 
                if 'COPERTINA' in row and pd.notnull(row['COPERTINA']): st.image(row['COPERTINA'], width=45)
            with cl2: st.markdown(f"**{row['TITOLO']}**")
            with cl3:
                st.markdown('<div class="btn-play-small">', unsafe_allow_html=True)
                if st.button("▶", key=f"l_p_{idx}"):
                    st.session_state.current_url = row['URL']; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with cl4:
                with st.popover("⚙️"):
                    st.code(row['URL'])
                    st.markdown(f'<a href="https://notube.link/it/youtube-app-317?url={row["URL"]}" target="_blank"><button style="width:100%; height:35px; background-color:#1DB954; color:black; border:none; border-radius:50px; font-weight:bold;">SCARICA</button></a>', unsafe_allow_html=True)
                    if st.button("Elimina", key=f"del_{idx}"):
                        conn.update(data=df.drop(index=idx)); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

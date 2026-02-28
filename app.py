import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 8.0: MOTORE SPOTIFY-CLONE, CONTROLLO TOTALE DELLE PARTICELLE
st.set_page_config(page_title="SIMPATIC-MUSIC LA MUSICA E LIBERTA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    h1, h2, h3 { color: #007FFF !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .result-card { background-color: #F8F9FA; padding: 20px; border-radius: 15px; border: 3px solid #007FFF; margin-bottom: 20px; box-shadow: 4px 4px 12px rgba(0,0,0,0.1); }
    .stButton>button { background-color: #1DB954 !important; color: white !important; border-radius: 30px !important; font-weight: 900 !important; text-transform: uppercase !important; width: 100% !important; border: none !important; height: 55px !important; font-size: 18px !important; }
    .btn-control>button { background-color: #007FFF !important; }
    .btn-delete>button { background-color: #DC3545 !important; }
    input { color: #000000 !important; font-weight: 900 !important; border: 2px solid #007FFF !important; text-transform: uppercase !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

def get_db():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "ID_VIDEO"])

# MOTORE BLINDATO: CERCA SOLO LE PARTICELLE ORIGINALI (COME SPOTIFY)
def search_spotify_like_songs(query):
    try:
        search_results = ytmusic.search(query, filter="songs", limit=10)
        formatted = []
        for res in search_results:
            vid_id = res['videoId']
            title = res['title']
            artists = ", ".join([a['name'] for a in res['artists']])
            formatted.append({
                'id': vid_id,
                'title': f"{artists} - {title}".upper()
            })
        return formatted
    except:
        return []

st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")
st.write("---")

# INIZIALIZZAZIONE DELLA MEMORIA DI SESSIONE PER IL LETTORE SPOTIFY-STYLE
if 'track_index' not in st.session_state:
    st.session_state.track_index = 0

menu = st.sidebar.radio("SALA REGIA", ["🔍 RICERCA BRANI (DATABASE UFFICIALE)", "🎧 LETTORE SIMPATIC-MUSIC"])

if menu == "🔍 RICERCA BRANI (DATABASE UFFICIALE)":
    st.markdown("### SCANSIONA L'ABISSO DEL DATABASE MUSICALE")
    query = st.text_input("INSERISCI LA PARTICELLA DA CERCARE (ES: PINO DANIELE NAPULE E)")
    
    if query:
        with st.spinner("SCANSIONE IN CORSO CON POLMONI D'ACCIAIO..."):
            results = search_spotify_like_songs(query)
            if not results:
                st.error("ERRORE: NESSUNA PARTICELLA TROVATA. CEMENTO INSTABILE.")
            else:
                for song in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{song["title"]}</h3></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            # ANTEPRIMA PARTICELLA
                            st.video(f"https://www.youtube.com/watch?v={song['id']}")
                        with c2:
                            if st.button("💾 AGGIUNGI ALLA CODA DI RIPRODUZIONE", key=f"s_{song['id']}"):
                                df = get_db()
                                new_row = pd.DataFrame([{"TITOLO": song['title'], "ID_VIDEO": song['id']}])
                                conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                                st.success("VINCITORE NASCOSTO AGGIUNTO ALLA DISCOTECA! DENSITÀ MASSIMA!")

else:
    st.title("🎧 LETTORE SIMPATIC-MUSIC - CONTROLLO TOTALE")
    df = get_db()
    
    if df.empty:
        st.warning("LA CODA È VUOTA. CERCA DELLE PARTICELLE PER INIZIARE IL FLUSSO.")
    else:
        # ASSICURIAMO CHE L'INDICE SIA SEMPRE BLINDATO
        if st.session_state.track_index >= len(df):
            st.session_state.track_index = 0
            
        current_track = df.iloc[st.session_state.track_index]
        
        st.markdown(f"### 🎶 IN RIPRODUZIONE ORA: {current_track['TITOLO']}")
        
        # IL LETTORE CENTRALE CHE ESEGUE LA PARTICELLA CORRENTE IN AUTOMATICO
        st.video(f"https://www.youtube.com/watch?v={current_track['ID_VIDEO']}?autoplay=1")
        
        # CONTROLLI TIPO SPOTIFY: AVANTI E INDIETRO
        col_prev, col_status, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            st.markdown('<div class="btn-control">', unsafe_allow_html=True)
            if st.button("⏮ BRANO PRECEDENTE"):
                if st.session_state.track_index > 0:
                    st.session_state.track_index -= 1
                else:
                    st.session_state.track_index = len(df) - 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_status:
            st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 20px; margin-top: 10px;'>TRACCIA {st.session_state.track_index + 1} DI {len(df)}</div>", unsafe_allow_html=True)
            
        with col_next:
            st.markdown('<div class="btn-control">', unsafe_allow_html=True)
            if st.button("⏭ BRANO SUCCESSIVO"):
                if st.session_state.track_index < len(df) - 1:
                    st.session_state.track_index += 1
                else:
                    st.session_state.track_index = 0
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown("### 📋 LA TUA CODA DI RIPRODUZIONE")
        
        for i, row in df.iterrows():
            with st.expander(f"{'▶️' if i == st.session_state.track_index else '🎵'} {row['TITOLO']}"):
                
                # TASTO PER SALTARE DIRETTAMENTE A QUESTA PARTICELLA
                if st.button("▶️ SALTA A QUESTA TRACCIA", key=f"jump_{i}"):
                    st.session_state.track_index = i
                    st.rerun()
                
                # TASTO ROSSO PER DISINTEGRARE LA PARTICELLA
                st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
                if st.button("❌ ELIMINA PARTICELLA", key=f"del_{i}"):
                    df_updated = df.drop(index=i)
                    conn.update(data=df_updated)
                    # FIX DENSITÀ: SE ELIMINIAMO LA TRACCIA ATTUALE, IL MOTORE SI RIALLINEA SENZA ERRORI
                    if st.session_state.track_index >= len(df_updated):
                         st.session_state.track_index = max(0, len(df_updated) - 1)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic
import urllib.parse

# PROTOCOLLO GRANITO 9.0: MOTORE IBRIDO (BRANI SINGOLI + PLAYLIST CONTINUE)
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
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

# MOTORE 1: BRANI SINGOLI
def search_songs(query):
    try:
        search_results = ytmusic.search(query, filter="songs", limit=8)
        formatted = []
        for res in search_results:
            formatted.append({
                'id': res['videoId'],
                'title': f"{', '.join([a['name'] for a in res['artists']])} - {res['title']}".upper(),
                'url': f"https://www.youtube.com/watch?v={res['videoId']}"
            })
        return formatted
    except:
        return []

# MOTORE 2: PLAYLIST UFFICIALI (FLUSSO CONTINUO)
def search_playlists(query):
    try:
        search_results = ytmusic.search(query, filter="playlists", limit=5)
        formatted = []
        for res in search_results:
            play_id = res['browseId']
            if play_id.startswith("VL"): play_id = play_id[2:] # Pulizia ID Playlist
            author = res.get('author', 'Artisti Vari')
            formatted.append({
                'id': play_id,
                'title': f"PLAYLIST: {author} - {res['title']}".upper(),
                'url': f"https://www.youtube.com/playlist?list={play_id}"
            })
        return formatted
    except:
        return []

st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")
st.write("---")

if 'track_index' not in st.session_state:
    st.session_state.track_index = 0

menu = st.sidebar.radio("SALA REGIA", ["🔍 RICERCA BRANI E PLAYLIST", "🎧 LA TUA DISCOTECA"])

if menu == "🔍 RICERCA BRANI E PLAYLIST":
    st.markdown("### SCANSIONA L'ABISSO DEL DATABASE MUSICALE")
    
    # SELETTORE DEL MOTORE DI RICERCA
    tipo_ricerca = st.radio("SELEZIONA IL FLUSSO CHE DESIDERI:", ["🎵 BRANO SINGOLO (Stile Spotify)", "📁 PLAYLIST INTERA (Flusso Continuo)"], horizontal=True)
    
    query = st.text_input("INSERISCI LA TUA RICERCA (ES: PINO DANIELE O ANNI 80)")
    
    if query:
        with st.spinner("SCANSIONE IN CORSO CON POLMONI D'ACCIAIO..."):
            if "SINGOLO" in tipo_ricerca:
                results = search_songs(query)
                is_playlist = False
            else:
                results = search_playlists(query)
                is_playlist = True
                
            if not results:
                st.error("ERRORE: NESSUNA PARTICELLA TROVATA. CEMENTO INSTABILE.")
            else:
                for item in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{item["title"]}</h3></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            if is_playlist:
                                # PLAYER PER PLAYLIST
                                iframe_code = f'<iframe width="100%" height="250" src="https://www.youtube.com/embed/videoseries?list={item["id"]}" frameborder="0" allowfullscreen></iframe>'
                                st.markdown(iframe_code, unsafe_allow_html=True)
                            else:
                                # PLAYER PER SINGOLO BRANO
                                st.video(item['url'])
                        with c2:
                            if st.button("💾 AGGIUNGI ALLA DISCOTECA", key=f"s_{item['id']}"):
                                df = get_db()
                                # CATEGORIZZAZIONE BLINDATA
                                categoria = "PLAYLIST" if is_playlist else "SINGOLO"
                                new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "CATEGORIA": categoria}])
                                conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                                st.success(f"{categoria} SALVATO CON DENSITÀ MASSIMA!")

else:
    st.title("🎧 LA TUA DISCOTECA - CONTROLLO TOTALE")
    df = get_db()
    
    if df.empty or 'URL' not in df.columns:
        st.warning("LA DISCOTECA È VUOTA. CERCA DELLE PARTICELLE PER INIZIARE.")
    else:
        # SEPARIAMO I BRANI SINGOLI DALLE PLAYLIST USANDO LA COLONNA URL O CATEGORIA
        df_singoli = df[~df['URL'].str.contains('list=')]
        df_playlist = df[df['URL'].str.contains('list=')]
        
        # ==========================================
        # SEZIONE 1: LETTORE SINGOLI BRANI (SPOTIFY CLONE)
        # ==========================================
        if not df_singoli.empty:
            st.markdown("### 🎵 CODA DI RIPRODUZIONE BRANI SINGOLI")
            
            # ALLINEAMENTO INDICE
            if st.session_state.track_index >= len(df_singoli):
                st.session_state.track_index = 0
                
            current_track = df_singoli.iloc[st.session_state.track_index]
            st.markdown(f"#### IN RIPRODUZIONE ORA: {current_track['TITOLO']}")
            st.video(current_track['URL'])
            
            # CONTROLLI TIPO SPOTIFY
            col_prev, col_status, col_next = st.columns([1, 2, 1])
            with col_prev:
                st.markdown('<div class="btn-control">', unsafe_allow_html=True)
                if st.button("⏮ BRANO PRECEDENTE", key="prev"):
                    st.session_state.track_index = st.session_state.track_index - 1 if st.session_state.track_index > 0 else len(df_singoli) - 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_status:
                st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 20px; margin-top: 10px;'>TRACCIA {st.session_state.track_index + 1} DI {len(df_singoli)}</div>", unsafe_allow_html=True)
            with col_next:
                st.markdown('<div class="btn-control">', unsafe_allow_html=True)
                if st.button("⏭ BRANO SUCCESSIVO", key="next"):
                    st.session_state.track_index = st.session_state.track_index + 1 if st.session_state.track_index < len(df_singoli) - 1 else 0
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            # LISTA DEI BRANI SINGOLI CON TASTO ELIMINA
            st.write("---")
            for idx, row in df_singoli.iterrows():
                # Troviamo la posizione relativa in df_singoli per il tasto "SALTA"
                rel_pos = df_singoli.index.get_loc(idx)
                with st.expander(f"{'▶️' if rel_pos == st.session_state.track_index else '🎵'} {row['TITOLO']}"):
                    c_jump, c_del = st.columns(2)
                    with c_jump:
                        if st.button("▶️ SALTA A QUESTA TRACCIA", key=f"jump_{idx}"):
                            st.session_state.track_index = rel_pos
                            st.rerun()
                    with c_del:
                        st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
                        if st.button("❌ ELIMINA", key=f"del_{idx}"):
                            conn.update(data=df.drop(index=idx))
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        
        # ==========================================
        # SEZIONE 2: LETTORE PLAYLIST (BACKGROUND CONTINUO)
        # ==========================================
        if not df_playlist.empty:
            st.markdown("### 📁 LE TUE PLAYLIST SALVATE")
            for idx, row in df_playlist.iterrows():
                with st.expander(f"📁 {row['TITOLO']}"):
                    # Estrae l'ID della playlist dal link
                    play_id = row['URL'].split("list=")[-1]
                    iframe_code = f'<iframe width="100%" height="350" src="https://www.youtube.com/embed/videoseries?list={play_id}" frameborder="0" allowfullscreen></iframe>'
                    st.markdown(iframe_code, unsafe_allow_html=True)
                    
                    st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
                    if st.button("❌ ELIMINA PLAYLIST", key=f"del_play_{idx}"):
                        conn.update(data=df.drop(index=idx))
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

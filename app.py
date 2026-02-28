import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic
import urllib.parse

# PROTOCOLLO GRANITO 12.0: MOTORE SEMANTICO E NAVIGAZIONE FLUIDA [cite: 2026-02-25]
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

# MOTORE SEMANTICO: TROVA TUTTO CIÒ CHE È ASSOCIATO AL NOME [cite: 2026-02-20]
def search_universal(query, filter_type):
    try:
        # Se è un link diretto, bypassiamo la ricerca [cite: 2026-02-25]
        if "youtube.com" in query or "youtu.be" in query:
             return [{'id': 'manual', 'title': 'LINK DIRETTO', 'url': query, 'is_playlist': 'list=' in query}]
        
        # Scansione dell'abisso senza filtri restrittivi iniziali per massima densità [cite: 2026-02-20]
        search_results = ytmusic.search(query, filter=filter_type, limit=12)
        formatted = []
        for res in search_results:
            try:
                if filter_type == "songs":
                    artists = res.get('artists', [{'name': 'Artista Sconosciuto'}])
                    name = f"{artists[0]['name']} - {res['title']}".upper()
                    url = f"https://www.youtube.com/watch?v={res['videoId']}"
                    item_id = res['videoId']
                else:
                    name = f"PLAYLIST: {res['title']}".upper()
                    item_id = res.get('browseId', res.get('playlistId', ''))
                    if item_id.startswith("VL"): item_id = item_id[2:]
                    url = f"https://www.youtube.com/playlist?list={item_id}"
                
                formatted.append({'id': item_id, 'title': name, 'url': url, 'is_playlist': filter_type != "songs"})
            except: continue
        return formatted
    except Exception:
        return []

st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")
st.write("---")

# MEMORIA DI SESSIONE PER IL PLAYER SPOTIFY-STYLE [cite: 2026-02-25]
if 'track_index' not in st.session_state: st.session_state.track_index = 0

menu = st.sidebar.radio("SALA REGIA", ["🔍 SCOPRI E CERCA", "🎧 LA TUA DISCOTECA"])

if menu == "🔍 SCOPRI E CERCA":
    st.markdown("### CERCA BRANI O PLAYLIST ASSOCIATE")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("COSA CERCHIAMO?", ["BRANI SINGOLI", "PLAYLIST E RACCOLTE"])
    with col2:
        query = st.text_input("INSERISCI NOME O LINK YOUTUBE:")

    if query:
        f_type = "songs" if tipo == "BRANI SINGOLI" else "playlists"
        with st.spinner("SCANSIONE CON POLMONI D'ACCIAIO... [cite: 2026-02-18]"):
            results = search_universal(query, f_type)
            if not results:
                st.error("ERRORE: NESSUNA PARTICELLA TROVATA. PROVA UN TERMINE PIÙ AMPIO [cite: 2026-02-20].")
            else:
                for item in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{item["title"]}</h3></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            if item['is_playlist']:
                                pid = item['url'].split("list=")[-1]
                                st.markdown(f'<iframe width="100%" height="300" src="https://www.youtube.com/embed/videoseries?list={pid}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                            else:
                                st.video(item['url'])
                        with c2:
                            if st.button("💾 AGGIUNGI ALLA DISCOTECA", key=f"s_{item['id']}_{item['title']}"):
                                df = get_db()
                                cat = "PLAYLIST" if item['is_playlist'] else "SINGOLO"
                                new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "CATEGORIA": cat}])
                                conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                                st.success("AGGIUNTO CON DENSITÀ MASSIMA! [cite: 2026-02-20]")

else:
    st.title("🎧 LA TUA DISCOTECA - FLUSSO CONTINUO [cite: 2026-02-21]")
    df = get_db()
    
    if df.empty:
        st.warning("IL CANTIERE È VUOTO. CERCA DELLE PARTICELLE PER INIZIARE [cite: 2026-02-20].")
    else:
        df_singoli = df[df['CATEGORIA'] == "SINGOLO"]
        df_playlist = df[df['CATEGORIA'] == "PLAYLIST"]
        
        if not df_singoli.empty:
            st.markdown("### 🎵 PLAYER SPOTIFY-STYLE (BRANI SINGOLI)")
            if st.session_state.track_index >= len(df_singoli): st.session_state.track_index = 0
            
            curr = df_singoli.iloc[st.session_state.track_index]
            st.markdown(f"#### ORA IN ONDA: {curr['TITOLO']}")
            st.video(curr['URL'])
            
            c_p, c_s, c_n = st.columns([1, 2, 1])
            with c_p:
                if st.button("⏮ PRECEDENTE"):
                    st.session_state.track_index = (st.session_state.track_index - 1) % len(df_singoli)
                    st.rerun()
            with c_s:
                st.write(f"TRACCIA {st.session_state.track_index + 1} / {len(df_singoli)}")
            with c_n:
                if st.button("⏭ SUCCESSIVO"):
                    st.session_state.track_index = (st.session_state.track_index + 1) % len(df_singoli)
                    st.rerun()
            
            with st.expander("VEDI TUTTA LA CODA"):
                for idx, row in df_singoli.iterrows():
                    col_t, col_d = st.columns([4, 1])
                    col_t.write(f"{row['TITOLO']}")
                    if col_d.button("❌", key=f"del_{idx}"):
                        conn.update(data=df.drop(index=idx))
                        st.rerun()

        if not df_playlist.empty:
            st.write("---")
            st.markdown("### 📁 LE TUE PLAYLIST E RACCOLTE")
            for idx, row in df_playlist.iterrows():
                with st.expander(f"📁 {row['TITOLO']}"):
                    pid = row['URL'].split("list=")[-1]
                    st.markdown(f'<iframe width="100%" height="350" src="https://www.youtube.com/embed/videoseries?list={pid}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                    if st.button("ELIMINA PLAYLIST", key=f"del_p_{idx}"):
                        conn.update(data=df.drop(index=idx))
                        st.rerun()

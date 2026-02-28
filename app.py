import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic
import yt_dlp
import urllib.parse

# PROTOCOLLO GRANITO 14.0: MOTORE IBRIDO E NAVIGAZIONE SPOTIFY [cite: 2026-02-25]
st.set_page_config(page_title="SIMPATIC-MUSIC LA MUSICA E LIBERTA", layout="wide")

# CSS: ALTA VISIBILITÀ E CEMENTO ARMATO [cite: 2026-01-20]
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

# MOTORE IBRIDO: PRECISIONE MUSICALE + FORZA BRUTA YOUTUBE [cite: 2026-02-18, 2026-02-20]
def search_hybrid(query):
    # BYPASS LINK DIRETTO [cite: 2026-02-25]
    if "youtube.com" in query or "youtu.be" in query:
        return [{'id': 'manual', 'title': 'LINK DIRETTO', 'url': query, 'cat': 'SINGOLO'}]
    
    formatted = []
    try:
        # PRIMA SCANSIONE: YT MUSIC (BRANI E PLAYLIST) [cite: 2026-02-20]
        results = ytmusic.search(query, limit=25)
        for res in results:
            r_type = res.get('resultType')
            if r_type in ['song', 'video']:
                artists = res.get('artists', [{'name': 'Artista'}])
                formatted.append({
                    'id': res.get('videoId'),
                    'title': f"{artists[0]['name']} - {res['title']}".upper(),
                    'url': f"https://www.youtube.com/watch?v={res['videoId']}",
                    'cat': 'SINGOLO'
                })
            elif r_type == 'playlist':
                p_id = res.get('browseId', res.get('playlistId', ''))
                if p_id.startswith("VL"): p_id = p_id[2:]
                formatted.append({
                    'id': p_id,
                    'title': f"PLAYLIST: {res['title']}".upper(),
                    'url': f"https://www.youtube.com/playlist?list={p_id}",
                    'cat': 'PLAYLIST'
                })
    except: pass

    # SECONDA SCANSIONE (FALLBACK): YOUTUBE SEARCH SE YT MUSIC FALLISCE [cite: 2026-02-20]
    if len(formatted) < 5:
        ydl_opts = {'quiet': True, 'default_search': 'ytsearch15', 'nocheckcertificate': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                for entry in info.get('entries', []):
                    if entry:
                        formatted.append({
                            'id': entry.get('id'),
                            'title': entry.get('title', 'SINFONIA').upper(),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'cat': 'SINGOLO'
                        })
            except: pass
    
    return formatted

st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")
st.write("---")

if 'track_idx' not in st.session_state: st.session_state.track_idx = 0

menu = st.sidebar.radio("SALA REGIA", ["🔍 SCOPRI E CERCA", "🎧 LA TUA DISCOTECA"])

if menu == "🔍 SCOPRI E CERCA":
    st.markdown("### CERCA NEL DATABASE UNIVERSALE")
    query = st.text_input("INSERISCI ARTISTA, CANZONE O LINK YOUTUBE (MAIUSCOLO) [cite: 2026-01-20]")
    
    if query:
        with st.spinner("SCANSIONE DELL'ABISSO IN CORSO... [cite: 2026-02-20]"):
            results = search_hybrid(query)
            if not results:
                st.error("ERRORE: NESSUNA PARTICELLA TROVATA. IL MURO È ALTO. RIPROVA [cite: 2026-01-25].")
            else:
                for item in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{item["title"]}</h3></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            if "list=" in item['url']:
                                pid = item['url'].split("list=")[-1]
                                st.markdown(f'<iframe width="100%" height="250" src="https://www.youtube.com/embed/videoseries?list={pid}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                            else:
                                st.video(item['url'])
                        with c2:
                            if st.button("💾 AGGIUNGI ALLA DISCOTECA", key=f"add_{item['id']}_{item['title'][:5]}"):
                                df = get_db()
                                new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "CATEGORIA": item['cat']}])
                                conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                                st.success("VINCITORE NASCOSTO SALVATO! [cite: 2026-02-20]")
                            st.write("LINK PER DOWNLOAD:")
                            st.code(item['url'], language="text")

else:
    st.title("🎧 LA TUA DISCOTECA - FLUSSO CONTINUO [cite: 2026-02-21]")
    df = get_db()
    
    if df.empty:
        st.warning("IL CANTIERE È VUOTO. COSTRUISCI LA TUA LIBERTÀ [cite: 2026-02-20].")
    else:
        # LETTORE SPOTIFY-STYLE PER I BRANI SINGOLI [cite: 2026-02-25]
        df_songs = df[df['CATEGORIA'] == "SINGOLO"]
        if not df_songs.empty:
            st.markdown("### 🎼 PLAYER SPOTIFY")
            if st.session_state.track_idx >= len(df_songs): st.session_state.track_idx = 0
            
            curr = df_songs.iloc[st.session_state.track_idx]
            st.markdown(f"#### IN ONDA ORA: {curr['TITOLO']}")
            st.video(curr['URL'])
            
            c_p, c_s, c_n = st.columns([1, 2, 1])
            with c_p:
                if st.button("⏮ PRECEDENTE"):
                    st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df_songs)
                    st.rerun()
            with c_s:
                st.write(f"TRACCIA {st.session_state.track_idx + 1} / {len(df_songs)}")
            with c_n:
                if st.button("⏭ SUCCESSIVO"):
                    st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df_songs)
                    st.rerun()
        
        st.write("---")
        with st.expander("GESTISCI TUTTA LA TUA DISCOTECA"):
            for idx, row in df.iterrows():
                col_t, col_j, col_d = st.columns([4, 1, 1])
                col_t.write(f"**{row['TITOLO']}** ({row['CATEGORIA']})")
                if row['CATEGORIA'] == "SINGOLO" and col_j.button("▶️", key=f"play_{idx}"):
                    # TROVA L'INDICE RELATIVO NELLA LISTA SINGOLI
                    st.session_state.track_idx = list(df_songs.index).index(idx)
                    st.rerun()
                if col_d.button("❌", key=f"del_{idx}"):
                    conn.update(data=df.drop(index=idx))
                    st.rerun()

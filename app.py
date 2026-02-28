import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import yt_dlp
import urllib.parse

# PROTOCOLLO GRANITO 13.0: MOTORE UNIVERSALE YOUTUBE - ZERO BLOCCHI [cite: 2026-02-25]
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

def get_db():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

# MOTORE UNIVERSALE: SCANSIONE DIRETTA YOUTUBE (ZERO FILTRI RESTRITTIVI) [cite: 2026-02-18, 2026-02-20]
def search_universal_yt(query, limit=30):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': f'ytsearch{limit}',
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    # BYPASS LINK DIRETTO [cite: 2026-02-25]
    if "youtube.com" in query or "youtu.be" in query:
        return [{'id': 'manual', 'title': 'LINK DIRETTO INSERITO', 'url': query, 'is_playlist': 'list=' in query}]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            results = info.get('entries', [])
            formatted = []
            for res in results:
                if res:
                    formatted.append({
                        'id': res.get('id'),
                        'title': res.get('title', 'Senza Titolo').upper(),
                        'url': f"https://www.youtube.com/watch?v={res.get('id')}",
                        'is_playlist': False
                    })
            return formatted
        except:
            return []

st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")
st.write("---")

if 'track_index' not in st.session_state: st.session_state.track_index = 0

menu = st.sidebar.radio("SALA REGIA", ["🔍 SCOPRI E CERCA", "🎧 LA TUA DISCOTECA"])

if menu == "🔍 SCOPRI E CERCA":
    st.markdown("### CERCA QUALSIASI BRANO O PLAYLIST NEL MONDO")
    query = st.text_input("INSERISCI NOME ARTISTA, CANZONE O LINK YOUTUBE:")

    if query:
        with st.spinner("SCANSIONE UNIVERSALE IN CORSO... DENSITÀ MASSIMA [cite: 2026-02-20]"):
            results = search_universal_yt(query)
            if not results:
                st.error("ERRORE: NESSUNA PARTICELLA TROVATA NELL'ABISSO [cite: 2026-01-25].")
            else:
                st.write(f"TROVATE {len(results)} SINFONIE DISPONIBILI.")
                for item in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{item["title"]}</h3></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            # PLAYER INTEGRATO - MASSIMA COMPATIBILITÀ [cite: 2026-02-25]
                            st.video(item['url'])
                        with c2:
                            if st.button("💾 AGGIUNGI ALLA DISCOTECA", key=f"s_{item['id']}_{item['title'][:10]}"):
                                df = get_db()
                                cat = "PLAYLIST" if item['is_playlist'] else "SINGOLO"
                                new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url'], "CATEGORIA": cat}])
                                conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                                st.success("AGGIUNTO CON POLMONI D'ACCIAIO! [cite: 2026-02-18]")
                            
                            st.write("COPIA LINK PER DOWNLOAD:")
                            st.code(item['url'], language="text")

else:
    st.title("🎧 LA TUA DISCOTECA - CONTROLLO TOTALE [cite: 2026-02-21]")
    df = get_db()
    
    if df.empty:
        st.warning("IL CANTIERE È VUOTO. INIZIA A COMPORRE LA TUA LIBERTÀ [cite: 2026-02-20].")
    else:
        # NAVIGAZIONE SPOTIFY-STYLE [cite: 2026-02-25]
        st.markdown("### 🎼 LETTORE SUPREMO")
        if st.session_state.track_index >= len(df): st.session_state.track_index = 0
        
        curr = df.iloc[st.session_state.track_index]
        st.markdown(f"#### ORA IN ONDA: {curr['TITOLO']}")
        st.video(curr['URL'])
        
        c_p, c_s, c_n = st.columns([1, 2, 1])
        with c_p:
            if st.button("⏮ PRECEDENTE"):
                st.session_state.track_index = (st.session_state.track_index - 1) % len(df)
                st.rerun()
        with c_s:
            st.write(f"TRACCIA {st.session_state.track_index + 1} / {len(df)}")
        with c_n:
            if st.button("⏭ SUCCESSIVO"):
                st.session_state.track_index = (st.session_state.track_index + 1) % len(df)
                st.rerun()
        
        st.write("---")
        with st.expander("GESTISCI TUTTA LA TUA DISCOTECA"):
            for idx, row in df.iterrows():
                col_t, col_j, col_d = st.columns([4, 1, 1])
                col_t.write(f"**{row['TITOLO']}**")
                if col_j.button("▶️", key=f"play_{idx}"):
                    st.session_state.track_index = df.index.get_loc(idx)
                    st.rerun()
                if col_d.button("❌", key=f"del_{idx}"):
                    conn.update(data=df.drop(index=idx))
                    st.rerun()

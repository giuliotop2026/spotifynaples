import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 6.0: SINFONIA CONTINUA E FLUSSO INARRESTABILE
st.set_page_config(page_title="SIMPATIC-MUSIC LA MUSICA E LIBERTA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    h1, h2, h3 { color: #007FFF !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .result-card { background-color: #F8F9FA; padding: 20px; border-radius: 15px; border: 3px solid #007FFF; margin-bottom: 20px; box-shadow: 4px 4px 12px rgba(0,0,0,0.1); }
    .stButton>button { background-color: #1DB954 !important; color: white !important; border-radius: 30px !important; font-weight: 900 !important; text-transform: uppercase !important; width: 100% !important; border: none !important; height: 55px !important; font-size: 18px !important; }
    .btn-delete>button { background-color: #DC3545 !important; }
    input { color: #000000 !important; font-weight: 900 !important; border: 2px solid #007FFF !important; text-transform: uppercase !important; }
</style>
""", unsafe_allow_html=True)

# CONNESSIONE DATABASE E MOTORE MUSICALE UFFICIALE
conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

def get_db():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "URL", "CATEGORIA"])

def search_spotify_like(query):
    try:
        search_results = ytmusic.search(query, filter="songs", limit=5)
        formatted = []
        for res in search_results:
            vid_id = res['videoId']
            title = res['title']
            artists = ", ".join([a['name'] for a in res['artists']])
            formatted.append({
                'id': vid_id,
                'title': f"{artists} - {title}".upper(),
                'webpage_url': f"https://www.youtube.com/watch?v={vid_id}"
            })
        return formatted
    except:
        return []

# ESTRATTORE DELLA PARTICELLA ID PER IL LETTORE SUPREMO
def extract_video_id(url):
    if "v=" in str(url):
        return str(url).split("v=")[1].split("&")[0]
    return None

st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")
st.write("---")

menu = st.sidebar.radio("SALA REGIA", ["🔍 CERCA SINFONIA", "📂 LA TUA DISCOTECA"])

if menu == "🔍 CERCA SINFONIA":
    query = st.text_input("INSERISCI L'ARTISTA O LA TRACCIA (MAIUSCOLO)")
    if query:
        with st.spinner("ACCORDANDO GLI STRUMENTI. SCANSIONE DELL'ABISSO IN CORSO..."):
            results = search_spotify_like(query)
            if not results:
                st.error("ERRORE: NESSUN ACCORDO UFFICIALE TROVATO.")
            else:
                for vid in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{vid["title"]}</h3></div>', unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            st.video(vid['webpage_url'])
                        with c2:
                            if st.button("💾 AGGIUNGI ALLA DISCOTECA", key=f"s_{vid['id']}"):
                                df = get_db()
                                new_row = pd.DataFrame([{"TITOLO": vid['title'], "URL": vid['webpage_url'], "CATEGORIA": "DISCOTECA"}])
                                conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                                st.success("TRACCIA REGISTRATA CON DENSITÀ MASSIMA!")
                        with c3:
                            st.write("**1️⃣ COPIA IL LINK DEL DISCO:**")
                            st.code(vid['webpage_url'], language="text")
                            st.write("**2️⃣ VAI IN SALA INCISIONE:**")
                            notube_correct = "https://notube.link/it/youtube-app-317"
                            st.markdown(f'<a href="{notube_correct}" target="_blank"><button style="width:100%; height:45px; background-color:#007FFF; color:white; border-radius:20px; border:none; font-weight:900; cursor:pointer; text-transform:uppercase;">⬇️ SCARICA MP3</button></a>', unsafe_allow_html=True)

else:
    st.title("📂 LA TUA DISCOTECA - FLUSSO CONTINUO")
    df = get_db()
    
    if df.empty:
        st.warning("LA DISCOTECA È VUOTA. INIZIA A COMPORRE LO SPARTITO.")
    else:
        # ---------------------------------------------------------
        # IL LETTORE SUPREMO: COSTRUISCE LA PLAYLIST AUTOMATICA
        # ---------------------------------------------------------
        st.markdown("### 📻 LETTORE SUPREMO (PLAYLIST AUTOMATICA)")
        
        video_ids = []
        for url in df['URL'].dropna():
            vid = extract_video_id(url)
            if vid:
                video_ids.append(vid)
        
        if video_ids:
            first_video = video_ids[0]
            # Unisce tutti gli altri video in una stringa separata da virgole
            playlist_string = ",".join(video_ids[1:]) if len(video_ids) > 1 else ""
            
            # Genera il player iframe blindato
            iframe_code = f'''
            <iframe width="100%" height="400" 
            src="https://www.youtube.com/embed/{first_video}?playlist={playlist_string}&autoplay=0&controls=1&loop=1" 
            title="SIMPATIC-MUSIC PLAYER" frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen></iframe>
            '''
            st.markdown(iframe_code, unsafe_allow_html=True)
            st.success("FLUSSO AGGANCIATO. USA I TASTI NEL VIDEO PER PASSARE AL BRANO SUCCESSIVO O PRECEDENTE.")
        
        st.write("---")
        st.markdown("### 🎼 GESTIONE SINGOLE TRACCE")
        
        for i, row in df.iterrows():
            with st.expander(f"🎵 {row['TITOLO']}"):
                st.write("**COPIA IL LINK DELLA TRACCIA:**")
                st.code(row['URL'], language="text")
                
                # TASTO ROSSO PER DISINTEGRARE LA PARTICELLA DAL DATABASE
                st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
                if st.button("❌ ELIMINA DALLA DISCOTECA", key=f"del_{i}"):
                    df_updated = df.drop(index=i)
                    conn.update(data=df_updated)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

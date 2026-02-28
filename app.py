import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# PROTOCOLLO GRANITO 7.0: RICERCA PLAYLIST UFFICIALI E FLUSSO SPOTIFY
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

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

def get_db():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "ID_PLAYLIST"])

# LA NUOVA CHIAVE: CERCARE SOLO PLAYLIST PER AVERE CENTINAIA DI BRANI ORIGINALI
def search_official_playlists(query):
    try:
        # filter="playlists" assicura che troviamo solo raccolte ufficiali
        search_results = ytmusic.search(query, filter="playlists", limit=5)
        formatted = []
        for res in search_results:
            play_id = res['browseId']
            # Rimuove il prefisso 'VL' che a volte YT Music aggiunge alle playlist
            if play_id.startswith("VL"):
                play_id = play_id[2:]
            
            title = res['title']
            author = res.get('author', 'Artisti Vari')
            formatted.append({
                'id': play_id,
                'title': f"{author} - {title}".upper()
            })
        return formatted
    except:
        return []

st.title("🎵 SIMPATIC-MUSIC: LA MUSICA È LIBERTÀ")
st.write("---")

menu = st.sidebar.radio("SALA REGIA", ["🔍 CERCA PLAYLIST (STILE SPOTIFY)", "📂 LE TUE PLAYLIST SALVATE"])

if menu == "🔍 CERCA PLAYLIST (STILE SPOTIFY)":
    st.markdown("### TROVA ORE DI MUSICA CONTINUA")
    query = st.text_input("CERCA UN ARTISTA, UN GENERE O UNA CLASSIFICA (ES: PINO DANIELE, TOP 50, POP ITALIANO)")
    
    if query:
        with st.spinner("SCANSIONE DELLE PLAYLIST UFFICIALI IN CORSO..."):
            results = search_official_playlists(query)
            if not results:
                st.error("ERRORE: NESSUNA PLAYLIST TROVATA. CEMENTO INSTABILE.")
            else:
                for play in results:
                    with st.container():
                        st.markdown(f'<div class="result-card"><h3>{play["title"]}</h3></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns([2, 1])
                        
                        with c1:
                            # IL LETTORE SUPREMO INCORPORATO DIRETTAMENTE NELLA RICERCA
                            iframe_code = f'''
                            <iframe width="100%" height="350" 
                            src="https://www.youtube.com/embed/videoseries?list={play['id']}&autoplay=0" 
                            title="SIMPATIC-MUSIC PLAYER" frameborder="0" 
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                            allowfullscreen></iframe>
                            '''
                            st.markdown(iframe_code, unsafe_allow_html=True)
                            
                        with c2:
                            if st.button("💾 SALVA PLAYLIST NELLA DISCOTECA", key=f"s_{play['id']}"):
                                df = get_db()
                                new_row = pd.DataFrame([{"TITOLO": play['title'], "ID_PLAYLIST": play['id']}])
                                conn.update(data=pd.concat([df, new_row], ignore_index=True).drop_duplicates())
                                st.success("PLAYLIST REGISTRATA CON DENSITÀ MASSIMA!")

else:
    st.title("📂 LE TUE PLAYLIST - FLUSSO CONTINUO")
    df = get_db()
    
    if df.empty:
        st.warning("LA TUA DISCOTECA È VUOTA. CERCA UNA PLAYLIST PER INIZIARE.")
    else:
        for i, row in df.iterrows():
            with st.expander(f"🎵 {row['TITOLO']}"):
                # IL LETTORE SUPREMO NELLA LIBRERIA
                iframe_code = f'''
                <iframe width="100%" height="350" 
                src="https://www.youtube.com/embed/videoseries?list={row['ID_PLAYLIST']}&autoplay=0" 
                title="SIMPATIC-MUSIC PLAYER" frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen></iframe>
                '''
                st.markdown(iframe_code, unsafe_allow_html=True)
                
                # TASTO ROSSO PER DISINTEGRARE LA PLAYLIST DAL DATABASE
                st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
                if st.button("❌ ELIMINA PLAYLIST", key=f"del_{i}"):
                    df_updated = df.drop(index=i)
                    conn.update(data=df_updated)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

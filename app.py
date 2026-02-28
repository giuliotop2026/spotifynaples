import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from ytmusicapi import YTMusic

# Configurazione dell'interfaccia Dark Mode
st.set_page_config(page_title="Simpatic-Music", layout="wide", initial_sidebar_state="collapsed")

# CSS: Design Dark con illuminazione attiva per il brano in riproduzione
st.markdown("""
<style>
    .stApp { background-color: #121212 !important; color: #FFFFFF !important; }
    h1, h2, h3 { color: #1DB954 !important; font-weight: 900; }
    
    /* Scheda brano standard */
    .result-card { 
        background-color: #181818; padding: 15px; border-radius: 10px; 
        border: 2px solid #282828; margin-bottom: 15px; transition: 0.3s;
    }
    
    /* Scheda illuminata quando il brano è in ascolto */
    .active-card { 
        background-color: #282828 !important; 
        border: 2px solid #1DB954 !important; 
        box-shadow: 0px 0px 15px rgba(29, 185, 84, 0.4);
    }
    
    .stButton>button { 
        background-color: #1DB954 !important; color: white !important; 
        border-radius: 50px !important; font-weight: 700 !important; 
        height: 45px !important; border: none !important; width: 100% !important;
    }
    
    .btn-delete>button { background-color: #E91E63 !important; }
    
    input { 
        background-color: #282828 !important; color: white !important; 
        border: 1px solid #1DB954 !important; border-radius: 10px !important;
    }
    
    p, label { color: #B3B3B3 !important; font-weight: 700; }
    code { background-color: #282828 !important; color: #1DB954 !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
ytmusic = YTMusic()

# Gestione della sessione per l'anteprima e la navigazione
if 'preview_url' not in st.session_state: st.session_state.preview_url = None
if 'track_idx' not in st.session_state: st.session_state.track_idx = 0

def get_db():
    try:
        # Legge i dati ignorando la cache per evitare sovrapposizioni
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["TITOLO", "URL"])

def search_music(query):
    try:
        results = ytmusic.search(query, limit=15)
        formatted = []
        for res in search_results := results:
            if res.get('resultType') in ['song', 'video']:
                artists = res.get('artists', [{'name': 'Artista'}])
                formatted.append({
                    'id': res.get('videoId'),
                    'title': f"{artists[0]['name']} - {res['title']}".upper(),
                    'url': f"https://www.youtube.com/watch?v={res['videoId']}"
                })
        return formatted
    except: return []

st.title("🎵 Simpatic-Music")
tabs = st.tabs(["🔍 CERCA", "📚 LIBRERIA"])

# --- SCHEDA RICERCA ---
with tabs[0]:
    # Player di anteprima unico in alto
    if st.session_state.preview_url:
        st.video(st.session_state.preview_url)
        if st.button("⏹ STOP ASCOLTO"):
            st.session_state.preview_url = None
            st.rerun()
    
    query = st.text_input("Cerca un brano o un artista", placeholder="Esempio: Pino Daniele...")
    if query:
        results = search_music(query)
        if not results:
            st.warning("Nessun risultato trovato.")
        for item in results:
            # Illumina la scheda se è quella in riproduzione
            is_active = "active-card" if st.session_state.preview_url == item['url'] else ""
            
            with st.container():
                st.markdown(f'''
                    <div class="result-card {is_active}">
                        <h4>{'▶️ ' if is_active else ''}{item["title"]}</h4>
                    </div>
                ''', unsafe_allow_html=True)
                
                col_play, col_save = st.columns([1, 1])
                
                with col_play:
                    if st.button(f"▶️ ASCOLTA", key=f"p_{item['id']}"):
                        st.session_state.preview_url = item['url']
                        st.rerun()
                
                with col_save:
                    if st.button(f"💾 SALVA IN LIBRERIA", key=f"lib_{item['id']}"):
                        # Recupera i dati attuali, aggiunge il nuovo e aggiorna tutto il foglio
                        df_current = get_db()
                        new_row = pd.DataFrame([{"TITOLO": item['title'], "URL": item['url']}])
                        df_updated = pd.concat([df_current, new_row], ignore_index=True).drop_duplicates()
                        conn.update(data=df_updated)
                        st.success("Aggiunto!")

# --- SCHEDA LIBRERIA (UNIFICATA) ---
with tabs[1]:
    st.markdown("### I TUOI BRANI SALVATI")
    df = get_db()
    
    if df.empty:
        st.info("La tua Libreria è vuota. Aggiungi brani dalla sezione Cerca.")
    else:
        # Player principale per la Libreria
        if st.session_state.track_idx >= len(df): st.session_state.track_idx = 0
        curr = df.iloc[st.session_state.track_idx]
        
        st.markdown(f"#### IN RIPRODUZIONE: {curr['TITOLO']}")
        st.video(curr['URL'])
        
        # Comandi avanti/indietro
        c_p, c_n = st.columns(2)
        if c_p.button("⏮ PRECEDENTE"):
            st.session_state.track_idx = (st.session_state.track_idx - 1) % len(df)
            st.rerun()
        if c_n.button("⏭ SUCCESSIVO"):
            st.session_state.track_idx = (st.session_state.track_idx + 1) % len(df)
            st.rerun()

        st.write("---")
        
        # Elenco per gestione link, download ed eliminazione
        for idx, row in df.iterrows():
            with st.expander(f"⚙️ GESTISCI: {row['TITOLO']}"):
                st.write("Copia il link per il download:")
                st.code(row['URL'], language="text")
                
                # Link diretto al convertitore
                notube_url = f"https://notube.link/it/youtube-app-317?url={row['URL']}"
                st.markdown(f'<a href="{notube_url}" target="_blank"><button style="width:100%; height:45px; background-color:#007FFF; color:white; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">VAI AL DOWNLOAD</button></a>', unsafe_allow_html=True)
                
                # Pulsante per eliminare il brano
                st.markdown('<div class="btn-delete">', unsafe_allow_html=True)
                if st.button("❌ ELIMINA DALLA LIBRERIA", key=f"rm_{idx}"):
                    df_new = df.drop(index=idx)
                    conn.update(data=df_new)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

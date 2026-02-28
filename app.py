import streamlit as st
import yt_dlp
import os
import io

# ==========================================
# 1. CONFIGURAZIONE E STILE "NAPOLI SPOTIFY"
# ==========================================
st.set_page_config(page_title="NAPOLI MUSIC HUB", page_icon="💙", layout="wide")

# Colori Napoli
AZZURRO_NAPOLI = "#1E90FF" # Un azzurro vivo
BLU_SCURO = "#001F5B"      # Per gradienti o contrasti
SFONDO_SCURO = "#121212"  # Sfondo base Spotify

# Iniezione CSS Personalizzato
st.markdown(f"""
<style>
    /* Sfondo generale e testo */
    .stApp {{
        background-color: {SFONDO_SCURO};
        color: white;
    }}

    /* Input di ricerca stilizzato */
    div[data-baseweb="input"] input {{
        background-color: #2A2A2A !important;
        color: white !important;
        border-radius: 20px !important;
        border: 1px solid transparent !important;
    }}
    div[data-baseweb="input"] input:focus {{
        border: 1px solid {AZZURRO_NAPOLI} !important;
    }}

    /* Pulsanti (Cerca e Download) */
    .stButton>button {{
        background-color: {AZZURRO_NAPOLI} !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
        width: 100%;
    }}
    .stButton>button:hover {{
        background-color: white !important;
        color: {BLU_SCURO} !important;
        transform: scale(1.05);
    }}

    /* Player Audio */
    audio {{
        width: 100%;
        border-radius: 10px;
    }}

    /* Titoli */
    h1, h2, h3, h7 {{
        color: white !important;
        font-family: 'Circular', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}

    /* Container dei risultati (Simil-Card) */
    .result-card {{
        background-color: #181818;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #282828;
        transition: background-color 0.3s ease;
    }}
    .result-card:hover {{
        background-color: #282828;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGICA DI BACKEND (YT-DLP)
# ==========================================

# Funzione per cercare e ottenere l'info dello streaming
@st.cache_data(show_spinner=False)
def get_stream_info(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'geo_bypass': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return {
            'id': info.get('id'),
            'title': info.get('title', 'TITOLO SCONOSCIUTO'),
            'url': info.get('url'), # URL Streaming diretto
            'thumb': info.get('thumbnail'),
            'duration': info.get('duration'),
            'webpage_url': info.get('webpage_url')
        }

# Funzione per scaricare l'MP3 effettivo (per l'offline)
def download_mp3_binary(video_url):
    # Cartella temporanea sul server Streamlit
    download_path = 'temp_download.mp3'

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_download.%(ext)s', # Salva temporaneamente
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Leggi il file in binario
    with open('temp_download.mp3', 'rb') as f:
        data = f.read()

    # Pulizia: rimuovi il file temporaneo sul server
    os.remove('temp_download.mp3')

    return data

# ==========================================
# 3. INTERFACCIA UTENTE
# ==========================================

# Sidebar simulata (stile Spotify)
with st.sidebar:
    st.markdown(f"<h1 style='color:{AZZURRO_NAPOLI}; text-align:center;'>💙 NAPOLI<br>MUSIC HUB</h1>", unsafe_allow_html=True)
    st.write("---")
    st.write("🎵 La tua musica.")
    st.write("🚫 Zero Pubblicità.")
    st.write("⬇️ Download Offline.")
    st.write("---")
    st.caption("Forza Napoli Sempre.")

# Area Principale
st.markdown("<h3>🔍 Cerca il tuo brano</h3>", unsafe_allow_html=True)
SEARCH_QUERY = st.text_input("", placeholder="Artista, canzone, album...", label_visibility="collapsed")

if SEARCH_QUERY:
    try:
        with st.spinner("⏳ Sintonizzazione sui server..."):
            DATA = get_stream_info(SEARCH_QUERY)

            # Layout Risultati a colonne
            col_thumb, col_play = st.columns([1, 3])

            with col_thumb:
                st.image(DATA['thumb'], use_container_width=True)

            with col_play:
                # Container stilizzato CSS
                st.markdown(f"""
                <div class="result-card">
                    <h7 style="color:gray;">BRANO</h7>
                    <h2 style="margin-top:0;">{DATA['title']}</h2>
                    <p style="color:gray;">Durata: {DATA['duration'] // 60}:{DATA['duration'] % 60:02d}</p>
                </div>
                <br>
                """, unsafe_allow_html=True)

                # PLAYER AUDIO DIRETTO (Streaming online)
                st.audio(DATA['url'], format='audio/mp3')

                st.write("---")
                # SEZIONE DOWNLOAD (Per Offline)
                st.markdown("<h4>⬇️ Salva per l'ascolto offline</h4>", unsafe_allow_html=True)
                st.caption("Il browser scaricherà il file MP3 sul tuo dispositivo.")

                # Bottone che attiva il download vero e proprio
                if st.button("PREPARA FILE MP3"):
                    with st.spinner("🔄 Conversione in MP3 in corso (potrebbe richiedere un minuto)..."):
                        mp3_data = download_mp3_binary(DATA['webpage_url'])

                        # Il vero bottone di download del browser apparirà ora
                        st.download_button(
                            label="⬇️ CLICCA QUI PER SCARICARE MP3",
                            data=mp3_data,
                            file_name=f"{DATA['title']}.mp3",
                            mime="audio/mp3"
                        )

    except Exception as e:
        st.error(f"⚠️ Errore durante il recupero: {e}")

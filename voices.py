import base64
import io
import streamlit as st
from gtts import gTTS

# Complete Sandbox Voice Profile Configuration Dropdown Menu
voice_config = {
    "🇺🇸 English (United States)": {"lang": "en", "tld": "com", "intro": "coords"},
    "🇦🇺 English (Australia)": {"lang": "en", "tld": "com.au", "intro": "coords"},
    "🇬🇧 English (United Kingdom)": {"lang": "en", "tld": "co.uk", "intro": "coords"},
    "🇨🇦 English (Canada)": {"lang": "en", "tld": "ca", "intro": "coords"},
    "🇮🇳 English (India)": {"lang": "en", "tld": "co.in", "intro": "coords"},
    "🇮🇪 English (Ireland)": {"lang": "en", "tld": "ie", "intro": "coords"},
    "🇳🇿 English (New Zealand)": {"lang": "en", "tld": "co.nz", "intro": "coords"},
    "🇿🇦 English (South Africa)": {"lang": "en", "tld": "co.za", "intro": "coords"},
    "🇲🇾 English (Malaysia)": {"lang": "en", "tld": "com.my", "intro": "coords"},
    "🇪🇸 Spanish (Spain Numbers)": {
        "lang": "es",
        "tld": "es",
        "intro": "coordenadas",
    },
    "🇫🇷 French (France Numbers)": {
        "lang": "fr",
        "tld": "fr",
        "intro": "coordonnées",
    },
    "🇩🇪 German (Germany Numbers)": {
        "lang": "de",
        "tld": "de",
        "intro": "koordinaten",
    },
}


def render_voice_settings():
    st.markdown("### 🎙️ Sandbox Voice Settings")
    voice_selection = st.selectbox(
        "Select Narration Profile / Accent Engine:",
        options=list(voice_config.keys()),
        index=0,
    )
    return voice_config[voice_selection]


def play_coordinates(target_x, target_y, cfg):
    narration_phrase = f"{cfg['intro']}, {target_x}, {target_y}. ... {target_x}, {target_y}."
    tts = gTTS(text=narration_phrase, lang=cfg["lang"], tld=cfg["tld"], slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)

    b64_audio = base64.b64encode(audio_fp.read()).decode()
    audio_data_uri = f"data:audio/mp3;base64,{b64_audio}"

    st.write("🔊 **Voice Narration Track:**")
    st.markdown(
        f'<audio src="{audio_data_uri}" controls autoplay style="width:100%;"></audio>',
        unsafe_allow_html=True,
    )

import streamlit as st
import io
import base64
from gtts import gTTS

def play_coordinate_narration(target_x, target_y):
    """
    Generates and plays the TTS coordinate narration track at 1.05x playback speed.
    """
    def fmt_tts(n):
        s = str(n)
        if len(s) == 3:
            return f"{s[0]} zero {s[2]}" if s[1] == '0' else f"{s[0]} {s[1:]}"
        return " ".join(list(s))

    speech_x = fmt_tts(target_x)
    speech_y = fmt_tts(target_y)
    
    # Formatted to cleanly speak the coordinates twice with a distinct pause break
    phrase = f"coords, {speech_x}, {speech_y}. ... {speech_x}, {speech_y}."
    
    audio_fp = io.BytesIO()
    gTTS(text=phrase, lang='en', tld='com').write_to_fp(audio_fp)
    audio_fp.seek(0)
    
    st.write("🔊 **Voice Narration Track:**")
    el_id = f"aud_{target_x}_{target_y}"
    
    st.markdown(
        f'<audio id="{el_id}" src="data:audio/mp3;base64,{base64.b64encode(audio_fp.read()).decode()}" controls autoplay style="width:100%;"></audio>', 
        unsafe_allow_html=True
    )
    
    # Speed modifier hack (5% increase)
    st.components.v1.html(
        f'<script>setTimeout(() => {{ const a = window.parent.document.getElementById("{el_id}"); if(a) a.playbackRate = 1.05; }}, 100);</script>', 
        height=0
    )

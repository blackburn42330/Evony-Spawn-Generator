import base64
import io
import streamlit as st
from gtts import gTTS


def render_voice_listener():
    html_code = """
    <div id="mic-status" style="color: #FFD700; font-weight: bold; font-family: sans-serif; padding: 10px; background: rgba(255,215,0,0.08); border: 1px solid #FFD700; border-radius: 6px; text-align: center; margin-bottom: 10px; cursor: pointer;">
        🎙️ Click here to wake up Hands-Free Companion Voice Engine
    </div>
    <script>
        function sendToStreamlit(data) {
            window.parent.postMessage({
                type: "streamlit:setComponentValue",
                value: data
            }, "*");
        }

        const statusBox = document.getElementById("mic-status");
        statusBox.addEventListener('click', () => {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) { statusBox.innerText = "❌ Speech API Blocked/Unsupported"; return; }
            
            const engine = new SpeechRec();
            engine.continuous = true;
            engine.interimResults = false;
            engine.lang = 'en-US';
            
            engine.onstart = () => {
                statusBox.innerHTML = "A🟢 LISTENING: Call out 'Spawn [1-5] X Y' hands-free...";
                statusBox.style.color = "#00FF00"; statusBox.style.background = "rgba(0,255,0,0.08)"; statusBox.style.borderColor = "#00FF00";
            };
            
            engine.onresult = (event) => {
                const transcript = event.results[event.results.length - 1].transcript.toLowerCase();
                const parse = transcript.match(/spawn\s*([1-5])\s*(\d{1,4})\s*(\d{1,4})/);
                if (parse) {
                    sendToStreamlit({
                        v_id: String(parse[1]),
                        v_x: String(parse[2]),
                        v_y: String(parse[3])
                    });
                }
            };
            engine.onerror = () => { engine.start(); };
            engine.onend = () => { engine.start(); };
            engine.start();
        }, { once: true });
    </script>
    """
    return st.components.v1.html(html_code, height=65)


def play_audio(target_x, target_y):
    phrase = f"coords, {target_x}, {target_y}. ... {target_x}, {target_y}."
    tts = gTTS(text=phrase, lang="en", tld="com", slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    b64 = base64.b64encode(audio_fp.read()).decode()
    st.markdown(
        f'<audio src="data:audio/mp3;base64,{b64}" autoplay style="display:none;"></audio>',
        unsafe_allow_html=True,
    )

import streamlit as st, numpy as np, pandas as pd, altair as alt, io, base64
from gtts import gTTS

st.set_page_config(page_title="Voice Companion", layout="centered")
st.title("🎙️ NCI Voice Spawn Companion")
st.markdown("<div style='color:#FFD700;font-size:22px;font-weight:bold;'>✨ BBR is an app writing genius ✨</div>", unsafe_allow_html=True)
st.write("Place phone next to iPad. Speak: **'Spawn [1-5] [X] [Y]'** (e.g., *'Spawn 2, 350, 800'*). Tap text to activate mic.")

HIVE_X, HIVE_Y = 356, 721

for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = ""
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = ""

# 🔊 Invisible Web Speech API Listening Engine (Fixed String Passing Arguments)
st.components.v1.html("""
    <div id="lis" style="color:#FFD700;font-weight:bold;padding:10px;background:rgba(255,215,0,0.1);border-radius:5px;text-align:center;font-family:sans-serif;cursor:pointer;">🔴 Microphone Standby (Tap screen once to wake up voice listener)</div>
    <script>
        window.addEventListener('click', () => {
            const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!Rec) { document.getElementById("lis").innerText = "❌ Speech Recognition Blocked"; return; }
            const rec = new Rec(); rec.continuous = true; rec.lang = 'en-US';
            rec.onstart = () => { let l = document.getElementById("lis"); l.innerText = "🟢 ACTIVE LISTENING: Say 'Spawn [1-5] X Y'..."; l.style.color = "#00FF00"; l.style.background = "rgba(0,255,0,0.1)"; };
            rec.onresult = (e) => {
                const text = e.results[e.results.length - 1].transcript.toLowerCase();
                const m = text.match(/spawn\s*([1-5])\s*(\d{1,4})\s*(\d{1,4})/);
                if (m) {
                    window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + `?u=${m[1]}&x=${m[2]}&y=${m[3]}`;
                }
            };
            rec.onerror = () => rec.start(); rec.onend = () => rec.start(); rec.start();
        }, { once: true });
    </script>""", height=65)

if "u" in st.query_params:
    st.session_state[f"x_{st.query_params['u']}"] = st.query_params["x"]
    st.session_state[f"y_{st.query_params['u']}"] = st.query_params["y"]
    st.query_params.clear()

if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6): st.session_state[f"x_{i}"], st.session_state[f"y_{i}"] = "", ""
    st.rerun()

spawns = []
st.subheader("📍 Monitored Spawns")
for i in range(1, 6):
    if i == 1 or (st.session_state[f"x_{i-1}"] and st.session_state[f"y_{i-1}"]):
        col_lbl, col_a, col_b, _ = st.columns([1.5, 1.5, 1.5, 4], gap="small")
        with col_lbl: st.markdown(f"<div style='padding-top:6px;font-weight:bold;'>Spawn {i}</div>", unsafe_allow_html=True)
        with col_a: x_in = st.text_input(f"S{i}X", value=st.session_state[f"x_{i}"], key=f"x_{i}", label_visibility="collapsed", placeholder="X")
        with col_b: y_in = st.text_input(f"S{i}Y", value=st.session_state[f"y_{i}"], key=f"y_{i}", label_visibility="collapsed", placeholder="Y")
        try:
            x_v, y_v = int(str(x_in).strip()), int(str(y_in).strip())
            if 0 <= x_v <= 1200 and 0 <= y_v <= 1200: spawns.append((x_v, y_v))
        except: pass

st.write("---")
rivals = [{"X": 319, "Y": 481, "Tag": "TDK"}, {"X": 611, "Y": 551, "Tag": "CoG"}, {"X": 673, "Y": 771, "Tag": "NFM"}]
t_df = pd.DataFrame(columns=["X", "Y", "E"])

if spawns:
    X, Y = np.meshgrid(np.arange(0, 1200), np.arange(0, 1200))
    X, Y = X.flatten(), Y.flatten()
    m = np.ones_like(X, dtype=bool)
    for sx, sy in spawns: m &= (np.sqrt((X - sx)**2 + (Y - sy)**2) > 150)
    for r in rivals: m &= (np.sqrt((X - r["X"])**2 + (r["Y"] - Y)**2) > 200)
    
    if len(X[m]) > 0:
        dist = np.sqrt((X[m] - HIVE_X)**2 + (Y[m] - HIVE_Y)**2)
        idx = np.argmin(dist)
        tx, ty = int(X[m][idx]), int(Y[m][idx])
        st.success(f"🎯 **Target Coordinates:** X: {tx}, Y: {ty} ({int(round(dist[idx]))} km from Hive)")
        
        # 🔊 Autoplay Google US Audio Pipeline
        tts = gTTS(text=f"coords, {tx}, {ty}. ... {tx}, {ty}.", lang='en', tld='com', slow=False)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay style="display:none;"></audio>', unsafe_allow_html=True)
        t_df = pd.DataFrame([{"X": tx-ty, "Y": tx+ty, "E": "🎯"}])
    else: st.error("❌ No safe coordinates found within constraints.")

# --- Mapping Visualization Layer ---
m_x_iso, max_x_iso = (520 - 350) - (600 + 350), (520 + 350) - (600 - 350)
m_y_iso, max_y_iso = (520 - 350) + (600 - 350), (520 + 350) + (600 + 350)
xs, ys = alt.Scale(domain=[m_x_iso, max_x_iso]), alt.Scale(domain=[m_y_iso, max_y_iso], reverse=True)

map_data = [{"X": HIVE_X-HIVE_Y, "Y": HIVE_X+HIVE_Y, "E": "🏰"}, {"X": 0, "Y": 1200, "E": "👑"}]
for sx, sy in spawns: map_data.append({"X": sx-sy, "Y": sx+sy, "E": "👹"})
for r in rivals: map_data.append({"X": r["X"]-r["Y"], "Y": r["X"]+r["Y"], "E": "💀"})

df = pd.concat([pd.DataFrame(map_data), t_df])
c = alt.Chart(df).mark_text(size=30).encode(x=alt.X('X:Q', scale=xs, axis=None), y=alt.Y('Y:Q', scale=ys, axis=None), text='E:N').properties(width=700, height=500).configure_view(strokeOpacity=0)
st.altair_chart(c, use_container_width=True)

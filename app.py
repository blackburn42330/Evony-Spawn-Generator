import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from gtts import gTTS
import io, base64

st.set_page_config(page_title="NCI Spawn Calculator", layout="centered")
st.title("🥷 NCI Spawn Calculator")

st.markdown("""
    <div style='text-align: left; font-family: "Arial Black", sans-serif; font-size: 22px; font-weight: bold; color: #FFD700; text-shadow: 0 0 10px #FFD700; padding-bottom: 15px; margin-top: -10px;'>✨ BBR is an app writing genius ✨</div>
    <style>
    div.stButton > button:first-child {
        font-size: 20px !important; font-weight: bold !important; padding: 10px 24px !important;
        border-radius: 8px !important; border: 2px solid #FFD700 !important; color: #FFD700 !important;
        background-color: rgba(255, 215, 0, 0.05) !important; width: 100% !important; margin: 10px 0 15px 0 !important;
    }
    div.stButton > button:first-child:hover { background-color: rgba(255, 215, 0, 0.15) !important; color: #FFF !important; border-color: #FFF !important; }
    </style>
""", unsafe_allow_html=True)

st.write("Finds the closest available coordinate to the hive outside a 150km radius of your spawns and 250km away from rivals.")

HIVE_X, HIVE_Y = 297, 791
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = ""
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = ""

if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6):
        st.session_state[f"x_{i}"], st.session_state[f"y_{i}"] = "", ""
        if f"field_x_{i}" in st.session_state: st.session_state[f"field_x_{i}"] = ""
        if f"field_y_{i}" in st.session_state: st.session_state[f"field_y_{i}"] = ""
    st.rerun()

st.subheader("📍 Active Spawns")
spawns = []
for i in range(1, 6):
    if i == 1 or (st.session_state[f"x_{i-1}"] and st.session_state[f"y_{i-1}"]):
        col_lbl, col_a, col_b, _ = st.columns([1.5, 1.5, 1.5, 4], gap="small")
        with col_lbl: st.markdown(f"<div style='padding-top: 6px; font-weight: bold;'>Spawn {i}</div>", unsafe_allow_html=True)
        with col_a: st.session_state[f"x_{i}"] = st.text_input(f"S{i}X", value=st.session_state[f"x_{i}"], key=f"field_x_{i}", placeholder="X...", label_visibility="collapsed")
        with col_b: st.session_state[f"y_{i}"] = st.text_input(f"S{i}Y", value=st.session_state[f"y_{i}"], key=f"field_y_{i}", placeholder="Y...", label_visibility="collapsed")
        try:
            x_v, y_v = int(st.session_state[f"x_{i}"].strip()), int(st.session_state[f"y_{i}"].strip())
            if 0 <= x_v <= 1200 and 0 <= y_v <= 1200: spawns.append((x_v, y_v))
        except ValueError: pass

st.write("---")
target_data = pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "Label", "Name"])
rivals = [{"X": 673, "Y": 771, "Tag": "TDK"}, {"X": 611, "Y": 551, "Tag": "CoG"}, {"X": 319, "Y": 481, "Tag": "NFM"}]

if len(spawns) > 0:
    X, Y = np.meshgrid(np.arange(0, 1200), np.arange(0, 1200))
    X, Y = X.flatten(), Y.flatten()
    valid_mask = np.ones_like(X, dtype=bool)
    
    for sx, sy in spawns: valid_mask &= (np.sqrt((X - sx)**2 + (Y - sy)**2) > 150)
    for r in rivals: valid_mask &= (np.sqrt((X - r["X"])**2 + (r["Y"] - Y)**2) > 250)
    
    valid_x, valid_y = X[valid_mask], Y[valid_mask]
    if len(valid_x) > 0:
        dist_to_hive = np.sqrt((valid_x - HIVE_X)**2 + (valid_y - HIVE_Y)**2)
        closest_idx = np.argmin(dist_to_hive)
        target_x, target_y = int(valid_x[closest_idx]), int(valid_y[closest_idx])
        true_dist = int(round(dist_to_hive[closest_idx]))
        
        st.success(f"🎯 **Teleport here:** X: {target_x}, Y: {target_y} ({true_dist} km from Hive)")
        
        clip_txt = f"{target_x} {target_y}"
        st.components.v1.html(f"""
        <button id="cb" style="width:100%; background:#1E1E24; color:#FFD700; border:1px solid #FFD700; padding:8px; border-radius:4px; font-weight:bold; cursor:pointer;">
            📋 <span id="ct">Copy Coordinates ({clip_txt})</span>
        </button>
        <script>
        document.getElementById('cb').addEventListener('click', function() {{
            navigator.clipboard.writeText('{clip_txt}').then(function() {{
                document.getElementById('ct').innerText = "Copied! ✓";
                document.getElementById('cb').style.background = "#2e7d32";
                document.getElementById('cb').style.color = "#fff";
                setTimeout(() => {{
                    document.getElementById('ct').innerText = "Copy Coordinates ({clip_txt})";
                    document.getElementById('cb').style.background = "#1E1E24";
                    document.getElementById('cb').style.color = "#FFD700";
                }}, 2000);
            }});
        }});
        </script>
        """, height=45)

        def fmt_tts(n):
            s = str(n)
            if len(s) == 3:
                return f"{s[0]} zero {s[2]}" if s[1] == '0' else f"{s[0]} {s[1:]}"
            return " ".join(list(s))

        speech_x = fmt_tts(target_x)
        speech_y = fmt_tts(target_y)
        
        # Formatted to cleanly speak the tracking coordinates twice with a distinct pause break
        phrase = f"coords, {speech_x}, {speech_y}. ... {speech_x}, {speech_y}."
        
        audio_fp = io.BytesIO()
        gTTS(text=phrase, lang='en', tld='com').write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        st.write("🔊 **Voice Narration Track:**")
        el_id = f"aud_{target_x}_{target_y}"
        st.markdown(f'<audio id="{el_id}" src="data:audio/mp3;base64,{base64.b64encode(audio_fp.read()).decode()}" controls autoplay style="width:100%;"></audio>', unsafe_allow_html=True)
        st.components.v1.html(f'<script>setTimeout(() => {{ const a = window.parent.document.getElementById("{el_id}"); if(a) a.playbackRate = 1.05; }}, 100);</script>', height=0)
        
        st.write("**Spawn Distances from Hive:**")
        st.write(" | ".join([f"**Spawn {idx}:** {int(round(np.sqrt((sx-HIVE_X)**2 + (sy-HIVE_Y)**2)))} km" for idx, (sx, sy) in enumerate(spawns, 1)]))
        target_data = pd.DataFrame([{"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯", "Label": f"Target ({target_x},{target_y})", "Name": ""}])
    else: st.error("❌ No valid spawning coordinates found.")

# --- Map Space definition Engine ---
min_x, max_x = 170, 870
min_y, max_y = 250, 950
x_s = alt.Scale(domain=[min_x - max_y, max_x - min_y])
y_s = alt.Scale(domain=[min_x + min_y, max_x + max_y])

h_d = pd.DataFrame([{"X_iso": HIVE_X - HIVE_Y, "Y_iso": HIVE_X + HIVE_Y, "Emoji": "🏰", "Label": f"Hive ({HIVE_X},{HIVE_Y})", "Name": "NCI"}])
t_d = pd.DataFrame([{"X_iso": 0, "Y_iso": 1200, "Emoji": "👑", "Label": "Throne (600,600)", "Name": ""}])
m_d = pd.DataFrame([{"X_iso": x-y, "Y_iso": x+y, "Emoji": "🏛️", "Label": f"Temple ({x},{y})", "Name": ""} for x, y in [(300,900), (900,300), (300,300), (900,900)]])
r_d = pd.DataFrame([{"X_iso": r["X"]-r["Y"], "Y_iso": r["X"]+r["Y"], "Emoji": "💀", "Label": f"[{r['Tag']}] ({r['X']},{r['Y']})", "Name": r["Tag"]} for r in rivals])
s_d = pd.DataFrame([{"X_iso": sx-sy, "Y_iso": sx+sy, "Emoji": "👾", "Label": f"Spawn {i} ({sx},{sy})", "Name": f"S{i}"} for i, (sx, sy) in enumerate(spawns, 1)])

rival_circles = pd.DataFrame([{"X_iso": r["X"]-r["Y"], "Y_iso": r["X"]+r["Y"]} for r in rivals])

map_items = pd.concat([h_d, t_d, m_d, r_d, s_d, target_data], ignore_index=True)

if not map_items.empty:
    st.subheader("🗺️ Tactical Map Overlay")
    
    base_chart = alt.Chart(map_items).mark_text(fontSize=22, baseline="middle", align="center").encode(
        x=alt.X("X_iso:Q", scale=x_s, axis=None), y=alt.Y("Y_iso:Q", scale=y_s, axis=None),
        text="Emoji:N", tooltip="Label:N"
    )
    
    names_chart = alt.Chart(map_items).mark_text(fontSize=13, fontWeight="bold", color="#FFA500", dx=22, align="left", baseline="middle").encode(
        x=alt.X("X_iso:Q", scale=x_s, axis=None), y=alt.Y("Y_iso:Q", scale=y_s, axis=None),
        text="Name:N"
    )
    
    layers = [base_chart, names_chart]
    
    if not rival_circles.empty:
        shade_chart = alt.Chart(rival_circles).mark_point(color="red", filled=True, opacity=0.12, size=20000).encode(
            x=alt.X("X_iso:Q", scale=x_s, axis=None), y=alt.Y("Y_iso:Q", scale=y_s, axis=None)
        )
        layers.insert(0, shade_chart)
        
    final_chart = alt.layer(*layers).properties(width=700, height=450, background="#111").configure_view(strokeWidth=0)
    st.altair_chart(final_chart, use_container_width=True)

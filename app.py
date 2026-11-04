import streamlit as st
import numpy as np
import pandas as pd
from gtts import gTTS
import io
import base64

# Import your newly created minimap module
from minimap import render_minimap

st.set_page_config(page_title="NCI Spawn Calculator", layout="centered")
st.title("🥷 NCI Spawn Calculator")

st.markdown("""
    <div style='text-align: left; font-family: "Arial Black", Gadget, sans-serif; font-size: 22px; font-weight: bold; color: #FFD700; text-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00; padding-bottom: 15px; margin-top: -10px;'>✨ BBR is an app writing genius ✨</div>
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
st.markdown("### 📋 Instructions:\n1. Enter the coordinates of your **first monster spawn** below.\n2. Type the coordinates of your **next spawn** into the fields side-by-side.\n3. The app will automatically calculate your safe location to teleport to as you type!")

# Updated Main Alliance Hive Coordinates
HIVE_X, HIVE_Y = 297, 791
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

# Initialize inputs inside session state cleanly
for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = ""
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = ""

# Memory Clear Loop Engine
if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6):
        st.session_state[f"x_{i}"] = ""
        st.session_state[f"y_{i}"] = ""
        if f"field_x_{i}" in st.session_state: st.session_state[f"field_x_{i}"] = ""
        if f"field_y_{i}" in st.session_state: st.session_state[f"field_y_{i}"] = ""
    st.rerun()

st.subheader("📍 Active Spawns")
spawns = []
def get_coord(val_string):
    try:
        val = int(val_string.strip())
        if 0 <= val <= 1200: return val
    except ValueError: pass
    return None

# --- Native Responsive Layout Generation ---
for i in range(1, 6):
    if i == 1 or (st.session_state[f"x_{i-1}"] and st.session_state[f"y_{i-1}"]) :
        col_lbl, col_a, col_b, _ = st.columns([1.5, 1.5, 1.5, 4], gap="small")
        with col_lbl:
            st.markdown(f"<div style='padding-top: 6px; font-weight: bold; font-size:15px; white-space: nowrap;'>Spawn {i}</div>", unsafe_allow_html=True)
        with col_a: 
            x_in = st.text_input(f"S{i}X", value=st.session_state[f"x_{i}"], key=f"field_x_{i}", placeholder="X...", label_visibility="collapsed")
            st.session_state[f"x_{i}"] = x_in
        with col_b: 
            y_in = st.text_input(f"S{i}Y", value=st.session_state[f"y_{i}"], key=f"field_y_{i}", placeholder="Y...", label_visibility="collapsed")
            st.session_state[f"y_{i}"] = y_in
        
        x_val, y_val = get_coord(x_in), get_coord(y_in)
        if x_val is not None and y_val is not None: spawns.append((x_val, y_val))

st.write("---")
target_x, target_y, true_dist = None, None, None
target_data = pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "Label"])
rivals = [{"X": 319, "Y": 481, "Tag": "TDK"}, {"X": 611, "Y": 551, "Tag": "CoG"}, {"X": 673, "Y": 771, "Tag": "NFM"}]

if len(spawns) > 0:
    x_range = np.arange(0, 1200)
    y_range = np.arange(0, 1200)
    X, Y = np.meshgrid(x_range, y_range)
    X, Y = X.flatten(), Y.flatten()
    valid_mask = np.ones_like(X, dtype=bool)
    
    for sx, sy in spawns: valid_mask &= (np.sqrt((X - sx)**2 + (Y - sy)**2) > 150)
    # Enforce 250km boundary around rivals
    for r in rivals: valid_mask &= (np.sqrt((X - r["X"])**2 + (r["Y"] - Y)**2) > 250)
    
    valid_x, valid_y = X[valid_mask], Y[valid_mask]
    if len(valid_x) > 0:
        # Calculate distance elements first
        dist_to_hive = np.sqrt((valid_x - HIVE_X)**2 + (valid_y - HIVE_Y)**2)
        closest_idx = np.argmin(dist_to_hive)
        
        # Set target coordinates correctly using the index
        target_x, target_y = int(valid_x[closest_idx]), int(valid_y[closest_idx])
        true_dist = int(round(dist_to_hive[closest_idx]))
        
        st.success(f"🎯 **Teleport here and continue spawning:** X: {target_x}, Y: {target_y} ({true_dist} km from Hive)")
        
        # Clean split formatter (e.g. 355 becomes "3 55", which speaks as "three fifty-five")
        def fmt_tts(num):
            s = str(num)
            if len(s) == 3:
                if s[1] == '0':
                    return f"{s[0]} zero {s[2]}"
                return f"{s[0]} {s[1:]}"
            return " ".join(list(s))

        speech_x = fmt_tts(target_x)
        speech_y = fmt_tts(target_y)
        phrase = f"coords, {speech_x}, {speech_y}. ... {speech_x}, {speech_y}."
        
        tts = gTTS(text=phrase, lang='en', tld='com', slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        b64 = base64.b64encode(audio_fp.read()).decode()
        st.write("🔊 **Voice Narration Track:**")
        
        audio_el_id = f"audio_{target_x}_{target_y}"
        st.markdown(f'<audio id="{audio_el_id}" src="data:audio/mp3;base64,{b64}" controls autoplay style="width:100%;"></audio>', unsafe_allow_html=True)
        
        # Speed modifier hack (5% increase)
        speed_control_html = f"""
        <script>
            setTimeout(() => {{
                const parentDoc = window.parent.document;
                const audioTag = parentDoc.getElementById("{audio_el_id}");
                if (audioTag) {{ audioTag.playbackRate = 1.05; }}
            }}, 100);
        </script>
        """
        st.components.v1.html(speed_control_html, height=0, width=0)
        
        st.write("**Spawn Distances from Hive:**")
        dist_strings = [f"**Spawn {idx}:** {int(round(np.sqrt((sx - HIVE_X)**2 + (sy - HIVE_Y)**2)))} km" for idx, (sx, sy) in enumerate(spawns, 1)]
        st.write(" | ".join(dist_strings))
        target_data = pd.DataFrame([{"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯", "Label": f"Target ({target_x},{target_y})"}])
    else: 
        st.error("❌ No valid spawning coordinates found with the current constraints.")

# --- Render Minimap Module Call ---
render_minimap(HIVE_X, HIVE_Y, spawns, rivals, target_data)

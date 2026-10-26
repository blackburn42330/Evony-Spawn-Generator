import base64
import io
import re
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="NCI Spawn Calculator", layout="centered")
st.title("🥷 NCI Spawn Calculator")

st.markdown(
    """
    <div style='text-align: left; font-family: "Arial Black", Gadget, sans-serif; font-size: 22px; font-weight: bold; color: #FFD700; text-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00; padding-bottom: 15px; margin-top: -10px;'>✨ BBR is an app writing genius ✨</div>
""",
    unsafe_allow_html=True,
)

st.write(
    "Finds the closest available coordinate to the hive outside a 150km radius of your spawns and 200km away from rivals."
)
st.markdown(
    "### 📋 Instructions:\n1. Type inputs normally using the side-by-side fields.\n2. **Optional Hands-Free:** Tap 'Start Listening', speak clearly (e.g., *'Spawn 1, 360, 700'*), and tap 'Stop & Process' to populate fields!"
)

HIVE_X, HIVE_Y = 356, 721
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

# Initialize inputs inside state loops
for i in range(1, 6):
    if f"x_{i}" not in st.session_state:
        st.session_state[f"x_{i}"] = ""
    if f"y_{i}" not in st.session_state:
        st.session_state[f"y_{i}"] = ""

st.subheader("🎙️ Hands-Free Voice Input")

# Text-to-Number Word Translation Dictionary to handle mobile voice streams
word_to_num = {
    "one": "1",
    "two": "2",
    "to": "2",
    "too": "2",
    "three": "3",
    "four": "4",
    "for": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "ate": "8",
    "nine": "9",
    "zero": "0",
    "oh": "0",
}


# --- ⚡ FIXED: Robust Voice Processing Pipeline with Clear Global Array Formatting Keys ---
def process_voice_input():
    # Dynamic unique key identification query loop matching the layout execution parameter context
    active_key = f"voice_engine_{st.session_state.get('active_voice_key_idx', 0)}"
    spoken_text = st.session_state.get(active_key)

    if spoken_text:
        # 1. Standardize text structure completely
        clean_text = str(spoken_text).lower().replace(",", " ").replace("-", " ").strip()

        # 2. Convert text numbers to regular digits
        words = clean_text.split()
        translated_words = [word_to_num.get(w, w) for w in words]
        processed_text = " ".join(translated_words)

        # 3. Pull out ALL standalone number fragments from the text block sequentially
        all_numbers = re.findall(r"\d+", processed_text)

        # 4. FIXED: Safe indexing parsing numbers directly out of string element blocks
        if len(all_numbers) >= 3:
            v_id = re.sub(r"\s+", "", str(all_numbers[0]))
            v_x = re.sub(r"\s+", "", str(all_numbers[1]))
            v_y = re.sub(r"\s+", "", str(all_numbers[2]))

            if v_id in ["1", "2", "3", "4", "5"]:
                try:
                    st.session_state[f"x_{v_id}"] = str(int(v_x))
                    st.session_state[f"y_{v_id}"] = str(int(v_y))
                except ValueError:
                    pass


# Keep count of populated data spawns to feed a dynamic shifting component key layout configuration
temp_spawns_count = 0
for i in range(1, 6):
    if st.session_state[f"x_{i}"] and st.session_state[f"y_{i}"]:
        temp_spawns_count += 1

st.session_state["active_voice_key_idx"] = temp_spawns_count
dynamic_engine_key = f"voice_engine_{temp_spawns_count}"

# FIXED: Render microphone component using our dynamic shifting key logic to stop DuplicateElement errors
speech_to_text(
    start_prompt="🎙️ Start Listening",
    stop_prompt="🛑 Stop & Process",
    language="en",
    key=dynamic_engine_key,
    callback=process_voice_input,
)

if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6):
        st.session_state[f"x_{i}"], st.session_state[f"y_{i}"] = "", ""
    st.rerun()

st.subheader("📍 Active Spawns")
spawns = []


def get_coord(val_string):
    try:
        val = int(str(val_string).strip())
        if 0 <= val <= 1200:
            return val
    except ValueError:
        pass
    return None


# Clean columns completely intact for standard grid typing or voice updates
for i in range(1, 6):
    if i == 1 or (st.session_state[f"x_{i-1}"] and st.session_state[f"y_{i-1}"]):
        col_lbl, col_a, col_b, _ = st.columns([1.5, 1.5, 1.5, 4], gap="small")
        with col_lbl:
            st.markdown(
                f"<div style='padding-top: 6px; font-weight: bold;'>Spawn {i}</div>",
                unsafe_allow_html=True,
            )
        with col_a:
            x_in = st.text_input(
                f"S{i}X",
                value=st.session_state[f"x_{i}"],
                key=f"x_{i}",
                placeholder="X...",
                label_visibility="collapsed",
            )
        with col_b:
            y_in = st.text_input(
                f"S{i}Y",
                value=st.session_state[f"y_{i}"],
                key=f"y_{i}",
                placeholder="Y...",
                label_visibility="collapsed",
            )
        x_val, y_val = get_coord(x_in), get_coord(y_in)
        if x_val is not None and y_val is not None:
            spawns.append((x_val, y_val))

st.write("---")
target_x, target_y = None, None
target_data = pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji"])
rivals = [{"X": 319, "Y": 481}, {"X": 611, "Y": 551}, {"X": 673, "Y": 771}]

if len(spawns) > 0:
    X, Y = np.meshgrid(np.arange(0, 1200), np.arange(0, 1200))
    X, Y = X.flatten(), Y.flatten()
    valid_mask = np.ones_like(X, dtype=bool)
    for sx, sy in spawns:
        valid_mask &= np.sqrt((X - sx) ** 2 + (Y - sy) ** 2) > 150
    for r in rivals:
        valid_mask &= np.sqrt((X - r["X"]) ** 2 + (r["Y"] - Y) ** 2) > 200

    valid_x, valid_y = X[valid_mask], Y[valid_mask]
    if len(valid_x) > 0:
        dist = np.sqrt((valid_x - HIVE_X) ** 2 + (valid_y - HIVE_Y) ** 2)
        idx = np.argmin(dist)
        target_x, target_y = int(valid_x[idx]), int(valid_y[idx])
        st.success(
            f"🎯 **Teleport here:** X: {target_x}, Y: {target_y} ({int(round(dist[idx]))} km from Hive)"
        )

        # 🔊 Autoplay Audio Output Channel
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
        target_data = pd.DataFrame(
            [{"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯"}]
        )

CENTER_X, CENTER_Y = 520, 600
x_scale = alt.Scale(
    domain=[
        (CENTER_X - 350) - (CENTER_Y + 350),
        (CENTER_X + 350) - (CENTER_Y - 350),
    ]
)
y_scale = alt.Scale(
    domain=[
        (CENTER_X - 350) + (CENTER_Y - 350),
        (CENTER_X + 350) + (CENTER_Y + 350),
    ],
    reverse=True,
)

map_data = [
    {"X_iso": HIVE_X - HIVE_Y, "Y_iso": HIVE_X + HIVE_Y, "Emoji": "🏰"},
    {"X_iso": 0, "Y_iso": 1200, "Emoji": "👑"},
]
for sx, sy in spawns:
    map_data.append({"X_iso": sx - sy, "Y_iso": sx + sy, "Emoji": "👹"})
for r in rivals:
    map_data.append({"X_iso": r["X"] - r["Y"], "Y_iso": r["X"] + r["Y"], "Emoji": "💀"})

df = pd.concat([pd.DataFrame(map_data), target_data])
chart = (
    alt.Chart(df)
    .mark_text(size=30)
    .encode(
        x=alt.X("X_iso:Q", scale=x_scale, axis=None),
        y=alt.Y("Y_iso:Q", scale=y_scale, axis=None),
        text="Emoji:N",
    )
    .properties(width=700, height=500)
    .configure_view(strokeOpacity=0)
)
st.altair_chart(chart, use_container_width=True)

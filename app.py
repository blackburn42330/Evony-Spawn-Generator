import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from voice_listener import render_voice_listener, play_audio

st.set_page_config(page_title="NCI Spawn Calculator", layout="centered")
st.title("🥷 NCI Spawn Calculator")

st.markdown("""
    <div style='text-align: left; font-family: "Arial Black", Gadget, sans-serif; font-size: 22px; font-weight: bold; color: #FFD700; text-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00; padding-bottom: 15px; margin-top: -10px;'>✨ BBR is an app writing genius ✨</div>
""", unsafe_allow_html=True)

HIVE_X, HIVE_Y = 356, 721
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = ""
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = ""

# Render voice companion component
render_voice_listener()

if "v_id" in st.query_params:
    st.session_state[f"x_{st.query_params['v_id']}"] = st.query_params["v_x"]
    st.session_state[f"y_{st.query_params['v_id']}"] = st.query_params["v_y"]
    st.query_params.clear()

if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6): st.session_state[f"x_{i}"], st.session_state[f"y_{i}"] = "", ""
    st.rerun()

st.subheader("📍 Active Spawns")
spawns = []
def get_coord(val_string):
    try:
        val = int(str(val_string).strip())
        if 0 <= val <= 1200: return val
    except ValueError: pass
    return None

for i in range(1, 6):
    if i == 1 or (st.session_state[f"x_{i-1}"] and st.session_state[f"y_{i-1}"]):
        col_lbl, col_a, col_b, _ = st.columns([1.5, 1.5, 1.5, 4], gap="small")
        with col_lbl: st.markdown(f"<div style='padding-top: 6px; font-weight: bold;'>Spawn {i}</div>", unsafe_allow_html=True)
        with col_a: x_in = st.text_input(f"S{i}X", value=st.session_state[f"x_{i}"], key=f"x_{i}", placeholder="X...", label_visibility="collapsed")
        with col_b: y_in = st.text_input(f"S{i}Y", value=st.session_state[f"y_{i}"], key=f"y_{i}", placeholder="Y...", label_visibility="collapsed")
        x_val, y_val = get_coord(x_in), get_coord(y_in)
        if x_val is not None and y_val is not None: spawns.append((x_val, y_val))

st.write("---")
target_x, target_y = None, None
target_data = pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji"])
rivals = [{"X": 319, "Y": 481}, {"X": 611, "Y": 551}, {"X": 673, "Y": 771}]

if len(spawns) > 0:
    X, Y = np.meshgrid(np.arange(0, 1200), np.arange(0, 1200))
    X, Y = X.flatten(), Y.flatten()
    valid_mask = np.ones_like(X, dtype=bool)
    for sx, sy in spawns: valid_mask &= (np.sqrt((X - sx)**2 + (Y - sy)**2) > 150)
    for r in rivals: valid_mask &= (np.sqrt((X - r["X"])**2 + (r["Y"] - Y)**2) > 200)
    
    valid_x, valid_y = X[valid_mask], Y[valid_mask]
    if len(valid_x) > 0:
        dist = np.sqrt((valid_x - HIVE_X)**2 + (valid_y - HIVE_Y)**2)
        idx = np.argmin(dist)
        target_x, target_y = int(valid_x[idx]), int(valid_y[idx])
        st.success(f"🎯 **Teleport here:** X: {target_x}, Y: {target_y} ({int(round(dist[idx]))} km from Hive)")
        
        play_audio(target_x, target_y)
        target_data = pd.DataFrame([{"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯"}])

CENTER_X, CENTER_Y = 520, 600
x_scale = alt.Scale(domain=[(CENTER_X - 350) - (CENTER_Y + 350), (CENTER_X + 350) - (CENTER_Y - 350)])
y_scale = alt.Scale(domain=[(CENTER_X - 350) + (CENTER_Y - 350), (CENTER_X + 350) + (CENTER_Y + 350)], reverse=True)

map_data = [{"X_iso": HIVE_X-HIVE_Y, "Y_iso": HIVE_X+HIVE_Y, "Emoji": "🏰"}, {"X_iso": 0, "Y_iso": 1200, "Emoji": "👑"}]
for sx, sy in spawns: map_data.append({"X_iso": sx-sy, "Y_iso": sx+sy, "Emoji": "👹"})
for r in rivals: map_data.append({"X_iso": r["X"]-r["Y"], "Y_iso": r["X"]+r["Y"], "Emoji": "💀"})

df = pd.concat([pd.DataFrame(map_data), target_data])
chart = alt.Chart(df).mark_text(size=30).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N').properties(width=700, height=500).configure_view(strokeOpacity=0)
st.altair_chart(chart, use_container_width=True)

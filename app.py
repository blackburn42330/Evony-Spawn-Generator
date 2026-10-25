import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Evony Spawn Generator", layout="centered")
st.title("🥷 Evony Spawn Generator")

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

# 🔄 Radius Description updated to 150km
st.write("Finds the closest available coordinate to the hive outside a 150km radius of your spawns and 200km away from rivals.")

st.markdown("### 📋 Instructions:\n1. Enter the coordinates of your **first monster spawn** below (do NOT enter your own hive coordinates).\n2. Type the coordinates of your **next spawn** into the new box that appears side-by-side.\n3. The app will automatically calculate your safe location to teleport to as you type!")

HIVE_X, HIVE_Y = 356, 721
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6): st.session_state[f"x_{i}"], st.session_state[f"y_{i}"] = "", ""
    st.rerun()

st.subheader("📍 Active Spawns")
for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = ""
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = ""

spawns = []
def get_coord(val_string):
    try:
        val = int(val_string.strip())
        if 0 <= val <= 1200: return val
    except ValueError: pass
    return None

# --- Spawn 1 Row ---
col1_a, col1_b = st.columns(2)
with col1_a:
    x_in_1 = st.text_input("Spawn 1 X", value=st.session_state["x_1"], key="x_1", placeholder="Type X...")
with col1_b:
    y_in_1 = st.text_input("Spawn 1 Y", value=st.session_state["y_1"], key="y_1", placeholder="Type Y...")
x_1, y_1 = get_coord(x_in_1), get_coord(y_in_1)

if x_1 is not None and y_1 is not None:
    spawns.append((x_1, y_1))
    
    # --- Spawn 2 Row ---
    col2_a, col2_b = st.columns(2)
    with col2_a:
        x_in_2 = st.text_input("Spawn 2 X", value=st.session_state["x_2"], key="x_2", placeholder="Type X...")
    with col2_b:
        y_in_2 = st.text_input("Spawn 2 Y", value=st.session_state["y_2"], key="y_2", placeholder="Type Y...")
    x_2, y_2 = get_coord(x_in_2), get_coord(y_in_2)
    
    if x_2 is not None and y_2 is not None:
        spawns.append((x_2, y_2))
        
        # --- Spawn 3 Row ---
        col3_a, col3_b = st.columns(2)
        with col3_a:
            x_in_3 = st.text_input("Spawn 3 X", value=st.session_state["x_3"], key="x_3", placeholder="Type X...")
        with col3_b:
            y_in_3 = st.text_input("Spawn 3 Y", value=st.session_state["y_3"], key="y_3", placeholder="Type Y...")
        x_3, y_3 = get_coord(x_in_3), get_coord(y_in_3)
        
        if x_3 is not None and y_3 is not None:
            spawns.append((x_3, y_3))
            
            # --- Spawn 4 Row ---
            col4_a, col4_b = st.columns(2)
            with col4_a:
                x_in_4 = st.text_input("Spawn 4 X", value=st.session_state["x_4"], key="x_4", placeholder="Type X...")
            with col4_b:
                y_in_4 = st.text_input("Spawn 4 Y", value=st.session_state["y_4"], key="y_4", placeholder="Type Y...")
            x_4, y_4 = get_coord(x_in_4), get_coord(y_in_4)
            
            if x_4 is not None and y_4 is not None:
                spawns.append((x_4, y_4))
                
                # --- Spawn 5 Row ---
                col5_a, col5_b = st.columns(2)
                with col5_a:
                    x_in_5 = st.text_input("Spawn 5 X", value=st.session_state["x_5"], key="x_5", placeholder="Type X...")
                with col5_b:
                    y_in_5 = st.text_input("Spawn 5 Y", value=st.session_state["y_5"], key="y_5", placeholder="Type Y...")
                x_5, y_5 = get_coord(x_in_5), get_coord(y_in_5)
                if x_5 is not None and y_5 is not None: spawns.append((x_5, y_5))

st.write("---")

# 🎯 Initializing target placeholder parameters
target_x, target_y, true_dist = None, None, None
target_data = pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "Label"])

# ⚡ Run logic calculation if spawns are entered
if len(spawns) > 0:
    x_range = np.arange(0, 1200)
    y_range = np.arange(0, 1200)
    X, Y = np.meshgrid(x_range, y_range)
    X, Y = X.flatten(), Y.flatten()
    valid_mask = np.ones_like(X, dtype=bool)
    
    for sx, sy in spawns: valid_mask &= (np.sqrt((X - sx)**2 + (Y - sy)**2) > 150)
    rivals = [{"X": 319, "Y": 481, "Tag": "TDK"}, {"X": 611, "Y": 551, "Tag": "CoG"}, {"X": 673, "Y": 771, "Tag": "NFM"}]
    for r in rivals: valid_mask &= (np.sqrt((X - r["X"])**2 + (r["Y"] - Y)**2) > 200)
    
    valid_x, valid_y = X[valid_mask], Y[valid_mask]
    if len(valid_x) > 0:
        dist_to_hive = np.sqrt((valid_x - HIVE_X)**2 + (valid_y - HIVE_Y)**2)
        closest_idx = np.argmin(dist_to_hive)
        target_x, target_y = int(valid_x[closest_idx]), int(valid_y[closest_idx])
        true_dist = int(round(dist_to_hive[closest_idx]))
        
        st.success(f"🎯 **Port here and continue spawning:** X: {target_x}, Y: {target_y}")
        st.metric(label="Distance from Hive", value=f"{true_dist} km")
        target_data = pd.DataFrame([{"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯", "Label": f"Target ({target_x},{target_y})"}])
    else:
        st.error("❌ No valid spawning coordinates found with the current constraints.")

# 🗺️ ALWAYS RENDERS MAP DOWN BELOW INSTEAD OF INSIDE THE TARGET CHECK BLOCK
CENTER_X, CENTER_Y = 520, 600
min_x, max_x = CENTER_X - 350, CENTER_X + 350
min_y, max_y = CENTER_Y - 350, CENTER_Y + 350
min_x_iso, max_x_iso = min_x - max_y, max_x - min_y
min_y_iso, max_y_iso = min_x + min_y, max_x + max_y

hive_data = pd.DataFrame([{"X_iso": HIVE_X - HIVE_Y, "Y_iso": HIVE_X + HIVE_Y, "Emoji": "🏰", "Label": f"Hive ({HIVE_X},{HIVE_Y})"}])
throne_data = pd.DataFrame([{"X_iso": 600 - 600, "Y_iso": 600 + 600, "Emoji": "👑", "Label": "Throne (600,600)"}])
temple_data = pd.DataFrame([
    {"X_iso": 300 - 900, "Y_iso": 300 + 900, "Emoji": "🏛️", "Label": "Hunter Temple (300,900)"},
    {"X_iso": 300 - 300, "Y_iso": 300 + 300, "Emoji": "🏛️", "Label": "Harvest Temple (300,300)"},
    {"X_iso": 900 - 300, "Y_iso": 900 + 300, "Emoji": "🏛️", "Label": "Forging Temple (900,300)"}
])

rivals = [{"X": 319, "Y": 481, "Tag": "TDK"}, {"X": 611, "Y": 551, "Tag": "CoG"}, {"X": 673, "Y": 771, "Tag": "NFM"}]
monster_list = [{"X_iso": sx - sy, "Y_iso": sx + sy, "Emoji": "👹", "TextLabel": str(idx), "Label": f"Spawn {idx} ({sx},{sy})"} for idx, (sx, sy) in enumerate(spawns, 1)]
for r in rivals:
    if min_x <= r["X"] <= max_x and min_y <= r["Y"] <= max_y:
        monster_list.append({"X_iso": r["X"] - r["Y"], "Y_iso": r["X"] + r["Y"], "Emoji": "💀", "TextLabel": r["Tag"], "Label": f"{r['Tag']} ({r['X']},{r['Y']})"})
        
spawn_data = pd.DataFrame(monster_list) if monster_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "TextLabel", "Label"])

x_scale = alt.Scale(domain=[min_x_iso, max_x_iso])
y_scale = alt.Scale(domain=[min_y_iso, max_y_iso], reverse=True)

hive_layer = alt.Chart(hive_data).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
throne_layer = alt.Chart(throne_data).mark_text(size=38).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
temple_layer = alt.Chart(temple_data).mark_text(size=32).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
monster_layer = alt.Chart(spawn_data).mark_text(size=28).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
target_layer = alt.Chart(target_data).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])

chart = alt.layer(throne_layer, temple_layer, hive_layer, target_layer, monster_layer).properties(width=700, height=500, background='rgba(0,0,0,0)').configure_view(strokeOpacity=0)
st.altair_chart(chart, use_container_width=True)

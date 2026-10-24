import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# Set mobile layout constraints
st.set_page_config(page_title="Evony Spawn Generator", layout="centered")

st.title("🥷 Evony Spawn Generator")

# Flashy Neon Gold Subtitle Style
st.markdown(
    """
    <div style="
        text-align: left; 
        font-family: 'Arial Black', Gadget, sans-serif; 
        font-size: 22px; 
        font-weight: bold; 
        color: #FFD700; 
        text-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00; 
        padding-bottom: 15px; 
        margin-top: -10px;
    ">
        ✨ BBR is an app writing genius ✨
    </div>
    """, 
    unsafe_allow_html=True
)

st.write("Finds the closest available coordinate to the hive outside a 140km radius of your spawns and 200km away from rivals.")

# Locked-in True Alliance Home Base
HIVE_X, HIVE_Y = 356, 721
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

# Clear All Fields Mechanism
if st.button("🔄 Clear All Fields", type="secondary"):
    for i in range(1, 6):
        st.session_state[f"x_{i}"], st.session_state[f"y_{i}"] = "", ""
    st.rerun()

st.subheader("📍 Active Spawns")

# Ensure clean string values stand in memory defaults
for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = ""
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = ""

spawns = []

def get_coord(val_string):
    try:
        val = int(val_string.strip())
        if 0 <= val <= 1200:
            return val
    except ValueError:
        pass
    return None

# --- Dynamic Cascading Entry Logic ---
x_in_1 = st.text_input("Spawn 1 X", value=st.session_state["x_1"], key="x_1", placeholder="Type X...")
y_in_1 = st.text_input("Spawn 1 Y", value=st.session_state["y_1"], key="y_1", placeholder="Type Y...")
x_1, y_1 = get_coord(x_in_1), get_coord(y_in_1)

if x_1 is not None and y_1 is not None:
    spawns.append((x_1, y_1))
    st.write("---")
    x_in_2 = st.text_input("Spawn 2 X", value=st.session_state["x_2"], key="x_2", placeholder="Type X...")
    y_in_2 = st.text_input("Spawn 2 Y", value=st.session_state["y_2"], key="y_2", placeholder="Type Y...")
    x_2, y_2 = get_coord(x_in_2), get_coord(y_in_2)
    
    if x_2 is not None and y_2 is not None:
        spawns.append((x_2, y_2))
        st.write("---")
        x_in_3 = st.text_input("Spawn 3 X", value=st.session_state["x_3"], key="x_3", placeholder="Type X...")
        y_in_3 = st.text_input("Spawn 3 Y", value=st.session_state["y_3"], key="y_3", placeholder="Type Y...")
        x_3, y_3 = get_coord(x_in_3), get_coord(y_in_3)
        
        if x_3 is not None and y_3 is not None:
            spawns.append((x_3, y_3))
            st.write("---")
            x_in_4 = st.text_input("Spawn 4 X", value=st.session_state["x_4"], key="x_4", placeholder="Type X...")
            y_in_4 = st.text_input("Spawn 4 Y", value=st.session_state["y_4"], key="y_4", placeholder="Type Y...")
            x_4, y_4 = get_coord(x_in_4), get_coord(y_in_4)
            
            if x_4 is not None and y_4 is not None:
                spawns.append((x_4, y_4))
                st.write("---")
                x_in_5 = st.text_input("Spawn 5 X", value=st.session_state["x_5"], key="x_5", placeholder="Type X...")
                y_in_5 = st.text_input("Spawn 5 Y", value=st.session_state["y_5"], key="y_5", placeholder="Type Y...")
                x_5, y_5 = get_coord(x_in_5), get_coord(y_in_5)
                if x_5 is not None and y_5 is not None: spawns.append((x_5, y_5))

st.write("---")

# Tactical Scanning Algorithm
if st.button("🥷 Calculate Next Target", type="primary"):
    x_range = np.arange(0, 1200)
    y_range = np.arange(0, 1200)
    X, Y = np.meshgrid(x_range, y_range)
    X, Y = X.flatten(), Y.flatten()
    valid_mask = np.ones_like(X, dtype=bool)
    
    # Exclusion 1: 140km active spawn zone
    for sx, sy in spawns:
        valid_mask &= (np.sqrt((X - sx)**2 + (Y - sy)**2) > 140)
        
    # Exclusion 2: 200km absolute ban from enemy alliances
    rivals = [
        {"X": 319, "Y": 481, "Tag": "TDK"},
        {"X": 611, "Y": 551, "Tag": "CoG"},
        {"X": 673, "Y": 771, "Tag": "NFM"}
    ]
    for r in rivals:
        valid_mask &= (np.sqrt((X - r["X"])**2 + (Y - r["Y"])**2) > 200)
        
    valid_x, valid_y = X[valid_mask], Y[valid_mask]
    
    if len(valid_x) > 0:
        dist_to_hive = np.sqrt((valid_x - HIVE_X)**2 + (valid_y - HIVE_Y)**2)
        closest_idx = np.argmin(dist_to_hive)
        target_x, target_y = int(valid_x[closest_idx]), int(valid_y[closest_idx])
        true_dist = int(round(dist_to_hive[closest_idx]))
        
        st.success(f"🎯 **Next Best Target Coordinates:** X: {target_x}, Y: {target_y}")
        st.metric(label="Distance from Hive", value=f"{true_dist} km")
        
        # 🎯 OPTIMAL STRATEGIC CENTER: Sets a balanced 650x650 grid window centered at (460, 640)
        CENTER_X, CENTER_Y = 460, 640
        min_x, max_x = CENTER_X - 325, CENTER_X + 325
        min_y, max_y = CENTER_Y - 325, CENTER_Y + 325

        # Calculate isometric visual scaling parameters 
        min_x_iso = min_x - max_y
        max_x_iso = max_x - min_y
        min_y_iso = min_x + min_y
        max_y_iso = max_x + max_y

        hive_data = pd.DataFrame([{"X_iso": HIVE_X - HIVE_Y, "Y_iso": HIVE_X + HIVE_Y, "Emoji": "🏰", "Label": f"Hive ({HIVE_X},{HIVE_Y})"}])
        target_data = pd.DataFrame([{"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯", "Label": f"Target ({target_x},{target_y})"}])
        
        # 👑 Server Throne Dataframe Asset Locked at (600, 600)
        throne_data = pd.DataFrame([{"X_iso": 600 - 600, "Y_iso": 600 + 600, "Emoji": "👑", "Label": "Throne (600,600)"}])
        
        monster_list = [{"X_iso": sx - sy, "Y_iso": sx + sy, "Emoji": "👹", "TextLabel": str(idx), "Label": f"Spawn {idx} ({sx},{sy})"} for idx, (sx, sy) in enumerate(spawns, 1)]
        
        rival_list = []
        for r in rivals:
            rx, ry = r["X"], r["Y"]
            if min_x <= rx <= max_x and min_y <= ry <= max_y:
                monster_list.append({"X_iso": rx - ry, "Y_iso": rx + ry, "Emoji": "💀", "TextLabel": r["Tag"], "Label": f"{r['Tag']} ({rx},{ry})"})
                rival_list.append({"X_iso": rx - ry, "Y_iso": rx + ry})
                
        spawn_data = pd.DataFrame(monster_list) if monster_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "TextLabel", "Label"])
        danger_ring_data = pd.DataFrame(rival_list) if rival_list else pd.DataFrame(columns=["X_iso", "Y_iso"])

        # Isometric Scales
        x_scale = alt.Scale(domain=[min_x_iso, max_x_iso])
        y_scale = alt.Scale(domain=[min_y_iso, max_y_iso], reverse=True)

        hive_layer = alt.Chart(hive_data).mark_text(size=35).encode(
            x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
        )
        target_layer = alt.Chart(target_data).mark_text(size=35).encode(
            x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
        )
        throne_layer = alt.Chart(throne_data).mark_text(size=38).encode(
            x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
        )
        monster_layer = alt.Chart(spawn_data).mark_text(size=28).encode(
            x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
        )
        number_layer = alt.Chart(spawn_data).mark_text(
            size=14, fontWeight='bold', color='#FFD700', dx=20, dy=-12
        ).encode(
            x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='TextLabel:N'
        )
        
        danger_fill_layer = alt.Chart(danger_ring_data).mark_point(
            size=9500, color='#FF1744', opacity=0.08, filled=True
        ).encode(
            x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None)
        )
        
        danger_border_layer = alt.Chart(danger_ring_data).mark_point(
            size=9500, strokeWidth=3.0, color='#FF1744', opacity=0.70, filled=False
        ).encode(
            x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None)
        )

        # Combined layout framework stack with the new Throne layer injected safely
        final_map = alt.layer(danger_fill_layer, danger_border_layer, hive_layer, target_layer, throne_layer, monster_layer, number_layer).properties(width=500, height=450).configure_view(strokeOpacity=0)
        st.write("### 🥷 Ninja Clan Inc.")
        st.altair_chart(final_map, use_container_width=True)
    else:
        st.error("No valid coordinates found on the map grid. Try clearing some old spawns!")

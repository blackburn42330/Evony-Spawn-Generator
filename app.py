import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# Mobile optimization layout
st.set_page_config(page_title="Evony Spawn Generator", layout="centered")

# Custom Dynamic Ninja Graphic Background Layer
st.markdown(
    """
    <style>
    .stApp {
        background-image: linear-gradient(rgba(13, 14, 18, 0.85), rgba(20, 22, 28, 0.9)), 
                          url("https://unsplash.com") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    .block-container {
        background: rgba(13, 14, 18, 0.75);
        padding: 2rem 1.5rem !important;
        border-radius: 16px;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 1rem;
    }
    p, span, label, .stSubheader {
        color: #e2e7f3 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 500;
    }
    hr {
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

st.write("Finds the closest available coordinate to the hive outside a 140km radius of your current spawns.")

# Fixed Hive Coordinates (350, 745)
HIVE_X, HIVE_Y = 350, 745
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

# Reset Functionality
if st.button("🔄 Clear All Fields", type="secondary"):
    for i in range(1, 6):
        st.session_state[f"x_{i}"] = ""
        st.session_state[f"y_{i}"] = ""
    st.rerun()

st.subheader("📍 Active Spawns")

# Set up defaults as empty strings (completely blank text boxes)
for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = ""
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = ""

spawns = []

# Helper function to validate and convert text inputs to real numbers safely
def get_coord(val_string):
    try:
        val = int(val_string.strip())
        if 0 <= val <= 1200:
            return val
    except ValueError:
        pass
    return None

# --- Dynamic Cascading Logic with Clean Text Inputs ---

# Spawn 1: Always Visible
x_in_1 = st.text_input("Spawn 1 X", value=st.session_state["x_1"], key="x_1", placeholder="Type X coordinate...")
y_in_1 = st.text_input("Spawn 1 Y", value=st.session_state["y_1"], key="y_1", placeholder="Type Y coordinate...")
x_1, y_1 = get_coord(x_in_1), get_coord(y_in_1)

if x_1 is not None and y_1 is not None:
    spawns.append((x_1, y_1))
    st.write("---")
    
    # Spawn 2
    x_in_2 = st.text_input("Spawn 2 X", value=st.session_state["x_2"], key="x_2", placeholder="Type X coordinate...")
    y_in_2 = st.text_input("Spawn 2 Y", value=st.session_state["y_2"], key="y_2", placeholder="Type Y coordinate...")
    x_2, y_2 = get_coord(x_in_2), get_coord(y_in_2)
    
    if x_2 is not None and y_2 is not None:
        spawns.append((x_2, y_2))
        st.write("---")
        
        # Spawn 3
        x_in_3 = st.text_input("Spawn 3 X", value=st.session_state["x_3"], key="x_3", placeholder="Type X coordinate...")
        y_in_3 = st.text_input("Spawn 3 Y", value=st.session_state["y_3"], key="y_3", placeholder="Type Y coordinate...")
        x_3, y_3 = get_coord(x_in_3), get_coord(y_in_3)
        
        if x_3 is not None and y_3 is not None:
            spawns.append((x_3, y_3))
            st.write("---")
            
            # Spawn 4
            x_in_4 = st.text_input("Spawn 4 X", value=st.session_state["x_4"], key="x_4", placeholder="Type X coordinate...")
            y_in_4 = st.text_input("Spawn 4 Y", value=st.session_state["y_4"], key="y_4", placeholder="Type Y coordinate...")
            x_4, y_4 = get_coord(x_in_4), get_coord(y_in_4)
            
            if x_4 is not None and y_4 is not None:
                spawns.append((x_4, y_4))
                st.write("---")
                
                # Spawn 5
                x_in_5 = st.text_input("Spawn 5 X", value=st.session_state["x_5"], key="x_5", placeholder="Type X coordinate...")
                y_in_5 = st.text_input("Spawn 5 Y", value=st.session_state["y_5"], key="y_5", placeholder="Type Y coordinate...")
                x_5, y_5 = get_coord(x_in_5), get_coord(y_in_5)
                
                if x_5 is not None and y_5 is not None:
                    spawns.append((x_5, y_5))

st.write("---")

# Calculation Logic
if st.button("🥷 Calculate Next Target", type="primary"):
    x_range = np.arange(max(0, HIVE_X - 200), min(1200, HIVE_X + 200))
    y_range = np.arange(max(0, HIVE_Y - 200), min(1200, HIVE_Y + 200))
    
    X, Y = np.meshgrid(x_range, y_range)
    X = X.flatten()
    Y = Y.flatten()
    
    valid_mask = np.ones_like(X, dtype=bool)
    for sx, sy in spawns:
        dist_to_spawn = np.sqrt((X - sx)**2 + (Y - sy)**2)
        valid_mask &= (dist_to_spawn > 140)
        
    valid_x = X[valid_mask]
    valid_y = Y[valid_mask]
    
    if len(valid_x) > 0:
        dist_to_hive = np.sqrt((valid_x - HIVE_X)**2 + (valid_y - HIVE_Y)**2)
        closest_idx = np.argmin(dist_to_hive)
        
        target_x = int(valid_x[closest_idx])
        target_y = int(valid_y[closest_idx])
        total_dist = dist_to_hive[closest_idx]
        
        st.success(f"🎯 **Next Best Target Coordinates:** X: {target_x}, Y: {target_y}")
        st.metric(label="Distance from Hive", value=f"{total_dist:.1f} km")
        
        # Explicit 400x400 map scaling grid boundary parameters
        min_x, max_x = HIVE_X - 200, HIVE_X + 200
        min_y, max_y = HIVE_Y - 200, HIVE_Y + 200

        # Create numerical arrays for explicit axis line positioning
        x_ticks = list(range(min_x, max_x + 1, 20))
        y_ticks = list(range(min_y, max_y + 1, 20))

        # Dedicated Dataframes
        hive_data = pd.DataFrame([{"X": HIVE_X, "Y": HIVE_Y, "Emoji": "🏰"}])
        target_data = pd.DataFrame([{"X": target_x, "Y": target_y, "Emoji": "🎯"}])
        
        spawn_list = [{"X": sx, "Y": sy, "Emoji": "👹", "Num": str(idx)} for idx, (sx, sy) in enumerate(spawns, 1)]
        spawn_data = pd.DataFrame(spawn_list) if spawn_list else pd.DataFrame(columns=["X", "Y", "Emoji", "Num"])

        # Forced Grid Scale Layout: explicitly pass hardcoded coordinate arrays
        x_axis_config = alt.Axis(values=x_ticks, format='d', grid=True)
        y_axis_config = alt.Axis(values=y_ticks, format='d', grid=True)

        hive_layer = alt.Chart(hive_data).mark_text(size=35).encode(
            x=alt.X('X:Q', scale=alt.Scale(domain=[min_x, max_x])),
            y=alt.Y('Y:Q', scale=alt.Scale(domain=[min_y, max_y]))
        ).transform_calculate(text="datum.Emoji")

        # Fix: explicitly define text mapping step for custom chart visuals
        hive_text = hive_layer.mark_text(size=35).encode(text='text:N')

        target_layer = alt.Chart(target_data).mark_text(size=35).encode(
            x=alt.X('X:Q', scale=alt.Scale(domain=[min_x, max_x])),
            y=alt.Y('Y:Q', scale=alt.Scale(domain=[min_y, max_y]))
        ).transform_calculate(text="datum.Emoji")
        
        target_text = target_layer.mark_text(size=35).encode(text='text:N')

        monster_layer = alt.Chart(spawn_data).mark_text(size=28).encode(
            x=alt.X('X:Q', scale=alt.Scale(domain=[min_x, max_x]), axis=x_axis_config),
            y=alt.Y('Y:Q', scale=alt.Scale(domain=[min_y, max_y]), axis=y_axis_config)
        ).transform_calculate(text="datum.Emoji")
        
        monster_text = monster_layer.mark_text(size=28).encode(text='text:N')

        number_layer = alt.Chart(spawn_data).mark_text(
            size=16, fontWeight='bold', color='#FFD700', dx=15, dy=-12
        ).encode(
            x=alt.X('X:Q', scale=alt.Scale(domain=[min_x, max_x])),
            y=alt.Y('Y:Q', scale=alt.Scale(domain=[min_y, max_y])),
            text='Num:N'
        )

        # Merge layers onto the final map frame
        final_map = alt.layer(hive_text, target_text, monster_text, number_layer).properties(
            width=500, height=450
        ).configure_view(strokeOpacity=0)

        st.write("### 🥷 Ninja Clan Inc.")
        st.altair_chart(final_map, use_container_width=True)

    else:
        st.error("No valid coordinates found in the search sector. Try clearing some old spawns!")

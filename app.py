import streamlit as st
import numpy as np

# Mobile optimization layout
st.set_page_config(page_title="Evony Spawn Generator", layout="centered")
st.title("🏹 Evony Spawn Generator")
st.write("Finds the closest available coordinate to the hive outside a 150km radius of your current spawns.")

# Fixed Hive Coordinates
HIVE_X, HIVE_Y = 356, 721
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

# Reset Functionality
if st.button("🔄 Clear All Fields", type="secondary"):
    for i in range(1, 6):
        st.session_state[f"x_{i}"] = 0
        st.session_state[f"y_{i}"] = 0
    st.rerun()

# UI Layout for Inputs
st.subheader("📍 Active Spawns")

spawns = []
for i in range(1, 6):
    cols = st.columns(2)
    # Set default values if not already present in session memory
    if f"x_{i}" not in st.session_state:
        st.session_state[f"x_{i}"] = 0
    if f"y_{i}" not in st.session_state:
        st.session_state[f"y_{i}"] = 0
        
    with cols[0]:
        x_val = st.number_input(f"Spawn {i} X", min_value=0, max_value=1200, step=1, key=f"x_{i}")
    with cols[1]:
        y_val = st.number_input(f"Spawn {i} Y", min_value=0, max_value=1200, step=1, key=f"key_{i}" if False else f"y_{i}")
        
    if x_val > 0 and y_val > 0:
        spawns.append((x_val, y_val))

st.write("---")

# Calculation Logic
if st.button("🔥 Calculate Next Target", type="primary"):
    # Generate full map space around hive to keep search hyper-fast but broad (400x400 area)
    x_range = np.arange(max(0, HIVE_X - 200), min(1200, HIVE_X + 200))
    y_range = np.arange(max(0, HIVE_Y - 200), min(1200, HIVE_Y + 200))
    
    # Create coordinate grid mesh
    X, Y = np.meshgrid(x_range, y_range)
    X = X.flatten()
    Y = Y.flatten()
    
    # Filter out points within 150km of any active spawn
    valid_mask = np.ones_like(X, dtype=bool)
    for sx, sy in spawns:
        dist_to_spawn = np.sqrt((X - sx)**2 + (Y - sy)**2)
        valid_mask &= (dist_to_spawn > 150)
        
    valid_x = X[valid_mask]
    valid_y = Y[valid_mask]
    
    if len(valid_x) > 0:
        # Find the point closest to the Hive
        dist_to_hive = np.sqrt((valid_x - HIVE_X)**2 + (valid_y - HIVE_Y)**2)
        closest_idx = np.argmin(dist_to_hive)
        
        target_x = valid_x[closest_idx]
        target_y = valid_y[closest_idx]
        total_dist = dist_to_hive[closest_idx]
        
        st.success(f"🎯 **Next Best Target Coordinates:** X: {target_x}, Y: {target_y}")
        st.metric(label="Distance from Hive", value=f"{total_dist:.1f} km")
    else:
        st.error("No valid coordinates found in the search sector. Try clearing some old spawns!")


import streamlit as st
import numpy as np

# Mobile optimization layout
st.set_page_config(page_title="Evony Spawn Generator", layout="centered")

# Custom Dynamic Ninja Graphic Background Layer
st.markdown(
    """
    <style>
    /* Injects an optimized dark high-contrast ninja image as a fixed frame background */
    .stApp {
        background-image: linear-gradient(rgba(13, 14, 18, 0.85), rgba(20, 22, 28, 0.9)), 
                          url("https://unsplash.com") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    
    /* Transparent layered component sheets for high font readability */
    .block-container {
        background: rgba(13, 14, 18, 0.75);
        padding: 2rem 1.5rem !important;
        border-radius: 16px;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 1rem;
    }

    /* Input title contrast stabilization adjustments */
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
        st.session_state[f"x_{i}"] = 0
        st.session_state[f"y_{i}"] = 0
    st.rerun()

st.subheader("📍 Active Spawns")

# Set up defaults in session state if they don't exist
for i in range(1, 6):
    if f"x_{i}" not in st.session_state:
        st.session_state[f"x_{i}"] = 0
    if f"y_{i}" not in st.session_state:
        st.session_state[f"y_{i}"] = 0

spawns = []

# --- Dynamic Row Logic ---

# Spawn 1: Always Visible
x_1 = st.number_input("Spawn 1 X", min_value=0, max_value=1200, value=st.session_state["x_1"], key="x_1")
y_1 = st.number_input("Spawn 1 Y", min_value=0, max_value=1200, value=st.session_state["y_1"], key="y_1")
if x_1 > 0 and y_1 > 0: 
    spawns.append((x_1, y_1))
    
    # Spawn 2: Visible only if Spawn 1 has data
    st.write("---")
    x_2 = st.number_input("Spawn 2 X", min_value=0, max_value=1200, value=st.session_state["x_2"], key="x_2")
    y_2 = st.number_input("Spawn 2 Y", min_value=0, max_value=1200, value=st.session_state["y_2"], key="y_2")
    if x_2 > 0 and y_2 > 0:
        spawns.append((x_2, y_2))
        
        # Spawn 3: Visible only if Spawn 2 has data
        st.write("---")
        x_3 = st.number_input("Spawn 3 X", min_value=0, max_value=1200, value=st.session_state["x_3"], key="x_3")
        y_3 = st.number_input("Spawn 3 Y", min_value=0, max_value=1200, value=st.session_state["y_3"], key="y_3")
        if x_3 > 0 and y_3 > 0:
            spawns.append((x_3, y_3))
            
            # Spawn 4: Visible only if Spawn 3 has data
            st.write("---")
            x_4 = st.number_input("Spawn 4 X", min_value=0, max_value=1200, value=st.session_state["x_4"], key="x_4")
            y_4 = st.number_input("Spawn 4 Y", min_value=0, max_value=1200, value=st.session_state["y_4"], key="y_4")
            if x_4 > 0 and y_4 > 0:
                spawns.append((x_4, y_4))
                
                # Spawn 5: Visible only if Spawn 4 has data
                st.write("---")
                x_5 = st.number_input("Spawn 5 X", min_value=0, max_value=1200, value=st.session_state["x_5"], key="x_5")
                y_5 = st.number_input("Spawn 5 Y", min_value=0, max_value=1200, value=st.session_state["y_5"], key="y_5")
                if x_5 > 0 and y_5 > 0:
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
        
        target_x = valid_x[closest_idx]
        target_y = valid_y[closest_idx]
        total_dist = dist_to_hive[closest_idx]
        
        st.success(f"🎯 **Next Best Target Coordinates:** X: {target_x}, Y: {target_y}")
        st.metric(label="Distance from Hive", value=f"{total_dist:.1f} km")
    else:
        st.error("No valid coordinates found in the search sector. Try clearing some old spawns!")

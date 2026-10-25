import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Evony Full Map Territory Overlaps", layout="centered")
st.title("🏰 Evony Alliance Boundary Overlaps")

st.markdown("""
    <div style='text-align: left; font-family: "Arial Black", Gadget, sans-serif; font-size: 22px; font-weight: bold; color: #FFD700; text-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00; padding-bottom: 15px; margin-top: -10px;'>✨ BBR is an app writing genius ✨</div>
    <style>
    /* Force specific coordinate block columns to stay locked horizontally closely together on mobile */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: flex-start !important;
        gap: 8px !important;
    }
    div[data-testid="column"] {
        flex: 0 0 auto !important;
        width: auto !important;
    }
    </style>
""", unsafe_allow_html=True)

st.write("Visualizes the entire 1200 x 1200 server canvas centered at the Throne (600,600). Overlapping territory controls are flagged dynamically in red.")

# --- Real-time Interactive Input Grid ---
st.subheader("⚙️ Map Settings")
col_input, col_spacer = st.columns([2.5, 3], gap="small")
with col_input:
    radius = st.number_input("Territory Bubble Radius (km)", min_value=10, max_value=500, value=175, step=5, help="Adjust to scale territory sizes dynamically")

st.write("---")
st.subheader("📍 Alliance Hive Coordinates")

default_alliances = [
    {"Tag": "NCI", "X": 356, "Y": 721},
    {"Tag": "TDK", "X": 319, "Y": 481},
    {"Tag": "CoG", "X": 611, "Y": 551},
    {"Tag": "NFM", "X": 673, "Y": 771}
]

alliances = []

for a in default_alliances:
    tag = a["Tag"]
    if f"map_x_{tag}" not in st.session_state: st.session_state[f"map_x_{tag}"] = a["X"]
    if f"map_y_{tag}" not in st.session_state: st.session_state[f"map_y_{tag}"] = a["Y"]
    
    col_lbl, col_x, col_y = st.columns([1.2, 1.5, 1.5], gap="small")
    with col_lbl:
        st.markdown(f"<div style='padding-top: 6px; font-weight: bold; font-size:15px; white-space: nowrap;'>[{tag}] Hive</div>", unsafe_allow_html=True)
    with col_x:
        x_val = st.number_input(f"{tag}_X", min_value=0, max_value=1200, step=1, value=st.session_state[f"map_x_{tag}"], key=f"map_x_{tag}", label_visibility="collapsed", placeholder="X...")
    with col_y:
        y_val = st.number_input(f"{tag}_Y", min_value=0, max_value=1200, step=1, value=st.session_state[f"map_y_{tag}"], key=f"map_y_{tag}", label_visibility="collapsed", placeholder="Y...")
    
    alliances.append({"X": int(x_val), "Y": int(y_val), "Tag": tag})

st.write("---")

# 🌍 FULL 1200x1200SERVER COORDINATE CONFIGURATION
min_x, max_x = 0, 1200
min_y, max_y = 0, 1200

# Translate 2D edges to exact full-scale isometric view limits
min_x_iso, max_x_iso = min_x - max_y, max_x - min_y
min_y_iso, max_y_iso = min_x + min_y, max_x + max_y

# Static map elements
throne_data = pd.DataFrame([{"X_iso": 600 - 600, "Y_iso": 600 + 600, "Emoji": "👑", "Label": "Throne (600,600)"}])
temple_data = pd.DataFrame([
    {"X_iso": 300 - 900, "Y_iso": 300 + 900, "Emoji": "🏛️", "Label": "Hunter Temple (300,900)"},
    {"X_iso": 300 - 300, "Y_iso": 300 + 300, "Emoji": "🏛️", "Label": "Harvest Temple (300,300)"},
    {"X_iso": 900 - 300, "Y_iso": 900 + 300, "Emoji": "🏛️", "Label": "Forging Temple (900,300)"}
])

# 🔵 Optimized processing array intervals to handle full server scales instantly
x_grid = np.linspace(min_x, max_x, 250)
y_grid = np.linspace(min_y, max_y, 250)
X, Y = np.meshgrid(x_grid, y_grid)
X, Y = X.flatten(), Y.flatten()

coverage_count = np.zeros_like(X, dtype=int)
for a in alliances:
    dist = np.sqrt((X - a["X"])**2 + (Y - a["Y"])**2)
    coverage_count[dist <= radius] += 1

overlap_mask = (coverage_count >= 2)
blue_mask = (coverage_count == 1)

overlap_x, overlap_y = X[overlap_mask], Y[overlap_mask]
blue_x, blue_y = X[blue_mask], Y[blue_mask]

overlap_df = pd.DataFrame({"X_iso": overlap_x - overlap_y, "Y_iso": overlap_x + overlap_y})
bubble_df = pd.DataFrame({"X_iso": blue_x - blue_y, "Y_iso": blue_x + blue_y})
castle_df = pd.DataFrame([{"X_iso": a["X"] - a["Y"], "Y_iso": a["X"] + a["Y"], "Emoji": "🏰", "Tag": a["Tag"], "Label": f"[{a['Tag']}] Hive ({a['X']},{a['Y']})"} for a in alliances])

x_scale = alt.Scale(domain=[min_x_iso, max_x_iso])
y_scale = alt.Scale(domain=[min_y_iso, max_y_iso], reverse=True)

# 🗺️ Render Layout Layers with size adjustments for full server view
blue_bubble_layer = alt.Chart(bubble_df).mark_square(color='rgba(30, 144, 255, 0.15)', size=10).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None)
)

red_overlap_layer = alt.Chart(overlap_df).mark_square(color='rgba(255, 0, 0, 0.4)', size=10).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None)
)

throne_layer = alt.Chart(throne_data).mark_text(size=32).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
)

temple_layer = alt.Chart(temple_data).mark_text(size=26).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
)

castle_layer = alt.Chart(castle_df).mark_text(size=28).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
)

tag_layer = alt.Chart(castle_df).mark_text(size=12, fontWeight='bold', color='white', dx=20, dy=-10).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Tag:N', tooltip=['Label:N']
)

chart = alt.layer(blue_bubble_layer, red_overlap_layer, throne_layer, temple_layer, castle_layer, tag_layer).properties(
    width=700, height=500, background='rgba(0,0,0,0)'
).configure_view(strokeOpacity=0)

st.altair_chart(chart, use_container_width=True)

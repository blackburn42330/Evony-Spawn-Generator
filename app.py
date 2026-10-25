import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Evony Alliance Territory Overlaps", layout="centered")
st.title("🏰 Evony Alliance Boundary Overlaps")

st.markdown("""
    <div style='text-align: left; font-family: "Arial Black", Gadget, sans-serif; font-size: 22px; font-weight: bold; color: #FFD700; text-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00; padding-bottom: 15px; margin-top: -10px;'>✨ BBR is an app writing genius ✨</div>
""", unsafe_allow_html=True)

st.write("Visualizes all major alliance hives using a custom territory radius bubble. Overlapping control regions are dynamically flagged in red shade zones.")

# --- Real-time Interactive Input Grid ---
st.subheader("⚙️ Map Settings")
# Forces a shrunken side-by-side arrangement natively on mobile phones and tablets
col_input, col_spacer = st.columns([2, 3], gap="small")
with col_input:
    radius = st.number_input("Territory Bubble Radius (km)", min_value=10, max_value=500, value=175, step=5, help="Adjust to scale territory sizes dynamically")

# Alliance dataset with updated NCI tag and text label tracking strings
alliances = [
    {"X": 356, "Y": 721, "Tag": "NCI"},
    {"X": 319, "Y": 481, "Tag": "TDK"},
    {"X": 611, "Y": 551, "Tag": "CoG"},
    {"X": 673, "Y": 771, "Tag": "NFM"}
]

# Coordinate bounds configuration
CENTER_X, CENTER_Y = 520, 600
min_x, max_x = CENTER_X - 350, CENTER_X + 350
min_y, max_y = CENTER_Y - 350, CENTER_Y + 350
min_x_iso, max_x_iso = min_x - max_y, max_x - min_y
min_y_iso, max_y_iso = min_x + min_y, max_x + max_y

# Static map elements
throne_data = pd.DataFrame([{"X_iso": 600 - 600, "Y_iso": 600 + 600, "Emoji": "👑", "Label": "Throne (600,600)"}])
temple_data = pd.DataFrame([
    {"X_iso": 300 - 900, "Y_iso": 300 + 900, "Emoji": "🏛️", "Label": "Hunter Temple (300,900)"},
    {"X_iso": 300 - 300, "Y_iso": 300 + 300, "Emoji": "🏛️", "Label": "Harvest Temple (300,300)"},
    {"X_iso": 900 - 300, "Y_iso": 900 + 300, "Emoji": "🏛️", "Label": "Forging Temple (900,300)"}
])

# 🔵 High-resolution vector engine to compute boundary intersections dynamically
x_grid = np.linspace(min_x, max_x, 180)
y_grid = np.linspace(min_y, max_y, 180)
X, Y = np.meshgrid(x_grid, y_grid)
X, Y = X.flatten(), Y.flatten()

# Counts overlap matrices matching the user-defined slider/number inputs parameters
coverage_count = np.zeros_like(X, dtype=int)
for a in alliances:
    dist = np.sqrt((X - a["X"])**2 + (Y - a["Y"])**2)
    coverage_count[dist <= radius] += 1

# Partition vector masks based on coverage thresholds
overlap_mask = (coverage_count >= 2)
blue_mask = (coverage_count == 1)

# Cast valid array locations to isometric maps
overlap_x, overlap_y = X[overlap_mask], Y[overlap_mask]
blue_x, blue_y = X[blue_mask], Y[blue_mask]

# Pack variables into structured layout dataframes
overlap_df = pd.DataFrame({"X_iso": overlap_x - overlap_y, "Y_iso": overlap_x + overlap_y})
bubble_df = pd.DataFrame({"X_iso": blue_x - blue_y, "Y_iso": blue_x + blue_y})
castle_df = pd.DataFrame([{"X_iso": a["X"] - a["Y"], "Y_iso": a["X"] + a["Y"], "Emoji": "🏰", "Tag": a["Tag"], "Label": f"[{a['Tag']}] Hive ({a['X']},{a['Y']})"} for a in alliances])

x_scale = alt.Scale(domain=[min_x_iso, max_x_iso])
y_scale = alt.Scale(domain=[min_y_iso, max_y_iso], reverse=True)

# 🗺️ Stitch all visual chart layers together
blue_bubble_layer = alt.Chart(bubble_df).mark_square(color='rgba(30, 144, 255, 0.15)', size=18).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None)
)

red_overlap_layer = alt.Chart(overlap_df).mark_square(color='rgba(255, 0, 0, 0.4)', size=18).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None)
)

throne_layer = alt.Chart(throne_data).mark_text(size=38).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
)

temple_layer = alt.Chart(temple_data).mark_text(size=32).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
)

# 🏰 Castle icons layer
castle_layer = alt.Chart(castle_df).mark_text(size=35).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N']
)

# 🏷️ Alliance tag text layer offsets text labels clearly to the top right of the castles
tag_layer = alt.Chart(castle_df).mark_text(size=14, fontWeight='bold', color='white', dx=24, dy=-12).encode(
    x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Tag:N', tooltip=['Label:N']
)

# Compile mapping layout stack
chart = alt.layer(blue_bubble_layer, red_overlap_layer, throne_layer, temple_layer, castle_layer, tag_layer).properties(
    width=700, height=500, background='rgba(0,0,0,0)'
).configure_view(strokeOpacity=0)

st.altair_chart(chart, use_container_width=True)

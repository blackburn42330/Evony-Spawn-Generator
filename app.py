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
    
    /* 📉 Make the interactive table row elements highly compact to eliminate blank space */
    div[data-testid="stDataEditor"] > div { margin-bottom: 0px !important; padding-bottom: 0px !important; }
    </style>
""", unsafe_allow_html=True)

st.write("Finds the closest available coordinate to the hive outside a 150km radius of your spawns and 200km away from rivals.")
st.markdown("### 📋 Instructions:\n1. Click any cell in the table below to type your spawn coordinates.\n2. The fields are locked side-by-side so they fit perfectly on phone layouts!\n3. The app will automatically calculate your safe location to teleport to instantly as you type!")

HIVE_X, HIVE_Y = 356, 721
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

# Baseline initialization tracking dataset parameters
if "spawn_df" not in st.session_state:
    st.session_state.spawn_df = pd.DataFrame([
        {"Spawn": "Spawn 1", "X Coordinate": None, "Y Coordinate": None},
        {"Spawn": "Spawn 2", "X Coordinate": None, "Y Coordinate": None},
        {"Spawn": "Spawn 3", "X Coordinate": None, "Y Coordinate": None},
        {"Spawn": "Spawn 4", "X Coordinate": None, "Y Coordinate": None},
        {"Spawn": "Spawn 5", "X Coordinate": None, "Y Coordinate": None}
    ])

if st.button("🗑️ Clear All Fields"):
    st.session_state.spawn_df = pd.DataFrame([
        {"Spawn": "Spawn 1", "X Coordinate": None, "Y Coordinate": None},
        {"Spawn": "Spawn 2", "X Coordinate": None, "Y Coordinate": None},
        {"Spawn": "Spawn 3", "X Coordinate": None, "Y Coordinate": None},
        {"Spawn": "Spawn 4", "X Coordinate": None, "Y Coordinate": None},
        {"Spawn": "Spawn 5", "X Coordinate": None, "Y Coordinate": None}
    ])
    st.rerun()

st.subheader("📍 Active Spawns")

# 📊 NATIVE MOBILE-LOCKED COORDINATE INPUT GRID
# Locks X and Y completely side-by-side and returns active key data streams instantly
edited_df = st.data_editor(
    st.session_state.spawn_df,
    column_config={
        "Spawn": st.column_config.TextColumn("Label", disabled=True, width="small"),
        "X Coordinate": st.column_config.NumberColumn("X Coordinate", min_value=0, max_value=1200, format="%d", help="Type X..."),
        "Y Coordinate": st.column_config.NumberColumn("Y Coordinate", min_value=0, max_value=1200, format="%d", help="Type Y...")
    },
    disabled=["Spawn"],
    hide_index=True,
    use_container_width=True,
    key="spawn_editor"
)
st.session_state.spawn_df = edited_df

# Extract user input points from rows smoothly
spawns = []
for index, row in edited_df.iterrows():
    x_val = row["X Coordinate"]
    y_val = row["Y Coordinate"]
    if pd.notna(x_val) and pd.notna(y_val):
        spawns.append((int(x_val), int(y_val)))

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
    for r in rivals: valid_mask &= (np.sqrt((X - r["X"])**2 + (r["Y"] - Y)**2) > 200)
    
    valid_x, valid_y = X[valid_mask], Y[valid_mask]
    if len(valid_x) > 0:
        dist_to_hive = np.sqrt((valid_x - HIVE_X)**2 + (valid_y - HIVE_Y)**2)
        closest_idx = np.argmin(dist_to_hive)
        target_x, target_y = int(valid_x[closest_idx]), int(valid_y[closest_idx])
        true_dist = int(round(dist_to_hive[closest_idx]))
        
        st.success(f"🎯 **Teleport here and continue spawning:** X: {target_x}, Y: {target_y} ({true_dist} km from Hive)")
        
        st.write("**Spawn Distances from Hive:**")
        dist_strings = []
        for idx, (sx, sy) in enumerate(spawns, 1):
            s_dist = int(round(np.sqrt((sx - HIVE_X)**2 + (sy - HIVE_Y)**2)))
            dist_strings.append(f"**Spawn {idx}:** {s_dist} km")
        st.write(" | ".join(dist_strings))
                
        target_data = pd.DataFrame([{"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯", "Label": f"Target ({target_x},{target_y})"}])
    else: st.error("❌ No valid spawning coordinates found with the current constraints.")

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

monster_list = [{"X_iso": sx - sy, "Y_iso": sx + sy, "Emoji": "👹", "TextLabel": str(idx), "Label": f"Spawn {idx} ({sx},{sy})"} for idx, (sx, sy) in enumerate(spawns, 1)]
rival_list = []
for r in rivals:
    if min_x <= r["X"] <= max_x and min_y <= r["Y"] <= max_y:
        monster_list.append({"X_iso": r["X"] - r["Y"], "Y_iso": r["X"] + r["Y"], "Emoji": "💀", "TextLabel": r["Tag"], "Label": f"{r['Tag']} ({r['X']},{r['Y']})"})
        rival_list.append({"X_iso": r["X"] - r["Y"], "Y_iso": r["X"] + r["Y"], "Label": f"{r['Tag']} Danger (200km)"})
        
spawn_data = pd.DataFrame(monster_list) if monster_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "TextLabel", "Label"])
danger_data = pd.DataFrame(rival_list) if rival_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Label"])

x_scale, y_scale = alt.Scale(domain=[min_x_iso, max_x_iso]), alt.Scale(domain=[min_y_iso, max_y_iso], reverse=True)

danger_zone_layer = alt.Chart(danger_data).mark_point(color='rgba(255, 0, 0, 0.12)', stroke='#8B0000', strokeWidth=2, filled=True, size=16500).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), tooltip=['Label:N'])
hive_layer = alt.Chart(hive_data).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
throne_layer = alt.Chart(throne_data).mark_text(size=38).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
temple_layer = alt.Chart(temple_data).mark_text(size=32).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
target_layer = alt.Chart(target_data).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
monster_emoji_layer = alt.Chart(spawn_data).mark_text(size=28).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
monster_text_layer = alt.Chart(spawn_data).mark_text(size=14, fontWeight='bold', color='white', dx=22, dy=-10).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='TextLabel:N', tooltip=['Label:N'])

chart = alt.layer(danger_zone_layer, throne_layer, temple_layer, hive_layer, target_layer, monster_emoji_layer, monster_text_layer).properties(width=700, height=500, background='rgba(0,0,0,0)').configure_view(strokeOpacity=0)
st.altair_chart(chart, use_container_width=True)

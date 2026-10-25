import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import streamlit.components.v1 as cmps

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

st.write("Finds the closest available coordinate to the hive outside a 150km radius of your spawns and 200km away from rivals.")
st.markdown("### 📋 Instructions:\n1. Enter your coordinates into the side-by-side boxes below.\n2. Tap anywhere outside the fields or press enter to trigger calculations instantly!\n3. The app will automatically calculate your safe location to teleport to as you type!")

HIVE_X, HIVE_Y = 356, 721
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

# Baseline dynamic state tracking parameters initialization
for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = ""
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = ""

if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6): st.session_state[f"x_{i}"], st.session_state[f"y_{i}"] = "", ""
    st.rerun()

st.subheader("📍 Active Spawns")

rows_html = ""
for i in range(1, 6):
    is_hidden = "hidden" if i > 1 and not (st.session_state[f'x_{i-1}'] and st.session_state[f'y_{i-1}']) else ""
    rows_html += f"""
    <div class="spawn-row {is_hidden}" id="row_{i}">
        <div class="label">Spawn {i}</div>
        <input type="number" class="input-box" id="x_{i}" placeholder="X..." value="{st.session_state[f'x_{i}']}" onchange="updateData({i})">
        <input type="number" class="input-box" id="y_{i}" placeholder="Y..." value="{st.session_state[f'y_{i}']}" onchange="updateData({i})">
    </div>"""

widget_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    html, body {{ font-family: sans-serif; background-color: transparent; color: white; margin: 0; padding: 0; }}
    .spawn-row {{ display: flex; align-items: center; margin-bottom: 12px; }}
    .label {{ width: 75px; font-weight: bold; font-size: 14px; color: #E0E0E0; }}
    .input-box {{ width: 85px; padding: 8px 10px; background: #1E293B; border: 1px solid #475569; border-radius: 6px; color: white; font-size: 15px; margin-right: 10px; outline: none; }}
    .input-box:focus {{ border-color: #FFD700; box-shadow: 0 0 5px rgba(255,215,0,0.3); }}
    .hidden {{ display: none !important; }}
</style>
</head>
<body>
    {rows_html}
    <script>
    function updateData(rowId) {{
        var xVal = document.getElementById('x_' + rowId).value;
        var yVal = document.getElementById('y_' + rowId).value;
        if(xVal && yVal && rowId < 5) {{
            var nextRow = document.getElementById('row_' + (rowId + 1));
            if(nextRow) nextRow.classList.remove('hidden');
        }}
        // Instantly transmits coordinate data objects up to the main Python layout engine
        Streamlit.setComponentValue({{row: rowId, x: xVal, y: yVal}});
    }}
    </script>
</body>
</html>"""

# Render shrunken input fields layer matching the visual aspect ratios of your photo mockup
response = cmps.html(widget_html, height=185, scrolling=False)

# Intercept row variables and update global tracking states instantly
if response and isinstance(response, dict):
    r = response.get('row')
    st.session_state[f"x_{r}"] = response.get('x', "")
    st.session_state[f"y_{r}"] = response.get('y', "")
    st.rerun()

spawns = []
def get_coord(val_string):
    try:
        if val_string and str(val_string).strip():
            val = int(str(val_string).strip())
            if 0 <= val <= 1200: return val
    except ValueError: pass
    return None

for i in range(1, 6):
    x_val = get_coord(st.session_state[f"x_{i}"])
    y_val = get_coord(st.session_state[f"y_{i}"])
    if x_val is not None and y_val is not None:
        spawns.append((x_val, y_val))

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

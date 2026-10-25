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
st.markdown("### 📋 Instructions:\n1. Enter your coordinates into the side-by-side boxes below.\n2. Tap anywhere outside the input fields to trigger the calculation instantly!\n3. The app will automatically calculate your safe location to teleport to as you type!")

HIVE_X, HIVE_Y = 356, 721
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = st.query_params.get(f"x_{i}", "")
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = st.query_params.get(f"y_{i}", "")

if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6):
        st.session_state[f"x_{i}"], st.session_state[f"y_{i}"] = "", ""
        if f"x_{i}" in st.query_params: del st.query_params[f"x_{i}"]
        if f"y_{i}" in st.query_params: del st.query_params[f"y_{i}"]
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
    html, body {{ height: 100%; width: 100%; font-family: sans-serif; background-color: transparent; color: white; margin: 0; padding: 0; }}
    .container {{ height: 100%; width: 100%; }}
    .spawn-row {{ display: flex; align-items: center; margin-bottom: 12px; }}
    .label {{ width: 75px; font-weight: bold; font-size: 14px; color: #E0E0E0; }}
    .input-box {{ width: 85px; padding: 8px 10px; background: #1E293B; border: 1px solid #475569; border-radius: 6px; color: white; font-size: 15px; margin-right: 10px; outline: none; }}
    .input-box:focus {{ border-color: #FFD700; box-shadow: 0 0 5px rgba(255,215,0,0.3); }}
    .hidden {{ display: none !important; }}
</style>
</head>
<body>
    <div class="container" id="bg_container">
        {rows_html}
    </div>
    <script>
    function updateData(rowId) {{
        var x = document.getElementById('x_' + rowId).value;
        var y = document.getElementById('y_' + rowId).value;
        if(x && y && rowId < 5) {{
            var n = document.getElementById('row_' + (rowId + 1));
            if(n) n.classList.remove('hidden');
        }}
        window.parent.postMessage({{type: 'streamlit:setComponentValue', value: {{key: 'sp_up', row: rowId, x: x, y: y}}}}, '*');
    }}
    
    // Forces input boxes to blur and update if a user taps anywhere outside the text fields
    document.getElementById('bg_container').addEventListener('click', function(e) {{
        if (e.target.tagName !== 'INPUT') {{
            var inputs = document.getElementsByTagName('input');
            for (var i = 0; i < inputs.length; i++) {{
                inputs[i].blur();
            }}
        }}
    }});
    </script>
</body>
</html>"""

response = cmps.html(widget_html, height=185, scrolling=False)

if response and isinstance(response, dict) and response.get('key') == 'sp_up':
    r, x_v, y_v = response.get('row'), response.get('x'), response.get('y')
    st.session_state[f"x_{r}"], st.session_state[f"y_{r}"] = x_v, y_v
    st.query_params[f"x_{r}"], st.query_params[f"y_{r}"] = x_v, y_v
    st.rerun()

spawns = []
for i in range(1, 6):
    try:
        x_s, y_s = str(st.session_state[f"x_{i}"]).strip(), str(st.session_state[f"y_{i}"]).strip()
        if x_s and y_s and 0 <= int(x_s) <= 1200 and 0 <= int(y_s) <= 1200:
            spawns.append((int(x_s), int(y_s)))
    except ValueError: pass

target_x, target_y, true_dist = None, None, None
target_data = pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji"])
rivals = [{"X": 319, "Y": 481, "Tag": "TDK"}, {"X": 611, "Y": 551, "Tag": "CoG"}, {"X": 673, "Y": 771, "Tag": "NFM"}]

if len(spawns) > 0:
    X, Y = np.meshgrid(np.arange(0, 1200), np.arange(0, 1200))
    X, Y = X.flatten(), Y.flatten()
    v_mask = np.ones_like(X, dtype=bool)
    for sx, sy in spawns: v_mask &= (np.sqrt((X - sx)**2 + (Y - sy)**2) > 150)
    for r in rivals: v_mask &= (np.sqrt((X - r["X"])**2 + (r["Y"] - Y)**2) > 200)
    v_x, v_y = X[v_mask], Y[v_mask]
    if len(v_x) > 0:
        d_hive = np.sqrt((v_x - HIVE_X)**2 + (v_y - HIVE_Y)**2)
        idx = np.argmin(d_hive)
        target_x, target_y, true_dist = int(v_x[idx]), int(v_y[idx]), int(round(d_hive[idx]))
        st.success(f"🎯 **Teleport here and continue spawning:** X: {target_x}, Y: {target_y} ({true_dist} km from Hive)")
        st.write("**Spawn Distances from Hive:**")
        st.write(" | ".join([f"**Spawn {idx}:** {int(round(np.sqrt((sx - HIVE_X)**2 + (sy - HIVE_Y)**2)))} km" for idx, (sx, sy) in enumerate(spawns, 1)]))
        target_data = pd.DataFrame([{"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯"}])
    else: st.error("❌ No valid spawning coordinates found.")

hive_df = pd.DataFrame([{"X_iso": HIVE_X - HIVE_Y, "Y_iso": HIVE_X + HIVE_Y, "Emoji": "🏰"}])
throne_df = pd.DataFrame([{"X_iso": 0, "Y_iso": 1200, "Emoji": "👑"}])
temple_df = pd.DataFrame([{"X_iso": -600, "Y_iso": 1200, "Emoji": "🏛️"}, {"X_iso": 0, "Y_iso": 600, "Emoji": "🏛️"}, {"X_iso": 600, "Y_iso": 1200, "Emoji": "🏛️"}])

m_list, r_list = [], []
for idx, (sx, sy) in enumerate(spawns, 1): m_list.append({"X_iso": sx - sy, "Y_iso": sx + sy, "Emoji": "👹", "Lbl": str(idx)})
for r in rivals:
    if 170 <= r["X"] <= 870 and 250 <= r["Y"] <= 950:
        m_list.append({"X_iso": r["X"] - r["Y"], "Y_iso": r["X"] + r["Y"], "Emoji": "💀", "Lbl": r["Tag"]})
        r_list.append({"X_iso": r["X"] - r["Y"], "Y_iso": r["X"] + r["Y"]})

sp_df = pd.DataFrame(m_list) if m_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "Lbl"])
dg_df = pd.DataFrame(r_list) if r_list else pd.DataFrame(columns=["X_iso", "Y_iso"])

# 🗺️ Fixed map scale constraints to resolve chart schema validation error
x_sc, y_scale = alt.Scale(domain=[-780, 620]), alt.Scale(domain=[420, 1820], reverse=True)
def mk_lyr(df, txt, sz, dx=0, dy=0, c=None, st_c=None, sw=0):
    o = alt.Chart(df).encode(x=alt.X('X_iso:Q', scale=x_sc, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None))
    if c and st_c: return o.mark_point(color=c, stroke=st_c, strokeWidth=sw, filled=True, size=16500)
    return o.mark_text(size=sz, dx=dx, dy=dy, fontWeight='bold', color='white' if not txt=='Emoji' else None).encode(text=f'{txt}:N')

l_dg = mk_lyr(dg_df, '', 0, c='rgba(255,0,0,0.12)', st_c='#8B0000', sw=2)
l_hv, l_th, l_tm, l_tg = mk_lyr(hive_df, 'Emoji', 35), mk_lyr(throne_df, 'Emoji', 38), mk_lyr(temple_df, 'Emoji', 32), mk_lyr(target_data, 'Emoji', 35)
l_me, l_mt = mk_lyr(sp_df, 'Emoji', 28), mk_lyr(sp_df, 'Lbl', 14, dx=22, dy=-10)

chart = alt.layer(l_dg, l_th, l_tm, l_hv, l_tg, l_me, l_mt).properties(width=700, height=500, background='rgba(0,0,0,0)').configure_view(strokeOpacity=0)
st.altair_chart(chart, use_container_width=True)

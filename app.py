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
    
    /* Force specific form columns to stay locked horizontally closely together on mobile */
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

st.write("Finds the closest available coordinate to the hive outside a 150km radius of your spawns and 200km away from rivals.")
st.markdown("### 📋 Instructions:\n1. Enter your coordinates into the side-by-side boxes below.\n2. Tap or click anywhere outside a field to trigger calculations instantly!\n3. The app will automatically calculate your safe location to teleport to as you type!")

HIVE_X, HIVE_Y = 356, 721
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

# Baseline dynamic state tracking initializations
for i in range(1, 6):
    if f"x_{i}" not in st.session_state: st.session_state[f"x_{i}"] = None
    if f"y_{i}" not in st.session_state: st.session_state[f"y_{i}"] = None

if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6):
        st.session_state[f"x_{i}"] = None
        st.session_state[f"y_{i}"] = None
    st.rerun()

st.subheader("📍 Active Spawns")

spawns = []

# --- Native Fixed Horizontal Grid Generation Loop ---
for i in range(1, 6):
    # Only reveal subsequent spawn fields once previous entries contain values
    if i == 1 or (st.session_state[f"x_{i-1}"] is not None and st.session_state[f"y_{i-1}"] is not None):
        col_lbl, col_x, col_y = st.columns([1.2, 1.5, 1.5], gap="small")
        
        with col_lbl:
            st.markdown(f"<div style='padding-top: 6px; font-weight: bold; font-size:15px;'>Spawn {i}</div>", unsafe_allow_html=True)
            
        with col_x:
            # Collapsing label parameters hides stacking triggers and shortens boxes natively
            x_val = st.number_input(f"X{i}", min_value=0, max_value=1200, step=1, value=st.session_state[f"x_{i}"], key=f"x_{i}", label_visibility="collapsed", placeholder="X...")
            
        with col_y:
            y_val = st.number_input(f"Y{i}", min_value=0, max_value=1200, step=1, value=st.session_state[f"y_{i}"], key=f"y_{i}", label_visibility="collapsed", placeholder="Y...")
            
        if x_val is not None and y_val is not None:
            spawns.append((int(x_val), int(y_val)))

st.write("---")
target_x, target_y, true_dist = None, None, None
target_list = []
rivals = [{"X": 319, "Y": 481, "Tag": "TDK"}, {"X": 611, "Y": 551, "Tag": "CoG"}, {"X": 673, "Y": 771, "Tag": "NFM"}]

if len(spawns) > 0:
    X, Y = np.meshgrid(np.arange(0, 1200), np.arange(0, 1200))
    X, Y = X.flatten(), Y.flatten()
    v_mask = np.ones_like(X, dtype=bool)
    
    for sx, sy in spawns: v_mask &= (np.sqrt((X - sx)**2 + (Y - sy)**2) > 150)
    for r in rivals: v_mask &= (np.sqrt((X - r["X"])**2 + (r["Y"] - Y)**2) > 200)
    
    valid_x, valid_y = X[v_mask], Y[v_mask]
    if len(valid_x) > 0:
        d_hive = np.sqrt((valid_x - HIVE_X)**2 + (valid_y - HIVE_Y)**2)
        idx = np.argmin(d_hive)
        target_x, target_y, true_dist = int(valid_x[idx]), int(valid_y[idx]), int(round(d_hive[idx]))
        
        st.success(f"🎯 **Teleport here and continue spawning:** X: {target_x}, Y: {target_y} ({true_dist} km from Hive)")
        st.write("**Spawn Distances from Hive:**")
        st.write(" | ".join([f"**Spawn {idx}:** {int(round(np.sqrt((sx - HIVE_X)**2 + (sy - HIVE_Y)**2)))} km" for idx, (sx, sy) in enumerate(spawns, 1)]))
        target_list.append({"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯", "Label": f"Target ({target_x},{target_y})"})
    else:
        st.error("❌ No valid spawning coordinates found.")

hive_df = pd.DataFrame([{"X_iso": HIVE_X - HIVE_Y, "Y_iso": HIVE_X + HIVE_Y, "Emoji": "🏰", "Label": f"Hive ({HIVE_X},{HIVE_Y})"}])
throne_df = pd.DataFrame([{"X_iso": 0, "Y_iso": 1200, "Emoji": "👑", "Label": "Throne (600,600)"}])
temple_df = pd.DataFrame([
    {"X_iso": -600, "Y_iso": 1200, "Emoji": "🏛️", "Label": "Hunter Temple (300,900)"}, 
    {"X_iso": 0, "Y_iso": 600, "Emoji": "🏛️", "Label": "Harvest Temple (300,300)"}, 
    {"X_iso": 600, "Y_iso": 1200, "Emoji": "🏛️", "Label": "Forging Temple (900,300)"}
])

m_list, r_list = [], []
for idx, (sx, sy) in enumerate(spawns, 1): 
    m_list.append({"X_iso": sx - sy, "Y_iso": sx + sy, "Emoji": "👹", "Lbl": str(idx), "Label": f"Spawn {idx} ({sx},{sy})"})
for r in rivals:
    m_list.append({"X_iso": r["X"] - r["Y"], "Y_iso": r["X"] + r["Y"], "Emoji": "💀", "Lbl": r["Tag"], "Label": f"{r['Tag']} ({r['X']},{r['Y']})"})
    r_list.append({"X_iso": r["X"] - r["Y"], "Y_iso": r["X"] + r["Y"], "Label": f"{r['Tag']} Danger (200km)"})

sp_df = pd.DataFrame(m_list) if m_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "Lbl", "Label"])
danger_df = pd.DataFrame(r_list) if r_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Label"])
target_data = pd.DataFrame(target_list) if target_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "Label"])

x_sc, y_scale = alt.Scale(domain=[-780, 620]), alt.Scale(domain=[-420, 1780], reverse=True)

# 🗺️ Structural map layer mappings
l_dg = alt.Chart(danger_df).mark_point(color='rgba(255,0,0,0.12)', stroke='#8B0000', strokeWidth=2, filled=True, size=16500).encode(x=alt.X('X_iso:Q', scale=x_sc, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), tooltip='Label:N')
l_hv = alt.Chart(hive_df).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_sc, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip='Label:N')
l_th = alt.Chart(throne_df).mark_text(size=38).encode(x=alt.X('X_iso:Q', scale=x_sc, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip='Label:N')
l_tm = alt.Chart(temple_df).mark_text(size=32).encode(x=alt.X('X_iso:Q', scale=x_sc, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip='Label:N')
l_tg = alt.Chart(target_data).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_sc, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip='Label:N')
l_me = alt.Chart(sp_df).mark_text(size=28).encode(x=alt.X('X_iso:Q', scale=x_sc, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip='Label:N')
l_mt = alt.Chart(sp_df).mark_text(size=14, fontWeight='bold', color='white', dx=22, dy=-10).encode(x=alt.X('X_iso:Q', scale=x_sc, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Lbl:N', tooltip='Label:N')

chart = alt.layer(l_dg, l_th, l_tm, l_hv, l_tg, l_me, l_mt).properties(width=700, height=500, background='rgba(0,0,0,0)').configure_view(strokeOpacity=0)
st.altair_chart(chart, use_container_width=True)

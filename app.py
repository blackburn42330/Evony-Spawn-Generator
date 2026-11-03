import io, base64
import numpy as np, pandas as pd, altair as alt, streamlit as st
from gtts import gTTS

st.set_page_config(page_title="NCI Spawn Calculator", layout="centered")
st.title("🥷 NCI Spawn Calculator")
st.markdown("""
<div style='text-align:left;font-family:"Arial Black",Gadget,sans-serif;font-size:22px;font-weight:bold;color:#FFD700;text-shadow:0 0 10px #FFD700, 0 0 20px #FF8C00;padding-bottom:12px'>NCI Spawn Calculator</div>
<style>div.stButton>button:first-child{font-size:20px!important;font-weight:bold!important;padding:10px 24px!important;border-radius:8px!important;border:2px solid #FFD700!important;color:#FFD700!important;background-color:rgba(255,215,0,.05)!important;width:100%!important;margin:10px 0 15px 0!important}div.stButton>button:first-child:hover{background-color:rgba(255,215,0,.15)!important;color:#FFF!important;border-color:#FFF!important}</style>
""", unsafe_allow_html=True)
st.write("Finds the closest available coordinate to the hive outside a 150km radius of your spawns and 250km away from rivals.")
st.markdown("### 📋 Instructions:\n1. Enter the coordinates of your **first monster spawn** below.\n2. Type the coordinates of your **next spawn** into the fields side-by-side.\n3. The app will auto-suggest where to teleport next.")

HIVE_X, HIVE_Y = 297, 791
st.info(f"🏰 **Main Alliance Hive:** ({HIVE_X}, {HIVE_Y})")

for i in range(1, 6):
    st.session_state.setdefault(f"x_{i}", "")
    st.session_state.setdefault(f"y_{i}", "")

if st.button("🗑️ Clear All Fields"):
    for i in range(1, 6):
        st.session_state[f"x_{i}"] = st.session_state[f"y_{i}"] = ""
        st.session_state.pop(f"field_x_{i}", None); st.session_state.pop(f"field_y_{i}", None)
    st.rerun()

st.subheader("📍 Active Spawns")
spawns, fields = [], []
def get_coord(v):
    try:
        n = int(str(v).strip())
        return n if 0 <= n <= 1200 else None
    except: return None

for i in range(1, 6):
    if i == 1 or (st.session_state.get(f"x_{i-1}") and st.session_state.get(f"y_{i-1}")):
        c1, c2, _ = st.columns([1.5, 1.5, 4])
        with c1: st.markdown(f"<div style='padding-top:6px;font-weight:bold;font-size:15px;white-space:nowrap'>Spawn {i}</div>", unsafe_allow_html=True)
        with c2:
            x = st.text_input(f"S{i}X", value=st.session_state[f"x_{i}"], key=f"field_x_{i}", placeholder="X...", label_visibility="collapsed")
            st.session_state[f"x_{i}"] = x
        with c2:
            y = st.text_input(f"S{i}Y", value=st.session_state[f"y_{i}"], key=f"field_y_{i}", placeholder="Y...", label_visibility="collapsed")
            st.session_state[f"y_{i}"] = y
        xv, yv = get_coord(x), get_coord(y)
        if xv is not None and yv is not None: spawns.append((xv, yv))

st.write("---")
target_x = target_y = true_dist = None
target_data = pd.DataFrame([{"X_iso":0,"Y_iso":0,"Emoji":"🎯","Label":"Target"}])
rivals = [{"X":319,"Y":481,"Tag":"TDK"},{"X":611,"Y":551,"Tag":"CoG"},{"X":673,"Y":771,"Tag":"NFM"}]

if spawns:
    X, Y = np.meshgrid(np.arange(0, 1200), np.arange(0, 1200))
    X, Y = X.ravel(), Y.ravel()
    mask = np.ones_like(X, dtype=bool)
    for sx, sy in spawns: mask &= np.hypot(X-sx, Y-sy) > 150
    for r in rivals: mask &= np.hypot(X-r["X"], Y-r["Y"]) > 250
    vx, vy = X[mask], Y[mask]
    if len(vx):
        d = np.hypot(vx-HIVE_X, vy-HIVE_Y)
        idx = np.argmin(d)
        target_x, target_y = int(vx[idx]), int(vy[idx]); true_dist = int(round(d[idx]))
        st.success(f"🎯 **Teleport here and continue spawning:** X: {target_x}, Y: {target_y} ({true_dist} km from Hive)")
        def fmt_tts(n):
            s = str(n)
            if len(s) == 3:
                return f"{s[0]} zero {s[2]}" if s[1] == "0" else f"{s[0]} {s[1:]}"
            return " ".join(list(s))
        phrase = f"coords, {fmt_tts(target_x)}, {fmt_tts(target_y)}. ... {fmt_tts(target_x)}, {fmt_tts(target_y)}."
        tts = gTTS(text=phrase, lang="en", tld="com", slow=False)
        buf = io.BytesIO(); tts.write_to_fp(buf); buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        st.write("🔊 **Voice Narration Track:**")
        aid = f"audio_{target_x}_{target_y}"
        st.markdown(f'<audio id="{aid}" src="data:audio/mp3;base64,{b64}" controls autoplay style="width:100%;"></audio>', unsafe_allow_html=True)
        st.components.v1.html(f'<script>setTimeout(()=>{{const a=window.parent.document.getElementById("{aid}");if(a)a.playbackRate=1.05}},100);</script>', height=0, width=0)
        st.write("**Spawn Distances from Hive:**")
        st.write(" | ".join(f"**Spawn {i}:** {int(round(np.hypot(sx-HIVE_X, sy-HIVE_Y)))} km" for i,(sx,sy) in enumerate(spawns,1)))
        target_data = pd.DataFrame([{"X_iso": target_x-target_y, "Y_iso": target_x+target_y, "Emoji":"🎯","Label":f"Target ({target_x},{target_y})"}])
    else:
        st.error("❌ No valid spawning coordinates found with the current constraints.")

CENTER_X, CENTER_Y = 520, 600
min_x, max_x = CENTER_X-350, CENTER_X+350
min_y, max_y = CENTER_Y-350, CENTER_Y+350
min_x_iso, max_x_iso = min_x-max_y, max_x-min_y
min_y_iso, max_y_iso = min_x+min_y, max_x+max_y

hive_data = pd.DataFrame([{"X_iso": HIVE_X-HIVE_Y, "Y_iso": HIVE_X+HIVE_Y, "Emoji":"🏰", "Label": f"Hive ({HIVE_X},{HIVE_Y})"}])
throne_data = pd.DataFrame([{"X_iso": 600-600, "Y_iso": 600+600, "Emoji":"👑", "Label":"Throne (600,600)"}])
temple_data = pd.DataFrame([
    {"X_iso":300-900,"Y_iso":300+900,"Emoji":"🏛️","Label":"Hunter Temple (300,900)"},
    {"X_iso":300-300,"Y_iso":300+300,"Emoji":"🏛️","Label":"Harvest Temple (300,300)"},
    {"X_iso":900-300,"Y_iso":900+300,"Emoji":"🏛️","Label":"Forging Temple (900,300)"},
])

monster_list = [{"X_iso": sx-sy, "Y_iso": sx+sy, "Emoji":"👹", "TextLabel": str(i), "Label": f"Spawn {i} ({sx},{sy})"} for i,(sx,sy) in enumerate(spawns,1)]
rival_list = []
for r in rivals:
    if min_x <= r["X"] <= max_x and min_y <= r["Y"] <= max_y:
        monster_list.append({"X_iso":r["X"]-r["Y"], "Y_iso":r["X"]+r["Y"], "Emoji":"💀", "TextLabel":r["Tag"], "Label": f"{r['Tag']} ({r['X']},{r['Y']})"})
        rival_list.append({"X_iso":r["X"]-r["Y"], "Y_iso":r["X"]+r["Y"], "Label":f"{r['Tag']} Danger (250km)"})
spawn_data = pd.DataFrame(monster_list) if monster_list else pd.DataFrame(columns=["X_iso","Y_iso","Emoji","TextLabel","Label"])
danger_data = pd.DataFrame(rival_list) if rival_list else pd.DataFrame(columns=["X_iso","Y_iso","Label"])

x_scale = alt.Scale(domain=[min_x_iso, max_x_iso])
y_scale = alt.Scale(domain=[min_y_iso, max_y_iso], reverse=True)

danger_zone_layer = alt.Chart(danger_data).mark_point(color="rgba(255,0,0,0.12)", stroke="#8B0000", strokeWidth=2, filled=True, size=16500).encode(x=alt.X("X_iso:Q", scale=x_scale, axis=None), y=alt.Y("Y_iso:Q", scale=y_scale, axis=None))
hive_layer = alt.Chart(hive_data).mark_text(size=35).encode(x=alt.X("X_iso:Q", scale=x_scale, axis=None), y=alt.Y("Y_iso:Q", scale=y_scale, axis=None), text="Emoji:N", tooltip=["Label:N"])
throne_layer = alt.Chart(throne_data).mark_text(size=38).encode(x=alt.X("X_iso:Q", scale=x_scale, axis=None), y=alt.Y("Y_iso:Q", scale=y_scale, axis=None), text="Emoji:N", tooltip=["Label:N"])
temple_layer = alt.Chart(temple_data).mark_text(size=32).encode(x=alt.X("X_iso:Q", scale=x_scale, axis=None), y=alt.Y("Y_iso:Q", scale=y_scale, axis=None), text="Emoji:N", tooltip=["Label:N"])
target_layer = alt.Chart(target_data).mark_text(size=35).encode(x=alt.X("X_iso:Q", scale=x_scale, axis=None), y=alt.Y("Y_iso:Q", scale=y_scale, axis=None), text="Emoji:N", tooltip=["Label:N"])
monster_emoji_layer = alt.Chart(spawn_data).mark_text(size=28).encode(x=alt.X("X_iso:Q", scale=x_scale, axis=None), y=alt.Y("Y_iso:Q", scale=y_scale, axis=None), text="Emoji:N", tooltip=["Label:N"])
monster_text_layer = alt.Chart(spawn_data).mark_text(size=14, fontWeight="bold", color="white", dx=22, dy=-10).encode(x=alt.X("X_iso:Q", scale=x_scale, axis=None), y=alt.Y("Y_iso:Q", scale=y_scale, axis=None), text="TextLabel:N", tooltip=["Label:N"])

chart = alt.layer(danger_zone_layer, hive_layer, throne_layer, temple_layer, target_layer, monster_emoji_layer, monster_text_layer).properties(width=700, height=500).configure_view(strokeOpacity=0)
st.altair_chart(chart, use_container_width=True)

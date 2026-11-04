import streamlit as st
import pandas as pd
import altair as alt

def render_minimap(hive_x, hive_y, spawns, rivals, target_data):
    """
    Renders the Altair isometric map layer by layer based on active coordinates.
    """
    CENTER_X, CENTER_Y = 520, 600
    min_x, max_x = CENTER_X - 350, CENTER_X + 350
    min_y, max_y = CENTER_Y - 350, CENTER_Y + 350
    min_x_iso, max_x_iso = min_x - max_y, max_x - min_y
    min_y_iso, max_y_iso = min_x + min_y, max_x + max_y

    hive_data = pd.DataFrame([{"X_iso": hive_x - hive_y, "Y_iso": hive_x + hive_y, "Emoji": "🏰", "Label": f"Hive ({hive_x},{hive_y})"}])
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
            rival_list.append({"X_iso": r["X"] - r["Y"], "Y_iso": r["X"] + r["Y"], "Label": f"{r['Tag']} Danger (250km)"})
            
    spawn_data = pd.DataFrame(monster_list) if monster_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "TextLabel", "Label"])
    danger_data = pd.DataFrame(rival_list) if rival_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Label"])

    x_scale, y_scale = alt.Scale(domain=[min_x_iso, max_x_iso]), alt.Scale(domain=[min_y_iso, max_y_iso], reverse=True)

    danger_zone_layer = alt.Chart(danger_data).mark_point(color='rgba(255, 0, 0, 0.12)', stroke='#8B0000', strokeWidth=2, filled=True, size=16500).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), tooltip=['Label:N'])
    hive_layer = alt.Chart(hive_data).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    throne_layer = alt.Chart(throne_data).mark_text(size=38).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    temple_layer = alt.Chart(temple_data).mark_text(size=32).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    target_layer = alt.Chart(target_data).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    monster_emoji_layer = alt.Chart(spawn_data).mark_text(size=28).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    monster_text_layer = alt.Chart(spawn_data).mark_text(size=14, fontWeight='bold', color='white', dx=22, dy=-10).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='TextLabel:N')

    # --- Combine Layers and Render Chart ---
    chart = alt.layer(danger_zone_layer, hive_layer, throne_layer, temple_layer, target_layer, monster_emoji_layer, monster_text_layer).properties(width=700, height=500).configure_view(strokeOpacity=0)
    st.altair_chart(chart, use_container_width=True)

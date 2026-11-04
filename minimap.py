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
    
    # FIXED: Re-mapped the isometric window calculation boundaries to match the layout transformation
    min_x_iso, max_x_iso = min_x + min_y, max_x + max_y
    min_y_iso, max_y_iso = min_y - max_x, max_y - min_x

    # FIXED: Re-mapped coordinate formulas (X + Y, Y - X) across all datasets to correctly align with Evony's grid layout
    hive_data = pd.DataFrame([{"X_iso": hive_x + hive_y, "Y_iso": hive_y - hive_x, "Emoji": "🏰", "Label": f"Hive ({hive_x},{hive_y})"}])
    throne_data = pd.DataFrame([{"X_iso": 600 + 600, "Y_iso": 600 - 600, "Emoji": "👑", "Label": "Throne (600,600)"}])
    
    temple_data = pd.DataFrame([
        {"X_iso": 300 + 900, "Y_iso": 900 - 300, "Emoji": "🏛️", "Label": "Hunter Temple (300,900)"},
        {"X_iso": 300 + 300, "Y_iso": 300 - 300, "Emoji": "🏛️", "Label": "Harvest Temple (300,300)"},
        {"X_iso": 900 + 300, "Y_iso": 300 - 900, "Emoji": "🏛️", "Label": "Forging Temple (900,300)"}
    ])

    monster_list = [{"X_iso": sx + sy, "Y_iso": sy - sx, "Emoji": "👹", "TextLabel": str(idx), "Label": f"Spawn {idx} ({sx},{sy})"} for idx, (sx, sy) in enumerate(spawns, 1)]
    rival_list = []
    
    for r in rivals:
        if min_x <= r["X"] <= max_x and min_y <= r["Y"] <= max_y:
            monster_list.append({"X_iso": r["X"] + r["Y"], "Y_iso": r["Y"] - r["X"], "Emoji": "💀", "TextLabel": r["Tag"], "Label": f"{r['Tag']} ({r['X']},{r['Y']})"})
            rival_list.append({"X_iso": r["X"] + r["Y"], "Y_iso": r["Y"] - r["X"], "Label": f"{r['Tag']} Danger (250km)"})
            
    spawn_data = pd.DataFrame(monster_list) if monster_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Emoji", "TextLabel", "Label"])
    danger_data = pd.DataFrame(rival_list) if rival_list else pd.DataFrame(columns=["X_iso", "Y_iso", "Label"])

    # Map scales set cleanly using the revised coordinate orientations
    x_scale, y_scale = alt.Scale(domain=[min_x_iso, max_x_iso]), alt.Scale(domain=[min_y_iso, max_y_iso])

    danger_zone_layer = alt.Chart(danger_data).mark_point(color='rgba(255, 0, 0, 0.12)', stroke='#8B0000', strokeWidth=2, filled=True, size=16500).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), tooltip=['Label:N'])
    hive_layer = alt.Chart(hive_data).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    throne_layer = alt.Chart(throne_data).mark_text(size=38).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    temple_layer = alt.Chart(temple_data).mark_text(size=32).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    
    # FIXED: Re-mapped the targeted coordinate output layer to use the updated transformation matrix
    if not target_data.empty:
        target_data_iso = target_data.copy()
        # Extracts original variables if passed through the target tracking engine dataframes
        if 'X' in target_data.columns and 'Y' in target_data.columns:
            target_data_iso['X_iso'] = target_data_iso['X'] + target_data_iso['Y']
            target_data_iso['Y_iso'] = target_data_iso['Y'] - target_data_iso['X']
        else:
            # Fallback if map coordinates were precalculated inside app.py
            target_data_iso['X_iso'] = target_data_iso['X_iso']
            target_data_iso['Y_iso'] = target_data_iso['Y_iso']
    else:
        target_data_iso = target_data

    target_layer = alt.Chart(target_data_iso).mark_text(size=35).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    monster_emoji_layer = alt.Chart(spawn_data).mark_text(size=28).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='Emoji:N', tooltip=['Label:N'])
    monster_text_layer = alt.Chart(spawn_data).mark_text(size=14, fontWeight='bold', color='white', dx=22, dy=-10).encode(x=alt.X('X_iso:Q', scale=x_scale, axis=None), y=alt.Y('Y_iso:Q', scale=y_scale, axis=None), text='TextLabel:N')

    # --- Combine Layers and Render Chart ---
    chart = alt.layer(danger_zone_layer, hive_layer, throne_layer, temple_layer, target_layer, monster_emoji_layer, monster_text_layer).properties(width=700, height=500).configure_view(strokeOpacity=0)
    st.altair_chart(chart, use_container_width=True)

# --- Replace your existing "if len(spawns) > 0:" block with this block ---

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
        
        # 🔊 Native Browser Voice Narration Trigger Button
        if st.button("🔊 Hear Next Target Coordinates"):
            tts_html = f"""
            <script>
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel(); // Clear any queued lines
                    const text = "teleport to coordinates x {target_x} y {target_y}";
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.rate = 1.0;
                    utterance.pitch = 1.0;
                    window.speechSynthesis.speak(utterance);
                }} else {{
                    alert("Speech Synthesis is not supported or blocked by your browser settings.");
                }}
            </script>
            """
            st.components.v1.html(tts_html, height=0, width=0)
        
        st.write("**Spawn Distances from Hive:**")
        dist_strings = []
        for idx, (sx, sy) in enumerate(spawns, 1):
            s_dist = int(round(np.sqrt((sx - HIVE_X)**2 + (sy - HIVE_Y)**2)))
            dist_strings.append(f"**Spawn {idx}:** {s_dist} km")
        st.write(" | ".join(dist_strings))
                
        target_data = pd.DataFrame([{"X_iso": target_x - target_y, "Y_iso": target_x + target_y, "Emoji": "🎯", "Label": f"Target ({target_x},{target_y})"}])
    else: st.error("❌ No valid spawning coordinates found with the current constraints.")

# --- Continue with your map settings (CENTER_X, CENTER_Y = 520, 600...) below ---

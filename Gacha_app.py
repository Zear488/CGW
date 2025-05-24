import streamlit as st
import pandas as pd
import io
import random
import os
import re
from streamlit.components.v1 import html
import numpy as np
import math

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Chaos Gacha Web", layout="wide")

# ------------------ LOAD EXISTING HISTORY ------------------
st.sidebar.header("📂 Load Previous History")
uploaded_file = st.sidebar.file_uploader("Upload history CSV (UTF-8)", type=["csv"])

if "log" not in st.session_state:
    st.session_state["log"] = []
    
if uploaded_file:
    try:
        df_loaded = pd.read_csv(uploaded_file, encoding="utf-8-sig")
        required_cols = {"Type", "Element", "Rarity", "Tier", "Luck", "Description", "Color"}
        if required_cols.issubset(set(df_loaded.columns)):
            st.session_state["log"] = df_loaded.to_dict(orient="records")
            st.sidebar.success("✅ History loaded successfully.")
        else:
            st.sidebar.error("❌ Invalid CSV format. Columns missing.")
    except Exception as e:
        st.sidebar.error(f"❌ Error loading file: {e}")

if st.sidebar.button("🗑️ Clear History"):
    st.session_state["log"] = []

# ------------------ READ FUNCTION ------------------
def read_file_with_weight(filename, avg, min_val, max_val):
    elements, weights, rarities, descriptions = [], [], [], []

    min_rarity = float(min_val)
    avg_rarity = float(avg)
    max_rarity = float(max_val)
    sigma = 1.2  

    if filename == "Random":
        filename = random.choice(["Ability", "Item", "Familiar", "Trait", "Skill"])

    chosentype = filename.capitalize()
    path = os.path.join("gachafiles", f"{filename}.txt")

    with open(path, "r", encoding="utf-8") as file:
        temp_description = []

        for line in file:
            match = re.match(r"^(\d+)\.(\S*)\s*(.*)", line)
            if match:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    element = parts[0].strip()
                    try:
                        rarity = float(parts[1])
                    except ValueError:
                        continue

                    elements.append(element)
                    rarities.append(rarity)

                    # Nuevo peso basado en distribución gaussiana centrada en avg
                    weight = math.exp(-((rarity - avg_rarity) ** 2) / (2 * sigma ** 2))
                    weights.append(weight)

                    if temp_description:
                        descriptions.append(" ".join(temp_description).strip())
                        temp_description = []
            else:
                temp_description.append(line)

        if temp_description:
            descriptions.append(" ".join(temp_description).strip())

    weightsum = sum(weights)

    return elements, weights, rarities, descriptions, weightsum, chosentype
# ------------------ GACHA FUNCTIONS ------------------

def randomizer(min_val, max_val, avg, std_dev=0.8, bonus_chance=0.0048, bonus_max=2.0, max_penalty=0.7, max_attempts=10):
    min_val = float(min_val)
    max_val = float(max_val)
    avg = float(avg)

    for attempt in range(1, max_attempts + 1):
        # Penalización progresiva al promedio para permitir encontrar algo cercano
        penalty_factor = 1 - min(max_penalty, (attempt - 1) * 0.07)  # Límite: -70%
        capped_avg = avg * penalty_factor
        rarity = random.gauss(capped_avg, std_dev)

        # Bonus de rareza ocasional
        if random.random() < bonus_chance:
            rarity += random.uniform(0.1, bonus_max)

        # Clampeamos dentro de los límites
        rarity = max(min_val, min(rarity, max_val))

        if min_val <= rarity <= max_val:
            return round(rarity, 2)
    # Si falla todo, retorna el peor resultado
    return round(min_val, 2)
    
def run_gacha(mode, min_val, avg, max_val, max_tries=10):
    elements, base_weights, rarities, descriptions, _, chosentype = read_file_with_weight(mode, avg, min_val, max_val)

    for attempt in range(1, max_tries + 1):
        raritypull = randomizer(min_val, max_val, avg, std_dev=0.8)

        filtered = [(e, w, r, d) for e, w, r, d in zip(elements, base_weights, rarities, descriptions)
                    if abs(r - raritypull) <= 0.25]

        if filtered:
            adjusted_weights = [w for _, w, _, _ in filtered]
            filtered_weights_sum = sum(adjusted_weights)
            if filtered_weights_sum == 0:
                return None

            selected = random.choices(filtered, weights=adjusted_weights)[0]
            element, _, rarity, desc = selected

            bonus_triggered = False
            # BONUS: 0.48% de probabilidad de +2 de rareza si no supera el máximo
            if random.random() < 0.0048 and rarity + 2 <= 10:
                rarity += 2
                element = f"★ {element}"
                bonus_triggered = True

            rarity_range = max_val - min_val
            if rarity_range == 0:
                estimated_luck = 100.0
            else:
                distance_from_min = rarity - min_val
                estimated_luck = max(0.1, min(100.0, 100.0 * (1 - (distance_from_min / rarity_range))))

            return {
                "element": element,
                "rarity": round(rarity, 2),
                "description": desc.replace("#", "").strip(),
                "luck": round(estimated_luck, 2),
                "type": chosentype,
                "bonus": bonus_triggered
            }

    return None

def get_tier_and_color(rarity):
    tiers = [
        (1.0, 'Trash', '#a39589'),
        (2.0, 'Common', '#9c7e5a'),
        (3.0, 'Uncommon', '#aed1d1'),
        (4.0, 'Rare', '#11d939'),
        (5.0, 'Elite', '#1172d9'),
        (6.0, 'Epic', '#6811d9'),
        (7.0, 'Legendary', '#f7d40a'),
        (8.0, 'Mythical', '#fc61ff'),
        (9.0, 'Divine', '#ff8c00'),
        (10.0, 'Transcendent', '#ff0000'),
    ]
    for limit, name, color in tiers:
        if rarity < limit:
            return name, color
    return "Transcendent", "#ff0000"

# ------------------ STREAMLIT INTERFACE ------------------
st.title("🎲 Chaos Gacha Web")

with st.expander("ℹ️ What do 'Rarity' and 'Estimated Luck' mean?"):
    st.markdown("""
    **🧪 Rarity** is a value between `0.1` and `10.0` that represents 
    how special or powerful an element is. The higher the number, the rarer it is.

    | Tier           | Rarity Range   | Color        |
    |----------------|----------------|--------------|
    | Trash          | < 1.0          | Brown        |
    | Common         | 1.0 – 2.0      | Bronze       |
    | Uncommon       | 2.0 – 3.0      | Teal         |
    | Rare           | 3.0 – 4.0      | Green        |
    | Elite          | 4.0 – 5.0      | Blue         |
    | Epic           | 5.0 – 6.0      | Purple       |
    | Legendary      | 6.0 – 7.0      | Gold         |
    | Mythical       | 7.0 – 8.0      | Pink         |
    | Divine         | 8.0 – 9.0      | Orange       |
    | Transcendent   | > 9.0          | Red          |

    ---

    **🍀 Estimated Luck** shows how unlikely it was to pull this element:

    | Estimated Luck | Interpretation             |
    |----------------|----------------------------|
    | > 30%          | Very Common                |
    | 10% – 30%      | Uncommon                   |
    | 1% – 10%       | Rare                       |
    | < 1%           | Extremely Rare / Epic Pull |

    The lower the percentage, the luckier you were. 
    This value is calculated based on the rarity and the configured search range.
    """)

presets = {
    "Bronze": ((0.1, 1.3, 3.3), "#cd7f32"),
    "Silver": ((0.5, 2.3, 4.3), "#c0c0c0"),
    "Gold": ((1.5, 3.3, 5.3), "#ffd700"),
    "Platinum": ((2.5, 4.3, 6.3), "#e5e4e2"),
    "Diamond": ((3.5, 5.3, 7.3), "#b9f2ff"),
    "Legendary": ((4.5, 6.3, 8.3), "#f7d40a"),
    "Mythical": ((5.5, 7.3, 9.3), "#fc61ff"),
    "Divine": ((6.5, 8.3, 10.0), "#ff8c00"),
}

if "min_val" not in st.session_state:
    st.session_state["min_val"] = 0.1
    st.session_state["avg"] = 1.3
    st.session_state["max_val"] = 3.3

if "log" not in st.session_state:
    st.session_state["log"] = []

st.subheader("🎚️ Choose a Rarity Preset")
cols = st.columns(len(presets))

for i, (label, (values, color)) in enumerate(presets.items()):
    with cols[i]:
        clicked = st.button(label, use_container_width=True, key=f"preset_{label}")
        if clicked:
            st.session_state["min_val"], st.session_state["avg"], st.session_state["max_val"] = values
        st.markdown(
            f"<div style='height:6px;background-color:{color};border-radius:4px;margin-top:4px;'></div>",
            unsafe_allow_html=True
        )

active_color = "#4a4a4a"
for label, (values, color) in presets.items():
    if (st.session_state["min_val"], st.session_state["avg"], st.session_state["max_val"]) == values:
        active_color = color
        break

st.subheader("Category")
mode = st.radio("Choose a category", ["Ability", "Item", "Familiar", "Skill", "Trait", "Random"], horizontal=True)

st.subheader("Rarity Range")
min_val = st.slider("Min", 0.0, 10.0, st.session_state["min_val"], 0.1)
avg = st.slider("Average", 0.0, 10.0, st.session_state["avg"], 0.1)
max_val = st.slider("Max", 0.0, 10.0, st.session_state["max_val"], 0.1)

st.session_state["min_val"] = min_val
st.session_state["avg"] = avg
st.session_state["max_val"] = max_val

# Selector + Botón de Multi Pull
# Selector de multipull
pull_count = st.selectbox("Select number of pulls:", [1, 2, 5, 10], index=0)

def classify_luck(luck_value):
    if luck_value > 95:
        return "Below Average"
    elif luck_value > 75:
        return "Average"
    elif luck_value > 55:
        return "Above Average"
    elif luck_value > 35:
        return "Notable"
    elif luck_value > 15:
        return "Rare"
    elif luck_value > 5:
        return "Exceptional Pull"
    else:
        return "Mythic Pull"

# Función para mostrar un resultado
def display_result(result, min_val, max_val):
    tier, color = get_tier_and_color(result["rarity"])
    luck_type = classify_luck(result["luck"])

    st.markdown(f"<h3 style='color:{color}' title='{result['description']}'>🎉 {result['element']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color}'><strong>Rarity</strong>: `{result['rarity']:.2f}` ({tier})</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color}'><strong>Type</strong>: `{result['type']}`</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color}'><strong>Estimated Luck</strong>: `{result['luck']:.2f}%` – {luck_type}</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        f"<div style='background-color:#111;padding:10px;border-radius:10px;'>"
        f"<p style='color:white;font-size:16px;line-height:1.5;text-align:justify;'>{result['description']}</p>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Registrar en el historial
    st.session_state["log"].append({
        "Type": result["type"],
        "Element": result["element"],
        "Rarity": f"{result['rarity']:.2f}",
        "Tier": tier,
        "Luck": f"{result['luck']:.2f}%",
        "Description": result["description"],
        "Color": color,
        "Bonus": "★" if result.get("bonus") else ""
    })

# Botón individual 🎰 Roll
if st.button("🎰 Roll"):
    result = run_gacha(mode, min_val, avg, max_val)
    if result:
        display_result(result, min_val, max_val)

# Botón de Multi-Roll
if st.button("🎲 Multi-Roll"):
    results = [run_gacha(mode, min_val, avg, max_val) for _ in range(pull_count)]
    for result in results:
        if result:
            display_result(result, min_val, max_val)


if st.session_state.get("log"):
    st.markdown("## 📜 Roll History")
    st.markdown(f"Total Rolls: **{len(st.session_state['log'])}**")

    # Mostrar historial como HTML
    log_html = """
    <div style='
        max-height: 500px;
        overflow-y: auto;
        padding-right: 10px;
        margin-bottom: 20px;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 10px;
        background-color: #1e1e1e;
    '>
    """
    for i, entry in enumerate(reversed(st.session_state["log"]), 1):
        color = entry.get("Color", "#f0f0f0")
        log_html += f"""
        <div style='
            background-color:#222;
            padding:15px;
            margin:10px 0;
            border-radius:10px;
            box-shadow:0 0 5px rgba(255,255,255,0.1);
        '>
            <h4 style='color:{color};margin-bottom:5px;'>#{len(st.session_state["log"]) - i + 1} — {entry.get("Element", "Unknown")}</h4>
            <p style='margin:2px 0;color:{color};'><strong>Type:</strong> {entry.get("Type", "-")}</p>
            <p style='margin:2px 0;color:{color};'><strong>Rarity:</strong> {entry.get("Rarity", "-")} ({entry.get("Tier", "-")})</p>
            <p style='margin:2px 0;color:{color};'><strong>Luck:</strong> {entry.get("Luck", "-")}</p>
            <p style='margin:10px 0 0 0;'><strong>Description:</strong></p>
            <div style='
                background-color:#111;
                padding:10px;
                border-radius:8px;
                color:#ddd;
                font-size:14px;
                white-space:pre-wrap;
                word-wrap:break-word;
            '>{entry.get("Description", "No description")}</div>
        </div>
        """
    log_html += "</div>"
    html(log_html, height=550)

    # Exportar CSV con BOM para compatibilidad móvil 
    df_log = pd.DataFrame(st.session_state["log"])
    csv_buffer = io.StringIO()
    df_log.to_csv(csv_buffer, index=False, encoding="utf-8-sig")  # <- BOM encoding
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label="⬇️ Download history as CSV",
        data=csv_data,
        file_name="gacha_history.csv",
        mime="text/csv"
    )

from datetime import datetime

# Carpetas que usadas:
# - "Original_gachafiles" para los archivos originales
# - "gachafiles" para los archivos editados actuales
# - "gachafiles_versions" para versiones guardadas (historial)

# Crear carpetas si no existen
for folder in ["Original_gachafiles", "gachafiles", "gachafiles_versions"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Inicializar session_state
if "original_files" not in st.session_state:
    st.session_state["original_files"] = {}

if "edited_files" not in st.session_state:
    st.session_state["edited_files"] = {}

# Lista de gachafiles según carpeta "gachafiles"
gachafile_options = [f.replace(".txt", "") for f in os.listdir("gachafiles") if f.endswith(".txt")]
selected_gachafile = st.selectbox("Select a Gacha File to view/edit", gachafile_options)

# Cargar original si no existe en session_state (desde Original_gachafiles)
if selected_gachafile not in st.session_state["original_files"]:
    path_original = os.path.join("Original_gachafiles", f"{selected_gachafile}.txt")
    with open(path_original, "r", encoding="utf-8") as f:
        content = f.read()
    st.session_state["original_files"][selected_gachafile] = content

# Cargar editado si no existe (desde gachafiles)
if selected_gachafile not in st.session_state["edited_files"]:
    path_edit = os.path.join("gachafiles", f"{selected_gachafile}.txt")
    with open(path_edit, "r", encoding="utf-8") as f:
        content_edit = f.read()
    st.session_state["edited_files"][selected_gachafile] = content_edit

edit_key = f"edit_area_{selected_gachafile}"

# Inicializar textarea controlado
if edit_key not in st.session_state:
    st.session_state[edit_key] = st.session_state["edited_files"][selected_gachafile]

# Botón Restore Original
if st.button("♻️ Restore Original"):
    st.session_state[edit_key] = st.session_state["original_files"][selected_gachafile]
    st.session_state["edited_files"][selected_gachafile] = st.session_state["original_files"][selected_gachafile]
    st.success(f"Restored original `{selected_gachafile}`.")

# Mostrar textarea editable
content = st.text_area(
    label=f"Edit {selected_gachafile}",
    value=st.session_state[edit_key],
    key=edit_key,
    height=300,
)

# Actualizar el contenido editado en session_state
st.session_state["edited_files"][selected_gachafile] = st.session_state[edit_key]

# Botón Guardar cambios manual
if st.button("💾 Save Changes"):
    path = os.path.join("gachafiles", f"{selected_gachafile}.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(st.session_state["edited_files"][selected_gachafile])
        st.success(f"✅ Changes saved to `{selected_gachafile}.txt`.")

        # Guardar versión automática con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_path = os.path.join("gachafiles_versions", f"{selected_gachafile}_{timestamp}.txt")
        with open(version_path, "w", encoding="utf-8") as f:
            f.write(st.session_state["edited_files"][selected_gachafile])

    except Exception as e:
        st.error(f"❌ Error saving file: {e}")

st.markdown("---")
st.subheader("Saved Versions")

import base64

st.markdown("## 📜 Saved Versions")

version_folder = "gachafiles_versions"
file_prefix = selected_gachafile + "_"

# Buscar versiones guardadas del archivo actual
version_files = sorted(
    [f for f in os.listdir(version_folder) if f.startswith(file_prefix)],
    reverse=True
    
)

if "editable_gachafiles" not in st.session_state:
    st.session_state.editable_gachafiles = {}
    
if version_files:
    for version_file in version_files:
        version_path = os.path.join(version_folder, version_file)
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
        
        with col1:
            st.markdown(f"📂 `{version_file}`")

        with col2:
            if st.button("🔄 Restore", key=f"restore_{version_file}"):
                with open(version_path, "r", encoding="utf-8") as f:
                    st.session_state.editable_gachafiles[selected_gachafile] = f.read()
                st.success(f"✅ Restored version: {version_file}")

        with col3:
            if st.button("🗑️ Delete", key=f"delete_{version_file}"):
                try:
                    os.remove(version_path)
                    st.success(f"🗑️ Deleted version: {version_file}")
                except Exception as e:
                    st.error(f"❌ Error deleting version: {e}")

        with col4:
            with open(version_path, "rb") as f:
                file_content = f.read()
                b64 = base64.b64encode(file_content).decode()
                href = f'<a href="data:file/txt;base64,{b64}" download="{version_file}">⬇️ Download</a>'
                st.markdown(href, unsafe_allow_html=True)
else:
    st.info("No saved versions available for this file.")

    st.markdown("## 🗑️ Manage Saved Versions")

version_folder = "gachafiles_versions"

if not os.path.exists(version_folder):
    os.makedirs(version_folder)

# -------------------------------
# Borrar versiones del archivo actual
# -------------------------------
file_prefix = selected_gachafile + "_"
version_files = [
    f for f in os.listdir(version_folder)
    if f.startswith(file_prefix) and f.endswith(".txt")
]

st.markdown("### 🔍 Delete Versions for Current File")

if version_files:
    selected_versions = st.multiselect(
        "Select versions to delete:",
        version_files,
        help="These are saved historical versions of the current file."
       
    )
    if st.button("❌ Delete Selected Versions"):
        deleted = []
        for vf in selected_versions:
            try:
                os.remove(os.path.join(version_folder, vf))
                deleted.append(vf)
            except Exception as e:
                st.error(f"Failed to delete {vf}: {e}")
        if deleted:
            st.success(f"Deleted: {', '.join(deleted)}")
        else:
            st.warning("No versions were deleted.")
else:
    st.info("No saved versions available for this file.")

# -------------------------------
# Borrar TODAS las versiones guardadas
# -------------------------------
st.markdown("---")
st.markdown("### 🧨 Delete All Versions (All Files)")

all_versions = [
    f for f in os.listdir(version_folder)
    if f.endswith(".txt")
]

if all_versions:
    if st.button("💣 Delete ALL Saved Versions (Irreversible)"):
        try:
            for f in all_versions:
                os.remove(os.path.join(version_folder, f))
            st.success("✅ All saved versions deleted.")
        except Exception as e:
            st.error(f"❌ Error deleting versions: {e}")
            
else:
    st.info("There are no saved versions in the system.")
    st.markdown("---")
import re

st.subheader("📤 Upload a Saved Version to Load")

uploaded_version = st.file_uploader("Upload a saved version (.txt)", type=["txt"], key="upload_saved_version")
manual_text = st.text_area("📋 Or paste the content manually", height=200, key="manual_upload_text")

# Variables para almacenar contenido y categoría detectada
version_content = None
base_name = None

if uploaded_version:
    filename = uploaded_version.name
    name_match = re.match(r"([A-Za-z]+)", filename)

    if name_match:
        base_name = name_match.group(1)

        if base_name in gachafile_options:
            version_content = uploaded_version.read().decode("utf-8")
            st.text_area(f"📄 Preview of '{filename}'", version_content, height=200, key="uploaded_version_preview", disabled=True)
        else:
            st.error(f"❌ Unknown file: '{base_name}' is not a valid gacha category.")
    else:
        st.error("❌ Invalid filename format. Use a file starting with the category name, like 'Item_*.txt'")

elif manual_text.strip():
    version_content = manual_text.strip()
    # Para contenido manual, el usuario debe elegir la categoría explícitamente.
    base_name = st.selectbox("📂 Assign content to category", options=gachafile_options, key="manual_category_select")
    st.text_area("📄 Preview of pasted content", version_content, height=200, key="manual_preview", disabled=True)

if version_content and base_name:
    if st.button(f"📥 Load to 'Saved Versions' as new version of '{base_name}'", key="load_uploaded_to_versions"):
        st.session_state.setdefault("gachafiles_versions", {}).setdefault(base_name, []).append(version_content)
        st.session_state.setdefault("edited_files", {})[base_name] = version_content
        if base_name not in st.session_state.get("original_files", {}):
            st.session_state.setdefault("original_files", {})[base_name] = version_content
        st.success(f"✅ Version added to saved history under '{base_name}' and updated as editable.")

import streamlit as st
import pandas as pd
import io
import random
import os
import re
from streamlit.components.v1 import html

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Chaos Gacha Web", layout="centered")

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
    weightsum = 0

    if filename == "Random":
        filename = random.choice(["Ability", "Item", "Familiar", "Trait", "Skill"])
    chosentype = filename.capitalize()
    path = os.path.join("gachafiles", f"{filename}.txt")

    with open(path, "r", encoding="utf-8") as file:
        tempdescription = []
        for line in file:
            match = re.match(r"^(\d+)\.(\S*)\s*(.*)", line)
            if match:
                parts = line.strip().split(",")
                element, rarity = parts[0], float(parts[1])
                elements.append(element)
                weight = 1 / (pow(4, abs(avg - rarity)))
                weights.append(weight)
                rarities.append(rarity)
                if min_rarity < rarity <= max_rarity:
                    weightsum += weight
                if tempdescription:
                    descriptions.append(" ".join(tempdescription).strip())
                    tempdescription = []
            else:
                tempdescription.append(line)
        if tempdescription:
            descriptions.append(" ".join(tempdescription).strip())

    return elements, weights, rarities, descriptions, weightsum, chosentype

# ------------------ GACHA FUNCTIONS ------------------
def randomizer(min_val, max_val, avg, exponent):
    min_val = float(min_val)
    max_val = float(max_val)
    avg = float(avg)
    randarr = []
    weights = []

    x = min_val
    while x < max_val:
        randarr.append(round(x, 2))
        weights.append(1 / (pow(float(exponent), abs(avg - x))))
        x += 0.1

    if not randarr or not weights:
        return avg

    rarity = random.choices(randarr, weights)[0] + 0.1
    return float(rarity)

def run_gacha(mode, min_val, avg, max_val, max_tries=10):
    elements, base_weights, rarities, descriptions, weightsum, chosentype = read_file_with_weight(mode, avg, min_val, max_val)

    for attempt in range(1, max_tries + 1):
        raritypull = randomizer(min_val, max_val, avg, 4)
        filtered = [(e, w, r, d) for e, w, r, d in zip(elements, base_weights, rarities, descriptions)
                    if abs(r - raritypull) <= 0.2]

        if filtered:
            penalty = max(1.0 - ((attempt - 1) * 0.05), 0.7)
            adjusted_weights = [w * penalty for _, w, _, _ in filtered]
            selected = random.choices(filtered, weights=adjusted_weights)[0]
            element, weight, rarity, desc = selected
            luckpercentage = 100 * weight / weightsum

            return {
                "element": element,
                "rarity": rarity,
                "description": desc.replace("#", "").strip(),
                "luck": round(luckpercentage * penalty, 2),
                "type": chosentype
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
    **🧪 Rarity** is a value between `0.1` and `10.0` that represents how special or powerful an element is. The higher the number, the rarer it is.

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

if st.button("🎰 Roll", type="primary"):
    result = run_gacha(mode, min_val, avg, max_val)

    if result:
        tier, color = get_tier_and_color(result["rarity"])
        st.markdown(f"<h3 style='color:{color}' title='{result['description']}'>🎉 {result['element']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:{color}'><strong>Rarity</strong>: `{result['rarity']:.2f}` ({tier})</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:{color}'><strong>Type</strong>: `{result['type']}`</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:{color}'><strong>Estimated Luck</strong>: `{result['luck']:.2f}%`</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"<div style='background-color:#111;padding:10px;border-radius:10px;'>"
                    f"<p style='color:white;font-size:16px;line-height:1.5;text-align:justify;'>{result['description']}</p>"
                    f"</div>", unsafe_allow_html=True)

        st.session_state["log"].append({
            "Type": result["type"],
            "Element": result["element"],
            "Rarity": f"{result['rarity']:.2f}",
            "Tier": tier,
            "Luck": f"{result['luck']:.2f}%",
            "Description": result["description"],
            "Color": color
        })
    else:
        st.warning("No valid result found. Try adjusting the rarity range.")

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

    # Exportar CSV con BOM para compatibilidad móvil (S23 y otros)
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

    import os
from datetime import datetime
import streamlit as st

# Carpetas que usarás:
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

# Listar versiones guardadas
version_files = sorted(
    [f for f in os.listdir("gachafiles_versions") if f.startswith(selected_gachafile) and f.endswith(".txt")],
    reverse=True,
)

for vf in version_files:
    col1, col2 = st.columns([2,1])
    with col1:
        if st.button(f"Restore {vf}", key=f"restore_{vf}"):
            with open(os.path.join("gachafiles_versions", vf), "r", encoding="utf-8") as f:
                version_content = f.read()
            st.session_state[edit_key] = version_content
            st.session_state["edited_files"][selected_gachafile] = version_content
            st.success(f"✅ Restored version: {vf}")
            # No experimental_rerun, el cambio se refleja al actualizar textarea
    with col2:
        with open(os.path.join("gachafiles_versions", vf), "rb") as f:
            st.download_button(
                label="Download",
                data=f,
                file_name=vf,
                mime="text/plain",
                key=f"download_{vf}"
            )

# Guardar automáticamente todos los archivos editados al iniciar
for fname in gachafile_options:
    content_to_save = st.session_state["edited_files"].get(fname)
    if content_to_save:
        file_path = os.path.join("gachafiles", f"{fname}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_to_save)

        # Guardar versión automática con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_path = os.path.join("gachafiles_versions", f"{fname}_{timestamp}.txt")
        with open(version_path, "w", encoding="utf-8") as f:
            f.write(content_to_save)
